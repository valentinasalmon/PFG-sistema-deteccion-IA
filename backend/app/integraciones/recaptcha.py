"""Verificación de reCAPTCHA con Google Cloud (funcionalidad 051).

reCAPTCHA es hoy parte de Google Cloud Fraud Defense. El navegador obtiene un
token con ``grecaptcha.enterprise.execute`` y el backend lo evalúa creando una
evaluación (*assessment*) en la API REST v1:

    POST https://recaptchaenterprise.googleapis.com/v1/projects/{proyecto}/assessments
         ?key={clave_api}
    {"event": {"token", "siteKey", "expectedAction", "userAgent", "userIpAddress"}}

La respuesta trae ``tokenProperties.valid``, ``tokenProperties.action`` y
``riskAnalysis.score`` (de 0, probablemente un robot, a 1, probablemente una
persona). Fuente: «Create assessments for websites», documentación de Google
Cloud consultada el 2026-11-26.

Sin la configuración completa se usa ``VerificadorRecaptchaDesactivado``, que
deja pasar todo: en desarrollo y en las pruebas no hace falta Google.

Realiza: RNF02 (seguridad); 051.
"""
import json
from dataclasses import dataclass
from urllib import error, parse, request

URL_EVALUACIONES = "https://recaptchaenterprise.googleapis.com/v1/projects/{proyecto}/assessments"
TIEMPO_ESPERA = 5  # segundos
UMBRAL_POR_DEFECTO = 0.5  # el que recomienda Google para empezar


class RecaptchaNoDisponible(Exception):
    """Google no respondió o respondió con un error del servicio (no del token)."""


@dataclass(frozen=True)
class Evaluacion:
    """Resultado de evaluar un token."""

    valida: bool
    puntaje: float
    accion: str
    motivo: str = ""


class VerificadorRecaptcha:
    """Evalúa tokens con la API de Google Cloud."""

    activo = True

    def __init__(self, proyecto, clave_sitio, clave_api, tiempo_espera=TIEMPO_ESPERA):
        self.proyecto = proyecto
        self.clave_sitio = clave_sitio
        self.clave_api = clave_api
        self.tiempo_espera = tiempo_espera

    def _pedir(self, cuerpo):
        url = URL_EVALUACIONES.format(proyecto=parse.quote(self.proyecto, safe=""))
        url += "?" + parse.urlencode({"key": self.clave_api})
        solicitud = request.Request(
            url, data=json.dumps(cuerpo).encode(), method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with request.urlopen(solicitud, timeout=self.tiempo_espera) as respuesta:
                return json.loads(respuesta.read() or b"{}")
        except (error.URLError, TimeoutError, ValueError) as falla:
            raise RecaptchaNoDisponible(str(falla)) from falla

    def evaluar(self, token, accion, ip=None, agente=None):
        """Evalúa el token de la acción indicada.

        Raises:
            RecaptchaNoDisponible: si Google no responde.
        """
        evento = {"token": token, "siteKey": self.clave_sitio, "expectedAction": accion}
        if ip:
            evento["userIpAddress"] = ip
        if agente:
            evento["userAgent"] = agente[:500]
        datos = self._pedir({"event": evento})
        propiedades = datos.get("tokenProperties") or {}
        puntaje = float((datos.get("riskAnalysis") or {}).get("score") or 0.0)
        return Evaluacion(
            valida=bool(propiedades.get("valid")),
            puntaje=puntaje,
            accion=propiedades.get("action") or "",
            motivo=propiedades.get("invalidReason") or "",
        )


class VerificadorRecaptchaDesactivado:
    """Sin reCAPTCHA configurado: no se pide ni se evalúa nada."""

    activo = False
    clave_sitio = ""

    def evaluar(self, token, accion, ip=None, agente=None):  # pylint: disable=unused-argument
        """Deja pasar todo."""
        return Evaluacion(valida=True, puntaje=1.0, accion=accion)


def crear_verificador_recaptcha(configuracion):
    """Verificador real si están el proyecto, la clave del sitio y la clave de API."""
    proyecto = configuracion.get("RECAPTCHA_PROYECTO", "")
    clave_sitio = configuracion.get("RECAPTCHA_CLAVE_SITIO", "")
    clave_api = configuracion.get("RECAPTCHA_CLAVE_API", "")
    if proyecto and clave_sitio and clave_api:
        return VerificadorRecaptcha(proyecto, clave_sitio, clave_api)
    return VerificadorRecaptchaDesactivado()
