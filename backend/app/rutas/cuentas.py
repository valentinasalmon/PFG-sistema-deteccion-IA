"""Rutas de registro, verificación de correo y recuperación de contraseña.

POST /api/cuentas/registro                    Crear cuenta (RF01)
POST /api/cuentas/verificacion                Verificar correo (RF02)
POST /api/cuentas/verificacion/reenvio        Reenviar verificación (RF02 CA2)
POST /api/cuentas/recuperacion                Pedir enlace de recuperación (RF05)
POST /api/cuentas/recuperacion/restablecer    Definir contraseña nueva (RF05)
"""
from flask import Blueprint, current_app, jsonify, request

from app.esquemas import validar
from app.esquemas.cuentas import (
    SolicitudCorreo,
    SolicitudRegistro,
    SolicitudRestablecimiento,
    SolicitudToken,
)
from app.servicios.fabrica import crear_servicio_cuentas

cuentas_bp = Blueprint("cuentas", __name__, url_prefix="/api/cuentas")

MENSAJE_REGISTRO = "Te enviamos un correo para verificar tu cuenta. Revisá tu bandeja de entrada."
MENSAJE_GENERICO_CORREO = (
    "Si el correo corresponde a una cuenta, te enviamos un mensaje con los pasos a seguir."
)


def _servicio():
    return crear_servicio_cuentas(current_app.config, current_app.extensions["enviador_correo"])


@cuentas_bp.post("/registro")
def registrar():
    """Registra una cuenta. La respuesta es igual si el correo ya existía (RF01 CA3)."""
    _servicio().registrar(validar(SolicitudRegistro, request.get_json(silent=True)))
    return jsonify({"mensaje": MENSAJE_REGISTRO}), 201


@cuentas_bp.post("/verificacion")
def verificar():
    """Activa la cuenta con el token del enlace de verificación (RF02)."""
    solicitud = validar(SolicitudToken, request.get_json(silent=True))
    _servicio().verificar_correo(solicitud.token)
    return jsonify({"mensaje": "Tu correo fue verificado. Ya podés iniciar sesión."})


@cuentas_bp.post("/verificacion/reenvio")
def reenviar_verificacion():
    """Reenvía el correo de verificación sin revelar si la cuenta existe."""
    solicitud = validar(SolicitudCorreo, request.get_json(silent=True))
    _servicio().reenviar_verificacion(solicitud.correo)
    return jsonify({"mensaje": MENSAJE_GENERICO_CORREO})


@cuentas_bp.post("/recuperacion")
def solicitar_recuperacion():
    """Envía el enlace de recuperación sin revelar si la cuenta existe (RF05 CA2)."""
    solicitud = validar(SolicitudCorreo, request.get_json(silent=True))
    _servicio().solicitar_recuperacion(solicitud.correo)
    return jsonify({"mensaje": MENSAJE_GENERICO_CORREO})


@cuentas_bp.post("/recuperacion/restablecer")
def restablecer():
    """Define una contraseña nueva y cierra todas las sesiones de la cuenta (RF05 CA3)."""
    solicitud = validar(SolicitudRestablecimiento, request.get_json(silent=True))
    _servicio().restablecer_contrasenia(solicitud.token, solicitud.contrasenia)
    return jsonify({"mensaje": "Tu contraseña fue actualizada. Ya podés iniciar sesión."})
