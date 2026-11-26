"""Actualización automática del catálogo de la SSN, sin red (funcionalidad 052).

Realiza: 052 CA1 a CA4.
"""
# pylint: disable=redefined-outer-name
import io
import json
from types import SimpleNamespace
from unittest import mock
from urllib import error

import pytest

from app.integraciones.fuente_ssn import FuenteSsn, FuenteSsnNoDisponible
from app.repositorios.catalogo_aseguradoras import Aseguradora, CatalogoAseguradoras
from app.servicios.servicio_catalogo_ssn import (
    CatalogoSsnInvalido,
    CatalogoSsnNoDisponible,
    ServicioCatalogoSsn,
    comparar,
    transformar,
)

ENCABEZADO = ("cia_id,cia_denominacion,cia_cuit,cia_sociedad_tipo,cia_actividad_principal,"
              "cia_pais_id,cia_pais\n")


def _csv(filas):
    return (ENCABEZADO + "".join(
        f"{i},{nombre},{cuit},SA,{actividad},ARG,Argentina\n"
        for i, nombre, cuit, actividad in filas
    )).encode()


def _aseguradoras(cantidad, desde=1):
    return [(i, f"ASEGURADORA {i}", f"30{i:09d}", "Seguros Generales")
            for i in range(desde, desde + cantidad)]


def test_transformar_quita_reaseguradoras_y_normaliza():
    """Quita «Reaseg. …», junta espacios y deja las columnas de la plataforma."""
    filas = _aseguradoras(100) + [
        (900, "REASEGURADORA", "30999999999", "Reaseg. Admitida"),
        (901, "FEDERACION  PATRONAL", "33707366589", "Seguros  Gen.-ART"),
    ]
    resultado = transformar(_csv(filas))
    assert len(resultado) == 101
    assert Aseguradora(901, "FEDERACION PATRONAL", "33707366589", "Seguros Gen.-ART") in resultado


@pytest.mark.parametrize("contenido,mensaje", [
    (b"cia_id,cia_denominacion\n1,X\n", "Faltan columnas"),
    (_csv(_aseguradoras(50)), "Solo trae 50"),
    (_csv(_aseguradoras(100) + [(1, "OTRA", "30111111111", "Vida")]), "repetidos"),
    (_csv(_aseguradoras(100) + [(500, "SIN CUIT", "123", "Vida")]), "incompletos"),
    (b"\xff\xfe", "UTF-8"),
])
def test_transformar_rechaza_archivos_rotos(contenido, mensaje):
    """Un archivo con otra forma no se aplica."""
    with pytest.raises(CatalogoSsnInvalido, match=mensaje):
        transformar(contenido)


def test_comparar_detecta_altas_bajas_cambios_y_revocaciones():
    """Las revocaciones que anota la SSN en la denominación se señalan aparte."""
    viejo = [Aseguradora(1, "A", "30000000001", "Vida"), Aseguradora(2, "B", "30000000002", "Vida"),
             Aseguradora(3, "C (Revocación autorización ya conocida)", "30000000003", "Vida")]
    nuevo = [Aseguradora(1, "A (Revocación autorización para operar no firme)", "30000000001",
                         "Vida"),
             Aseguradora(3, "C (Revocación autorización ya conocida)", "30000000003", "Vida"),
             Aseguradora(4, "D", "30000000004", "Vida")]
    diferencias = comparar(viejo, nuevo)
    assert [a.id for a in diferencias["altas"]] == [4]
    assert [a.id for a in diferencias["bajas"]] == [2]
    assert [a.id for a in diferencias["modificadas"]] == [1]
    assert [a.id for a in diferencias["revocaciones"]] == [1]


def test_catalogo_usa_la_copia_actualizada_y_la_relee_si_cambia(tmp_path):
    """Sin copia, el del repositorio; al guardar, la nueva, sin reiniciar."""
    catalogo = CatalogoAseguradoras(carpeta_actualizada=tmp_path / "catalogos")
    original = len(catalogo.todas())
    assert catalogo.metadatos() == {"origen": "repositorio", "total": original}
    nuevas = [Aseguradora(1, "ÚNICA", "30000000001", "Vida")]
    catalogo.guardar(nuevas, {"fuente": "https://x"})
    assert catalogo.todas() == tuple(nuevas)
    assert catalogo.metadatos() == {"fuente": "https://x", "origen": "datos_abiertos", "total": 1}
    with pytest.raises(RuntimeError):
        CatalogoAseguradoras().guardar(nuevas, {})


class _Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_fuente_busca_el_csv_vigente_y_lo_baja():
    """Consulta CKAN, elige el CSV de entidades activas y lo baja por HTTPS."""
    paquete = {"result": {"metadata_modified": "2026-10-31", "resources": [
        {"format": "PDF", "url": "https://x/doc.pdf"},
        {"format": "CSV", "url": "https://ssn/download/entidades-activas.csv",
         "last_modified": "2026-10-26T16:10:13"},
    ]}}
    respuestas = [_Respuesta(json.dumps(paquete).encode()), _Respuesta(b"cia_id\n")]
    with mock.patch("app.integraciones.fuente_ssn.request.urlopen", side_effect=respuestas):
        contenido, recurso = FuenteSsn("https://datos/paquete").descargar()
    assert contenido == b"cia_id\n"
    assert recurso == {"url": "https://ssn/download/entidades-activas.csv",
                       "actualizado": "2026-10-26T16:10:13"}


