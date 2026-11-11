"""Los correos de casos dicen «siniestro» a las aseguradoras y «caso» a los abogados (039).

Realiza: RNF10 (textos según el perfil de quien recibe).
"""
from datetime import date
from types import SimpleNamespace

import pytest

from app.integraciones.correo import EnviadorMemoria
from app.servicios.servicio_correos import ServicioCorreos

CASO = SimpleNamespace(id=7, numero="CASO-2026-000007")


def _servicio():
    enviador = EnviadorMemoria()
    return ServicioCorreos(enviador, "https://evidentia.prueba"), enviador


def _usuario(perfil):
    return SimpleNamespace(
        nombre="Rita", apellido="López", correo="rita@ejemplo.com", perfil=perfil
    )


@pytest.mark.parametrize("perfil, palabra, otra", [
    ("aseguradora", "siniestro", "caso"),
    ("abogado", "caso", "siniestro"),
])
def test_cada_correo_de_casos_usa_la_palabra_del_perfil(perfil, palabra, otra):
    servicio, enviador = _servicio()
    usuario = _usuario(perfil)
    otro = _usuario("abogado")
    servicio.enviar_aviso_analisis_finalizado(usuario, CASO, 2)
    servicio.enviar_aviso_analisis_fallido(usuario, CASO, "sin espacio")
    servicio.enviar_aviso_acceso_caso(usuario, CASO, "otorgado", "lectura")
    servicio.enviar_aviso_transferencia_caso(usuario, CASO, True, otro)
    servicio.enviar_solicitud_transferencia_caso(usuario, CASO, otro)
    servicio.enviar_respuesta_transferencia_caso(usuario, CASO, otro, True)
    servicio.enviar_aviso_caso_eliminado(usuario, CASO.numero, otro)
    servicio.enviar_aviso_retencion(usuario, CASO, date(2031, 1, 1))

    assert len(enviador.enviados) == 8
    for correo in enviador.enviados:
        assert palabra in correo.asunto, correo.asunto
        # El número del caso (CASO-…) no cuenta: se busca la palabra suelta, en minúscula.
        texto = correo.texto.replace(CASO.numero, "")
        assert f" {otra} " not in texto and f" {otra}." not in texto, correo.asunto
        assert palabra in texto


def test_el_boton_del_correo_tambien_cambia():
    servicio, enviador = _servicio()
    servicio.enviar_aviso_analisis_fallido(_usuario("aseguradora"), CASO, "sin espacio")
    assert "Ir al siniestro" in enviador.enviados[0].html
