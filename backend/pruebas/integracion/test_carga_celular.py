"""Pruebas de la carga desde el celular con un enlace de un solo uso (funcionalidad 024).

Las imágenes se generan en memoria: nunca se usan imágenes de casos reales.
"""
# pylint: disable=unused-argument,redefined-outer-name
import io
from datetime import datetime, timedelta

import pytest
from PIL import Image

from app.extensiones import db
from app.modelos.enlace_carga import EnlaceCarga
from app.servicios import servicio_enlaces_carga
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
    assert datos["numero"] == caso["numero"] and datos["restantes"] == 30

    subida = _subir(celular, token, _foto())
    assert subida.status_code == 201, subida.get_json()
    assert "huella" in subida.get_json()["imagen"] and "id" not in subida.get_json()["imagen"]
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert [i["cargada_por"] for i in imagenes] == ["Ana López"]
    carga = entradas_auditoria(aplicacion, "imagen.carga")[-1]
    assert carga["detalle"]["origen"] == "celular"
    assert celular.get(f"/api/carga/{token}").get_json()["restantes"] == 29
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


def test_limite_de_fotos_y_validaciones(aplicacion, ana, caso, monkeypatch):
    """El enlace tiene un tope de fotos y aplica las validaciones de siempre."""
    monkeypatch.setattr(servicio_enlaces_carga, "MAXIMO_CARGAS", 1)
    token = _token(ana.post(f"/api/casos/{caso['id']}/enlace-carga"))
    celular = aplicacion.test_client()
    assert _subir(celular, token, b"no es una imagen", "texto.jpg").status_code == 400
    assert _subir(celular, token, _foto()).status_code == 201
    agotado = _subir(celular, token, _foto((1, 2, 3)))
    assert agotado.status_code == 409 and agotado.get_json()["codigo"] == "enlace_agotado"


def test_solo_quien_puede_cargar_genera_el_enlace(aplicacion, ana, caso, cuenta):
    """Sin permiso de carga sobre el caso no se puede generar ni cancelar el enlace."""
    beto = cuenta("beto@ejemplo.com", "Beto")
    assert beto.post(f"/api/casos/{caso['id']}/enlace-carga").status_code == 404
    assert beto.delete(f"/api/casos/{caso['id']}/enlace-carga").status_code == 404
    assert aplicacion.test_client().post(f"/api/casos/{caso['id']}/enlace-carga").status_code == 401


# --- Enlace para la persona afectada (028, CP-32) ---

def _enlace_afectada(cliente, id_caso, **datos):
    respuesta = cliente.post(f"/api/casos/{id_caso}/enlaces-persona-afectada", json=datos)
    assert respuesta.status_code == 201, respuesta.get_json()
    return respuesta.get_json()["enlace"]


def _subir_afectada(cliente, token, contenido, declaracion=True):
    datos = {"archivo": (io.BytesIO(contenido), "foto.jpg")}
    if declaracion:
        datos["declaracion"] = "true"
    return cliente.post(f"/api/carga/{token}", data=datos, content_type="multipart/form-data")


def test_persona_afectada_sube_sus_fotos_con_declaracion(aplicacion, ana, caso):
    """La persona ve quién le pide las fotos, sin datos del caso, y acepta la declaración."""
    enlace = _enlace_afectada(ana, caso["id"], destinatario="Juan Pérez")
    assert enlace["destinatario"] == "Juan Pérez"
    token = enlace["url"].rsplit("/", 1)[-1]
    persona = aplicacion.test_client()

    datos = persona.get(f"/api/carga/{token}").get_json()
    assert datos["tipo"] == "persona_afectada"
    assert datos["solicitante"] == "Ana López" and datos["organizacion"] is None
    assert "numero" not in datos and not datos["declaracion_aceptada"]
    assert "Declaro" in datos["declaracion"]

    sin_declaracion = _subir_afectada(persona, token, _foto(), declaracion=False)
    assert sin_declaracion.status_code == 400
    assert sin_declaracion.get_json()["codigo"] == "declaracion_requerida"

    assert _subir_afectada(persona, token, _foto()).status_code == 201
    assert _subir_afectada(persona, token, _foto((9, 9, 9))).status_code == 201
    assert persona.get(f"/api/carga/{token}").get_json()["declaracion_aceptada"]

    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert [i["origen"] for i in imagenes] == ["persona_afectada", "persona_afectada"]
    operaciones = [
        e["detalle"]["operacion"] for e in entradas_auditoria(aplicacion, "imagen.enlace_carga")
    ]
    assert operaciones == ["crear", "declaracion"]
    declaracion = entradas_auditoria(aplicacion, "imagen.enlace_carga")[-1]
    assert declaracion["id_usuario"] is None and declaracion["detalle"]["version"]
    listado = ana.get(f"/api/casos/{caso['id']}/enlaces-persona-afectada").get_json()
    assert listado["enlaces"][0]["cargas"] == 2 and listado["enlaces"][0]["declaracion_aceptada"]


