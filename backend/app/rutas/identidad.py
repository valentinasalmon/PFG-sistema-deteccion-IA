"""Rutas públicas de la verificación de identidad (funcionalidad 035).

GET  /api/identidad/<token>              Aseguradora y estado de la verificación (pública)
POST /api/identidad/<token>/simulacion   Simular el resultado (solo con el proveedor simulado)

No usan sesión: el token del enlace es la credencial, como en el pago (032).
Por eso no llevan protección CSRF. Cuando se conecte Identik, su aviso de
resultado (*webhook*, firmado) se suma acá.

Realiza: RN41; CA3 y CA6 de la funcionalidad 035.
"""
from flask import Blueprint, current_app, jsonify, request

from app.esquemas import validar
from app.esquemas.identidad import SolicitudSimulacionIdentidad
from app.extensiones import proteccion_csrf
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_identidad

identidad_bp = Blueprint("identidad", __name__, url_prefix="/api/identidad")
proteccion_csrf.exempt(identidad_bp)


def _servicio():
    return crear_servicio_identidad(current_app.config, origen_de_la_solicitud())


@identidad_bp.get("/<token>")
def consultar(token):
    """Aseguradora, estado y si la verificación es simulada."""
    return jsonify({"verificacion": _servicio().consultar(token)})


@identidad_bp.post("/<token>/simulacion")
def simular(token):
    """Resultado simulado (aprobada o rechazada) de la verificación."""
    solicitud = validar(SolicitudSimulacionIdentidad, request.get_json(silent=True))
    verificacion = _servicio().simular(token, solicitud.resultado)
    return jsonify(
        {"verificacion": verificacion, "mensaje": "Se registró el resultado (simulado)."}
    )
