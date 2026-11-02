"""Rutas del pago del plan por transferencia (funcionalidad 032).

GET  /api/pagos/<token>              Datos del cobro para la pantalla de pago (pública)
POST /api/pagos/<token>/simulacion   Simular la acreditación de la transferencia (pública)

No usan sesión: el token del enlace es la credencial, porque el pago se hace
al final del registro, antes de verificar el correo. Por eso no llevan
protección CSRF, que solo tiene sentido con cookies de sesión.

Realiza: RF20 (CA2); CP-34.
"""
from flask import Blueprint, current_app, jsonify

from app.extensiones import proteccion_csrf
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_pagos

pagos_bp = Blueprint("pagos", __name__, url_prefix="/api/pagos")
proteccion_csrf.exempt(pagos_bp)


def _servicio():
    return crear_servicio_pagos(current_app.config, origen_de_la_solicitud())


@pagos_bp.get("/<token>")
def consultar(token):
    """Plan, organización, CVU, alias, referencia y estado del cobro."""
    return jsonify({"cobro": _servicio().consultar(token)})


@pagos_bp.post("/<token>/simulacion")
def simular(token):
    """Acredita el cobro como si hubiera llegado la transferencia (pago simulado)."""
    cobro = _servicio().simular_acreditacion(token)
    return jsonify({"cobro": cobro, "mensaje": "Se acreditó el pago (simulado)."})