def test_enlace_de_persona_afectada_vence_en_7_dias_y_se_anula(aplicacion, ana, caso):
    """Vence a los 7 días por defecto, se puede elegir otra vigencia y anular."""
    enlace = _enlace_afectada(ana, caso["id"])
    creado = datetime.fromisoformat(enlace["creado_en"])
    assert datetime.fromisoformat(enlace["vence_en"]) - creado == timedelta(days=7)
    corto = _enlace_afectada(ana, caso["id"], dias=2)
    assert datetime.fromisoformat(corto["vence_en"]) - datetime.fromisoformat(
        corto["creado_en"]) == timedelta(days=2)
    for dias in (0, 31, "7", True):
        respuesta = ana.post(
            f"/api/casos/{caso['id']}/enlaces-persona-afectada", json={"dias": dias}
        )
        assert respuesta.status_code == 400, dias

    # Generar el QR del celular no anula los enlaces de la persona afectada.
    ana.post(f"/api/casos/{caso['id']}/enlace-carga")
    ana.delete(f"/api/casos/{caso['id']}/enlace-carga")
    vigentes = ana.get(f"/api/casos/{caso['id']}/enlaces-persona-afectada").get_json()["enlaces"]
    assert {e["id"] for e in vigentes} == {enlace["id"], corto["id"]}

    ruta = f"/api/casos/{caso['id']}/enlaces-persona-afectada/{enlace['id']}"
    assert ana.delete(ruta).status_code == 200
    assert ana.delete(ruta).status_code == 404
    token = enlace["url"].rsplit("/", 1)[-1]
    anulado = aplicacion.test_client().get(f"/api/carga/{token}")
    assert anulado.status_code == 404 and "Pedile uno nuevo" in anulado.get_json()["mensaje"]
    vigentes = ana.get(f"/api/casos/{caso['id']}/enlaces-persona-afectada").get_json()["enlaces"]
    assert [e["id"] for e in vigentes] == [corto["id"]]


def test_tope_de_enlaces_y_permisos_de_la_persona_afectada(
    aplicacion, ana, caso, cuenta, monkeypatch
):
    """Hay un tope de enlaces vigentes y solo quien puede cargar los maneja."""
    monkeypatch.setattr(servicio_enlaces_carga, "MAXIMO_ENLACES_VIGENTES", 1)
    _enlace_afectada(ana, caso["id"])
    otro = ana.post(f"/api/casos/{caso['id']}/enlaces-persona-afectada", json={})
    assert otro.status_code == 409 and otro.get_json()["codigo"] == "demasiados_enlaces"

    beto = cuenta("beto@ejemplo.com", "Beto")
    ruta = f"/api/casos/{caso['id']}/enlaces-persona-afectada"
    assert beto.get(ruta).status_code == 404
    assert beto.post(ruta, json={}).status_code == 404
    assert beto.delete(f"{ruta}/1").status_code == 404
    assert aplicacion.test_client().get(ruta).status_code == 401


def test_tope_de_fotos_de_la_persona_afectada(aplicacion, ana, caso, monkeypatch):
    """El tope de fotos le pide a la persona un enlace nuevo a quien se lo mandó."""
    monkeypatch.setattr(servicio_enlaces_carga, "MAXIMO_CARGAS", 1)
    token = _enlace_afectada(ana, caso["id"])["url"].rsplit("/", 1)[-1]
    persona = aplicacion.test_client()
    assert _subir_afectada(persona, token, _foto()).status_code == 201
    agotado = _subir_afectada(persona, token, _foto((1, 2, 3)))
    assert agotado.status_code == 409 and "Pedile uno nuevo" in agotado.get_json()["mensaje"]


def test_la_carga_desde_la_computadora_queda_con_su_origen(ana, caso):
    """Cada imagen dice de dónde vino (028)."""
    respuesta = ana.post(
        f"/api/casos/{caso['id']}/imagenes",
        data={"archivo": (io.BytesIO(_foto()), "frente.jpg")}, content_type="multipart/form-data",
    )
    assert respuesta.status_code == 201, respuesta.get_json()
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert imagenes[0]["origen"] == "computadora"
    detalle = ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]
    assert detalle["cantidad_imagenes"] == 1 and detalle["cantidad_informes"] == 0
