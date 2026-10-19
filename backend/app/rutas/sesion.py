"""Rutas de sesión.

GET    /api/sesion/csrf   Token CSRF para las solicitudes que modifican datos (RNF02 CA3)
POST   /api/sesion        Iniciar sesión (RF03)
GET    /api/sesion        Usuario de la sesión actual
DELETE /api/sesion        Cerrar sesión (RF04)
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf

from app.esquemas import validar
from app.esquemas.cuentas import SolicitudInicioSesion, usuario_a_dict
from app.seguridad.autenticacion import cerrar_sesion, iniciar_sesion
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_sesion

sesion_bp = Blueprint("sesion", __name__, url_prefix="/api/sesion")


@sesion_bp.get("/csrf")
def obtener_csrf():
    """Entrega el token CSRF que el frontend envía en la cabecera X-CSRFToken."""
    return jsonify({"csrf": generate_csrf()})


@sesion_bp.post("")
def iniciar():
    """Valida las credenciales y abre la sesión (RF03)."""
    solicitud = validar(SolicitudInicioSesion, request.get_json(silent=True))
    servicio = crear_servicio_sesion(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )
    usuario = servicio.autenticar(solicitud.correo, solicitud.contrasenia)
    iniciar_sesion(usuario)
    return jsonify({"usuario": usuario_a_dict(usuario), "csrf": generate_csrf()})


@sesion_bp.get("")
@login_required
def obtener():
    """Devuelve el usuario de la sesión actual, o 401 si no hay sesión (CA22)."""
    return jsonify({"usuario": usuario_a_dict(current_user)})


@sesion_bp.delete("")
@login_required
def cerrar():
    """Cierra la sesión actual y la elimina del servidor (RF04, CA11)."""
    cerrar_sesion()
    return jsonify({"mensaje": "Cerraste la sesión."})