@pytest.mark.parametrize("efecto", [
    error.URLError("sin red"),
    [_Respuesta(b"no es json")],
    [_Respuesta(json.dumps({"result": {"resources": []}}).encode())],
    [_Respuesta(json.dumps({"result": {"resources": [
        {"format": "CSV", "url": "http://inseguro/entidades-activas.csv"}]}}).encode())],
])
def test_fuente_no_disponible(efecto):
    """Sin red, respuesta rara, sin CSV o sin HTTPS: FuenteSsnNoDisponible."""
    with mock.patch("app.integraciones.fuente_ssn.request.urlopen", side_effect=efecto):
        with pytest.raises(FuenteSsnNoDisponible):
            FuenteSsn("https://datos/paquete").descargar()


def test_fuente_rechaza_archivos_enormes():
    """Más de 2 MB no es el archivo esperado."""
    with mock.patch("app.integraciones.fuente_ssn.request.urlopen",
                    return_value=_Respuesta(b"x" * (2 * 1024 * 1024 + 10))):
        with pytest.raises(FuenteSsnNoDisponible, match="supera"):
            FuenteSsn("https://datos/paquete").descargar()


@pytest.fixture
def servicio(tmp_path):
    """Servicio con un catálogo de 130 aseguradoras y dobles para lo demás."""
    catalogo = CatalogoAseguradoras(carpeta_actualizada=tmp_path)
    catalogo.guardar([Aseguradora(*fila) for fila in _aseguradoras(130)], {})
    fuente = mock.Mock()
    registro = mock.Mock()
    organizacion = SimpleNamespace(id=7, nombre="ASEGURADORA 3", cuit=f"30{3:09d}")
    organizaciones = mock.Mock()
    organizaciones.obtener_por_cuit.side_effect = (
        lambda cuit: organizacion if cuit == organizacion.cuit else None
    )
    usuarios = mock.Mock()
    usuarios.administradores.return_value = [SimpleNamespace(correo="admin@x", nombre="Admin")]
    correos = mock.Mock()
    return SimpleNamespace(
        servicio=ServicioCatalogoSsn(fuente, catalogo, registro, organizaciones=organizaciones,
                                     usuarios=usuarios, correos=correos),
        fuente=fuente, registro=registro, correos=correos, catalogo=catalogo,
    )


def test_sin_cambios_no_toca_nada(servicio):
    """Si el archivo es igual, no guarda, no audita ni avisa."""
    servicio.fuente.descargar.return_value = (_csv(_aseguradoras(130)), {"url": "u",
                                                                         "actualizado": "f"})
    resultado = servicio.servicio.actualizar()
    assert resultado["cambio"] is False and resultado["total"] == 130
    servicio.registro.registrar.assert_not_called()
    servicio.correos.enviar_aviso_catalogo_ssn.assert_not_called()


def test_con_cambios_guarda_audita_y_avisa_las_registradas(servicio):
    """Una baja de una aseguradora registrada llega al Administrador."""
    filas = [f for f in _aseguradoras(130) if f[0] != 3] + _aseguradoras(1, desde=500)
    servicio.fuente.descargar.return_value = (_csv(filas), {"url": "u", "actualizado": "f"})
    resultado = servicio.servicio.actualizar()
    assert resultado["cambio"] and [o.id for o in resultado["afectadas"]] == [7]
    assert len(servicio.catalogo.todas()) == 130
    assert servicio.catalogo.metadatos()["actualizado_en_la_fuente"] == "f"
    detalle = servicio.registro.registrar.call_args.kwargs["detalle"]
    assert detalle["bajas"] == [3] and detalle["altas"] == [500]
    assert detalle["organizaciones_afectadas"] == [7]
    argumentos = servicio.correos.enviar_aviso_catalogo_ssn.call_args.args
    assert [o.id for o in argumentos[2]] == [7] and argumentos[3] == 130


def test_no_aplica_una_lista_mucho_mas_corta_sin_forzar(servicio):
    """Menos del 80 %: se sospecha de un archivo roto."""
    servicio.fuente.descargar.return_value = (_csv(_aseguradoras(100)), {"url": "u",
                                                                         "actualizado": "f"})
    with pytest.raises(CatalogoSsnInvalido, match="forzar"):
        servicio.servicio.actualizar()
    assert servicio.servicio.actualizar(forzar=True)["total"] == 100


def test_portal_caido(servicio):
    """Si el portal no responde, se informa sin tocar el catálogo."""
    servicio.fuente.descargar.side_effect = FuenteSsnNoDisponible("caído")
    with pytest.raises(CatalogoSsnNoDisponible):
        servicio.servicio.actualizar()
