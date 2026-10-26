"""Pruebas de la carga desde el celular con un enlace de un solo uso (funcionalidad 024).

Las imágenes se generan en memoria: nunca se usan imágenes de casos reales.
"""
# pylint: disable=unused-argument,redefined-outer-name
import io
from datetime import timedelta

import pytest
from PIL import Image

from app.extensiones import db
from app.modelos.enlace_carga import EnlaceCarga
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import entradas_auditoria

CASO = {
    "espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
    "lugar": "Av. Corrientes 1234",
}


def _foto(color=(200, 30, 30)):
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), color).save(salida, format="JPEG")
    return salida.getvalue()


def _token(respuesta):
    return respuesta.get_json()["enlace"]["url"].rsplit("/", 1)[-1]


def _subir(cliente, token, contenido, nombre="IMG_0001.jpg"):
    return cliente.post(
        f"/api/carga/{token}", data={"archivo": (io.BytesIO(contenido), nombre)},
        content_type="multipart/form-data",
    )


@pytest.fixture
def ana(cuenta):
    """Responsable del caso."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def caso(ana):
    """Caso personal de Ana en Borrador."""
    return ana.post("/api/casos", json=CASO).get_json()["caso"]


def test_qr_y_carga_sin_sesion(aplicacion, ana, caso):
    """CA2: el enlace se muestra como QR y el celular carga sin iniciar sesión."""
    respuesta = ana.post(f"/api/casos/{caso['id']}/enlace-carga")
    assert respuesta.status_code == 201
    enlace = respuesta.get_json()["enlace"]
    assert enlace["url"].startswith("http://frontend.prueba/cargar/")
    assert enlace["qr"].startswith("data:image/svg+xml")
    token = _token(respuesta)

    celular = aplicacion.test_client()  # sin sesión
    datos = celular.get(f"/api/carga/{token}").get_json()
    assert datos["numero"] == caso["numero"] and datos["restantes"] == 20  # plan Personal

    subida = _subir(celular, token, _foto())
    assert subida.status_code == 201, subida.get_json()
    assert "huella" in subida.get_json()["imagen"] and "id" not in subida.get_json()["imagen"]
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert [i["cargada_por"] for i in imagenes] == ["Ana López"]
    carga = entradas_auditoria(aplicacion, "imagen.carga")[-1]
    assert carga["detalle"]["origen"] == "celular"
    assert celular.get(f"/api/carga/{token}").get_json()["restantes"] == 19
    with aplicacion.app_context():
        assert token not in {e.huella_token for e in EnlaceCarga.query.all()}


def test_enlace_cancelado_vencido_o_inventado(aplicacion, ana, caso):
    """El enlace deja de servir al cancelarlo, al generar otro o al vencer."""
    primero = _token(ana.post(f"/api/casos/{caso['id']}/enlace-carga"))
    segundo = _token(ana.post(f"/api/casos/{caso['id']}/enlace-carga"))
    celular = aplicacion.test_client()
    assert celular.get(f"/api/carga/{primero}").status_code == 404
    assert celular.get("/api/carga/inventado").status_code == 404

    with aplicacion.app_context():
        enlace = EnlaceCarga.query.filter_by(revocado_en=None).one()
        enlace.vence_en = ahora_utc() - timedelta(seconds=1)
        db.session.commit()
    assert _subir(celular, segundo, _foto()).status_code == 404

    tercero = _token(ana.post(f"/api/casos/{caso['id']}/enlace-carga"))
    assert ana.delete(f"/api/casos/{caso['id']}/enlace-carga").status_code == 200
    respuesta = celular.get(f"/api/carga/{tercero}")
    assert respuesta.status_code == 404 and "Pedí uno nuevo" in respuesta.get_json()["mensaje"]
    entradas = entradas_auditoria(aplicacion, "imagen.enlace_carga")
    operaciones = [e["detalle"]["operacion"] for e in entradas]
    assert operaciones == ["crear", "crear", "crear", "cancelar"]


def test_sin_tope_por_enlace_solo_el_limite_del_plan(aplicacion, ana, caso):
    """El enlace no limita la cantidad de fotos; rige el límite del plan (RN15)."""
    plan = aplicacion.config["PLAN_PERSONAL"]
    aplicacion.config["PLAN_PERSONAL"] = {**plan, "imagenes_por_caso": 3}
    token = _token(ana.post(f"/api/casos/{caso['id']}/enlace-carga"))
    celular = aplicacion.test_client()
    assert _subir(celular, token, b"no es una imagen", "texto.jpg").status_code == 400
    for color in ((1, 1, 1), (2, 2, 2), (3, 3, 3)):
        assert _subir(celular, token, _foto(color)).status_code == 201
    assert celular.get(f"/api/carga/{token}").get_json()["restantes"] == 0
    assert _subir(celular, token, _foto((4, 4, 4))).status_code == 409


def test_solo_quien_puede_cargar_genera_el_enlace(aplicacion, ana, caso, cuenta):
    """Sin permiso de carga sobre el caso no se puede generar ni cancelar el enlace."""
    beto = cuenta("beto@ejemplo.com", "Beto")
    assert beto.post(f"/api/casos/{caso['id']}/enlace-carga").status_code == 404
    assert beto.delete(f"/api/casos/{caso['id']}/enlace-carga").status_code == 404
    assert aplicacion.test_client().post(f"/api/casos/{caso['id']}/enlace-carga").status_code == 401
