"""Pruebas de la retención de los casos: prórroga, aviso y destrucción (funcionalidad 015).

La tarea diaria se ejecuta con el comando ``flask retencion procesar``; las
fechas se simulan corriendo el inicio del plazo de retención.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import io
from datetime import timedelta

import pytest
from PIL import Image

from app.extensiones import db
from app.modelos.caso import Caso
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import entradas_auditoria

CASO = {"espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
        "lugar": "Av. Corrientes 1234"}
CINCO_ANIOS = timedelta(days=5 * 365 + 1)


@pytest.fixture
def ana(cuenta):
    """Responsable de los casos."""
    return cuenta("ana@ejemplo.com")


def _caso_cerrado(cliente, con_imagen=False):
    caso = cliente.post("/api/casos", json=CASO).get_json()["caso"]
    if con_imagen:
        salida = io.BytesIO()
        Image.new("RGB", (64, 48), (10, 20, 30)).save(salida, "PNG")
        cliente.post(
            f"/api/casos/{caso['id']}/imagenes",
            data={"archivo": (io.BytesIO(salida.getvalue()), "frente.png")},
            content_type="multipart/form-data",
        )
    cliente.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "cerrar"})
    return caso


def _mover_inicio(aplicacion, id_caso, hace):
    with aplicacion.app_context():
        db.session.get(Caso, id_caso).retencion_desde = ahora_utc() - hace
        db.session.commit()


def _vence_en(aplicacion, id_caso, dias):
    """Ubica el inicio del plazo para que la retención venza dentro de ``dias``."""
    vence = ahora_utc() + timedelta(days=dias, hours=1)
    with aplicacion.app_context():
        db.session.get(Caso, id_caso).retencion_desde = vence.replace(year=vence.year - 5)
        db.session.commit()


def _procesar(aplicacion):
    resultado = aplicacion.test_cli_runner().invoke(args=["retencion", "procesar"])
    assert resultado.exit_code == 0, resultado.output
    return resultado.output


def test_prorroga_con_motivo(aplicacion, ana):
    """RF51 CA1: la destrucción se extiende 1 año y el motivo queda en la auditoría."""
    caso = _caso_cerrado(ana)
    vence_antes = ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]["retencion_vence"]

    respuesta = ana.post(f"/api/casos/{caso['id']}/prorroga", json={"motivo": "Juicio en trámite"})

    assert respuesta.status_code == 200
    vence_despues = respuesta.get_json()["caso"]["retencion_vence"]
    assert int(vence_despues[:4]) == int(vence_antes[:4]) + 1
    assert "se conserva hasta el" in respuesta.get_json()["mensaje"]
    entrada = entradas_auditoria(aplicacion, "caso.prorroga_retencion")[-1]
    assert entrada["detalle"]["motivo"] == "Juicio en trámite"


def test_prorroga_sin_motivo_o_de_un_borrador(ana):
    """RF51 CA2: sin motivo se rechaza; un borrador no tiene plazo que prorrogar."""
    caso = _caso_cerrado(ana)
    assert ana.post(f"/api/casos/{caso['id']}/prorroga", json={"motivo": "  "}).status_code == 400
    borrador = ana.post("/api/casos", json=CASO).get_json()["caso"]
    respuesta = ana.post(f"/api/casos/{borrador['id']}/prorroga", json={"motivo": "Juicio"})
    assert respuesta.status_code == 409


def test_accion_prorrogar_solo_en_casos_cerrados(ana):
    """La interfaz ofrece prorrogar solo al Responsable de un caso cerrado o archivado."""
    caso = _caso_cerrado(ana)
    assert ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]["acciones"]["prorrogar"] is True
    borrador = ana.post("/api/casos", json=CASO).get_json()["caso"]
    assert borrador["acciones"]["prorrogar"] is False


def test_aviso_a_30_dias(aplicacion, ana, correos):
    """RF50: el día en que faltan 30 días se avisa al Responsable, una sola vez."""
    caso = _caso_cerrado(ana)
    _vence_en(aplicacion, caso["id"], 30)

    salida = _procesar(aplicacion)

    assert "1 aviso(s)" in salida
    aviso = correos[-1]
    assert aviso.destinatario == "ana@ejemplo.com"
    assert f"El caso {caso['numero']} se elimina en 30 días" == aviso.asunto
    assert "1 año" in aviso.texto
    _vence_en(aplicacion, caso["id"], 29)  # al día siguiente ya no se repite
    assert "0 aviso(s)" in _procesar(aplicacion)


def test_destruccion_al_vencer(aplicacion, ana):
    """RF49 CA1 y CA2: se destruye y se audita con el número y las huellas."""
    caso = _caso_cerrado(ana, con_imagen=True)
    _mover_inicio(aplicacion, caso["id"], CINCO_ANIOS + timedelta(days=2))

    salida = _procesar(aplicacion)

    assert "1 caso(s) destruido(s)" in salida
    assert ana.get(f"/api/casos/{caso['id']}").status_code == 404
    entrada = entradas_auditoria(aplicacion, "caso.destruccion_retencion")[-1]
    assert entrada["detalle"]["numero"] == caso["numero"]
    assert len(entrada["detalle"]["sha256_eliminados"]) == 1


def test_un_caso_reabierto_no_se_destruye(aplicacion, ana):
    """RN30: reabrir detiene el plazo; la tarea no lo toca."""
    caso = _caso_cerrado(ana)
    _mover_inicio(aplicacion, caso["id"], CINCO_ANIOS + timedelta(days=2))
    ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "reabrir"})

    assert "0 caso(s) destruido(s)" in _procesar(aplicacion)
    assert ana.get(f"/api/casos/{caso['id']}").status_code == 200


def test_imagen_cargada_queda_sellada_con_el_simulado(aplicacion, ana):
    """016: al cargar, la imagen se sella (en pruebas, con el sellador simulado)."""
    caso = ana.post("/api/casos", json=CASO).get_json()["caso"]
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), (10, 20, 30)).save(salida, "PNG")
    imagen = ana.post(
        f"/api/casos/{caso['id']}/imagenes",
        data={"archivo": (io.BytesIO(salida.getvalue()), "frente.png")},
        content_type="multipart/form-data",
    ).get_json()["imagen"]

    assert imagen["sello"]["estado"] == "sellado" and imagen["sello"]["simulado"] is True
    resultado = aplicacion.test_cli_runner().invoke(args=["sellos", "procesar"])
    assert "0 sellado(s), 0 en curso" in resultado.output
