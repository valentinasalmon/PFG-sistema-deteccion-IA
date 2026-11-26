"""reCAPTCHA de los formularios públicos (funcionalidad 051).

GET /api/recaptcha/configuracion    Si está activo y la clave del sitio (pública)

La clave del sitio llega al navegador desde acá, y no al compilar el frontend:
así se cambia en Parameter Store sin volver a compilar (pedido de la autora:
«que las variables no estén en el frontend»). El navegador manda el token en la
cabecera ``X-Recaptcha``.

Realiza: RNF02; 051.
"""
from flask import Blueprint, current_app, jsonify, request

from app.servicios.fabrica import crear_servicio_recaptcha

recaptcha_bp = Blueprint("recaptcha", __name__, url_prefix="/api/recaptcha")

CABECERA_TOKEN = "X-Recaptcha"


@recaptcha_bp.get("/configuracion")
def configuracion():
    """Si el navegador tiene que pedir un token y con qué clave del sitio."""
    return jsonify(crear_servicio_recaptcha(current_app.config).configuracion_publica())


def exigir_persona(accion):
    """Rechaza la solicitud si reCAPTCHA no confirma que la envió una persona.

    Raises:
        VerificacionHumanaFallida: se responde 400 con el código ``verificacion_humana``.
    """
    crear_servicio_recaptcha(current_app.config).exigir(
        request.headers.get(CABECERA_TOKEN, ""),
        accion,
        ip=request.remote_addr,
        agente=request.headers.get("User-Agent"),
    )
