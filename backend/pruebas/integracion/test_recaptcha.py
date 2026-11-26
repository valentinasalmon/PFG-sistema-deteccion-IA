"""reCAPTCHA en los formularios públicos (funcionalidad 051, CA1 y CA4).

Realiza: 051 CA1, CA4.
"""
# pylint: disable=redefined-outer-name,unused-argument
from unittest import mock

import pytest

from app.integraciones.recaptcha import Evaluacion
from pruebas.conftest import datos_registro


@pytest.fixture
def con_recaptcha(aplicacion):
    """Activa reCAPTCHA con una evaluación que la prueba decide."""
    aplicacion.config.update(
        RECAPTCHA_PROYECTO="p", RECAPTCHA_CLAVE_SITIO="clave-sitio", RECAPTCHA_CLAVE_API="a",
    )
    with mock.patch("app.integraciones.recaptcha.VerificadorRecaptcha.evaluar") as evaluar:
        yield evaluar
    aplicacion.config.update(
        RECAPTCHA_PROYECTO="", RECAPTCHA_CLAVE_SITIO="", RECAPTCHA_CLAVE_API="",
    )


def test_sin_configurar_no_pide_nada(cliente):
    """Desactivado: la configuración pública lo dice y los formularios andan igual."""
    assert cliente.get("/api/recaptcha/configuracion").get_json() == {
        "habilitado": False, "clave_sitio": None,
    }
    assert cliente.get("/api/salud").get_json()["recaptcha"] == {"activo": False}
    assert cliente.post("/api/cuentas/registro", json=datos_registro()).status_code == 201


def test_registro_e_inicio_de_sesion_exigen_el_token(cliente, con_recaptcha):
    """Sin token o con puntaje bajo, 400; con un token bueno, sigue."""
    assert cliente.get("/api/recaptcha/configuracion").get_json() == {
        "habilitado": True, "clave_sitio": "clave-sitio",
    }
    sin_token = cliente.post("/api/cuentas/registro", json=datos_registro())
    assert sin_token.status_code == 400
    assert sin_token.get_json()["codigo"] == "verificacion_humana"
    con_recaptcha.assert_not_called()

    con_recaptcha.return_value = Evaluacion(valida=True, puntaje=0.1, accion="registro")
    robot = cliente.post("/api/cuentas/registro", json=datos_registro(),
                         headers={"X-Recaptcha": "tok"})
    assert robot.status_code == 400

    con_recaptcha.return_value = Evaluacion(valida=True, puntaje=0.9, accion="registro")
    persona = cliente.post("/api/cuentas/registro", json=datos_registro(),
                           headers={"X-Recaptcha": "tok"})
    assert persona.status_code == 201
    assert con_recaptcha.call_args.args[:2] == ("tok", "registro")

    con_recaptcha.return_value = Evaluacion(valida=True, puntaje=0.9, accion="registro")
    otra_accion = cliente.post("/api/sesion", json={"correo": "a@b.com", "contrasenia": "x"},
                               headers={"X-Recaptcha": "tok"})
    assert otra_accion.get_json()["codigo"] == "verificacion_humana"


@pytest.mark.parametrize("ruta,accion", [
    ("/api/cuentas/recuperacion", "recuperacion"),
    ("/api/cuentas/verificacion/reenvio", "reenvio_verificacion"),
])
def test_recuperacion_y_reenvio(cliente, con_recaptcha, ruta, accion):
    """Los pedidos que mandan correos también lo exigen."""
    assert cliente.post(ruta, json={"correo": "a@b.com"}).status_code == 400
    con_recaptcha.return_value = Evaluacion(valida=True, puntaje=0.9, accion=accion)
    assert cliente.post(ruta, json={"correo": "a@b.com"},
                        headers={"X-Recaptcha": "tok"}).status_code == 200
