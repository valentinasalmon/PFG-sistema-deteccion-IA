"""Pruebas de reCAPTCHA sin red (funcionalidad 051).

Realiza: 051 CA2, CA3.
"""
import io
import json
from unittest import mock
from urllib import error

import pytest

from app.integraciones.recaptcha import (
    Evaluacion,
    RecaptchaNoDisponible,
    VerificadorRecaptcha,
    VerificadorRecaptchaDesactivado,
    crear_verificador_recaptcha,
)
from app.servicios.errores import VerificacionHumanaFallida
from app.servicios.servicio_recaptcha import ServicioRecaptcha


class _Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _verificador():
    return VerificadorRecaptcha("mi-proyecto", "clave-sitio", "clave-api")


def test_arma_la_evaluacion_como_dice_google():
    """URL v1 con la clave de API y el evento con el token, la acción y la clave del sitio."""
    respuesta = {
        "tokenProperties": {"valid": True, "action": "registro"},
        "riskAnalysis": {"score": 0.9, "reasons": []},
    }
    with mock.patch("app.integraciones.recaptcha.request.urlopen",
                    return_value=_Respuesta(json.dumps(respuesta).encode())) as abrir:
        evaluacion = _verificador().evaluar("tok", "registro", "1.2.3.4", "Safari")
    pedido = abrir.call_args.args[0]
    assert pedido.full_url == (
        "https://recaptchaenterprise.googleapis.com/v1/projects/mi-proyecto/assessments"
        "?key=clave-api"
    )
    assert json.loads(pedido.data) == {"event": {
        "token": "tok", "siteKey": "clave-sitio", "expectedAction": "registro",
        "userIpAddress": "1.2.3.4", "userAgent": "Safari",
    }}
    assert evaluacion == Evaluacion(valida=True, puntaje=0.9, accion="registro")


def test_token_invalido_y_google_caido():
    """Un token inválido da una evaluación no válida; sin respuesta, RecaptchaNoDisponible."""
    respuesta = {"tokenProperties": {"valid": False, "invalidReason": "EXPIRED"}}
    with mock.patch("app.integraciones.recaptcha.request.urlopen",
                    return_value=_Respuesta(json.dumps(respuesta).encode())):
        evaluacion = _verificador().evaluar("tok", "registro")
    assert not evaluacion.valida and evaluacion.motivo == "EXPIRED"
    with mock.patch("app.integraciones.recaptcha.request.urlopen",
                    side_effect=error.URLError("sin red")):
        with pytest.raises(RecaptchaNoDisponible):
            _verificador().evaluar("tok", "registro")


def test_sin_configuracion_completa_queda_desactivado():
    """Faltando cualquiera de los tres valores, no se usa Google."""
    assert isinstance(crear_verificador_recaptcha({}), VerificadorRecaptchaDesactivado)
    assert isinstance(crear_verificador_recaptcha(
        {"RECAPTCHA_PROYECTO": "p", "RECAPTCHA_CLAVE_SITIO": "s"}
    ), VerificadorRecaptchaDesactivado)
    assert isinstance(crear_verificador_recaptcha({
        "RECAPTCHA_PROYECTO": "p", "RECAPTCHA_CLAVE_SITIO": "s", "RECAPTCHA_CLAVE_API": "a",
    }), VerificadorRecaptcha)


class _Falso:
    activo = True
    clave_sitio = "clave-sitio"

    def __init__(self, evaluacion=None, falla=None):
        self.evaluacion = evaluacion
        self.falla = falla

    def evaluar(self, *_args):
        if self.falla:
            raise self.falla
        return self.evaluacion


@pytest.mark.parametrize("evaluacion", [
    Evaluacion(valida=False, puntaje=0.9, accion="registro"),
    Evaluacion(valida=True, puntaje=0.9, accion="inicio_sesion"),
    Evaluacion(valida=True, puntaje=0.2, accion="registro"),
])
def test_rechaza_invalido_otra_accion_o_puntaje_bajo(evaluacion):
    """Token inválido, de otra acción o con puntaje bajo: se rechaza."""
    with pytest.raises(VerificacionHumanaFallida):
        ServicioRecaptcha(_Falso(evaluacion)).exigir("tok", "registro")


def test_acepta_y_sin_token_rechaza():
    """Puntaje suficiente pasa; sin token no."""
    servicio = ServicioRecaptcha(_Falso(Evaluacion(valida=True, puntaje=0.7, accion="registro")))
    servicio.exigir("tok", "registro")
    with pytest.raises(VerificacionHumanaFallida):
        servicio.exigir("", "registro")


def test_si_google_no_responde_deja_pasar():
    """Una caída de Google no impide registrarse ni entrar."""
    ServicioRecaptcha(_Falso(falla=RecaptchaNoDisponible("caído"))).exigir("tok", "registro")


def test_desactivado_y_configuracion_publica():
    """Desactivado no pide nada y no muestra clave; activo muestra la clave del sitio."""
    apagado = ServicioRecaptcha(VerificadorRecaptchaDesactivado())
    apagado.exigir("", "registro")
    assert apagado.configuracion_publica() == {"habilitado": False, "clave_sitio": None}
    prendido = ServicioRecaptcha(_Falso())
    assert prendido.configuracion_publica() == {"habilitado": True, "clave_sitio": "clave-sitio"}
    with pytest.raises(ValueError):
        prendido.exigir("tok", "otra")
