"""Pruebas del sello de tiempo pedido desde el navegador (funcionalidad 016, RF37).

BFA solo acepta conexiones desde Argentina: en el modo ``navegador`` el
servidor no llama a BFA, valida los recibos que le pasa el navegador.
"""
import base64
import io

import pytest
from PIL import Image

from pruebas.conftest import entradas_auditoria

CASO = {"espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
        "lugar": "Av. Corrientes 1234"}
TEMPORAL = base64.b64encode(b"0x-36d5997c8c63-0x42bd1533e6d9").decode()


def _definitivo(huella, bloque="50435901"):
    return base64.b64encode(f"1x-{huella}-36d5997c8c63-0x42bd1533e6d9-{bloque}".encode()).decode()


@pytest.fixture
def ana(cuenta):
    """Responsable del caso."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def imagen(aplicacion, ana):
    """Caso con una imagen cargada en modo navegador: queda pendiente."""
    aplicacion.config["SELLO_TIEMPO"] = "navegador"
    caso = ana.post("/api/casos", json=CASO).get_json()["caso"]
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), (10, 20, 30)).save(salida, "PNG")
    datos = ana.post(
        f"/api/casos/{caso['id']}/imagenes",
        data={"archivo": (io.BytesIO(salida.getvalue()), "frente.png")},
        content_type="multipart/form-data",
    ).get_json()["imagen"]
    return {**datos, "id_caso": caso["id"]}


def _ruta(imagen):
    return f"/api/casos/{imagen['id_caso']}/imagenes/{imagen['id']}/sello"


def test_modo_navegador_deja_la_imagen_pendiente(aplicacion, ana, imagen):
    """El servidor no intenta sellar y le indica a la pantalla que lo haga el navegador."""
    assert imagen["sello"]["estado"] == "pendiente"
    listado = ana.get(f"/api/casos/{imagen['id_caso']}/imagenes").get_json()
    assert listado["sello_en_navegador"] is True
    resultado = aplicacion.test_cli_runner().invoke(args=["sellos", "procesar"])
    assert "0 sellado(s), 0 en curso" in resultado.output


def test_recibo_temporal_y_definitivo(aplicacion, ana, imagen):
    """El temporal pasa a enviado; el definitivo de esta huella la deja sellada."""
    enviada = ana.post(_ruta(imagen), json={"recibo": TEMPORAL}).get_json()["imagen"]
    assert enviada["sello"]["estado"] == "enviado"
    assert enviada["sello"]["recibo"] == TEMPORAL

    sellada = ana.post(_ruta(imagen), json={
        "recibo_definitivo": _definitivo(imagen["huella"]), "fecha": "21/10/2026 18:05:27",
    }).get_json()["imagen"]
    assert sellada["sello"]["estado"] == "sellado"
    assert sellada["sello"]["referencia"] == "BFA bloque 50435901"
    assert sellada["sello"]["fecha"] == "2026-10-21T21:05:27"
    assert sellada["sello"]["simulado"] is False
    entradas = entradas_auditoria(aplicacion, "imagen.sello")
    assert entradas and entradas[-1]["detalle"]["origen"] == "navegador"


def test_recibos_invalidos(ana, imagen):
    """Un recibo de otra imagen o que no es de BFA se rechaza."""
    otra = _definitivo("b" * 64)
    assert ana.post(_ruta(imagen), json={"recibo_definitivo": otra}).status_code == 400
    assert ana.post(_ruta(imagen), json={"recibo": "no-es-base64"}).status_code == 400
    assert ana.post(_ruta(imagen), json={}).status_code == 400


def test_sin_modo_navegador_o_sin_acceso(aplicacion, ana, cuenta, imagen):
    """Si el sello lo gestiona el servidor, la ruta no aplica; sin acceso al caso, 404."""
    beto = cuenta("beto@ejemplo.com")
    assert beto.post(_ruta(imagen), json={"recibo": TEMPORAL}).status_code == 404
    aplicacion.config["SELLO_TIEMPO"] = "simulado"
    assert ana.post(_ruta(imagen), json={"recibo": TEMPORAL}).status_code == 409
    aplicacion.config["SELLO_TIEMPO"] = "desactivado"
    assert ana.post(_ruta(imagen), json={"recibo": TEMPORAL}).status_code == 409
