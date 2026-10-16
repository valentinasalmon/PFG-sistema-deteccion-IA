"""Rutas del perfil propio.

GET   /api/perfil                         Ver mis datos
PATCH /api/perfil                         Editar nombre, apellido, colegio o empresa (RF07)
POST  /api/perfil/contrasenia             Cambiar la contraseña (RF06)
POST  /api/perfil/correo                  Pedir cambio de correo (RF07 CA2)
POST  /api/perfil/correo/confirmacion     Confirmar el correo nuevo con el enlace recibido
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.cuentas import (
    SolicitudActualizacionPerfil,
    SolicitudCambioContrasenia,
    SolicitudCambioCorreo,
    SolicitudToken,
    usuario_a_dict,
)
from app.seguridad.autenticacion import renovar_sesion, usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_perfil

perfil_bp = Blueprint("perfil", __name__, url_prefix="/api/perfil")


def _servicio():
    return crear_servicio_perfil(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


@perfil_bp.get("")
@login_required
def obtener():
    """Devuelve los datos del perfil propio."""
    return jsonify({"usuario": usuario_a_dict(usuario_actual())})


@perfil_bp.patch("")
@login_required
def actualizar():
    """Actualiza solo los campos enviados. El perfil no puede cambiarse (RF07 CA4)."""
    solicitud = validar(SolicitudActualizacionPerfil, request.get_json(silent=True))
    cambios = solicitud.model_dump(exclude_unset=True)
    usuario = _servicio().actualizar_datos(usuario_actual(), cambios)
    return jsonify(
        {"usuario": usuario_a_dict(usuario), "mensaje": "Tus datos fueron actualizados."}
    )


@perfil_bp.post("/contrasenia")
@login_required
def cambiar_contrasenia():
    """Cambia la contraseña verificando la actual y cierra las demás sesiones (RF06)."""
    solicitud = validar(SolicitudCambioContrasenia, request.get_json(silent=True))
    usuario = _servicio().cambiar_contrasenia(
        usuario_actual(), solicitud.contrasenia_actual, solicitud.contrasenia_nueva
    )
    # Las demás sesiones quedaron cerradas; la actual se mantiene.
    renovar_sesion(usuario)
    return jsonify({"mensaje": "Tu contraseña fue actualizada."})


@perfil_bp.post("/correo")
@login_required
def solicitar_cambio_correo():
    """Envía la confirmación a la dirección nueva y un aviso a la actual (RF07 CA2)."""
    solicitud = validar(SolicitudCambioCorreo, request.get_json(silent=True))
    _servicio().solicitar_cambio_correo(
        usuario_actual(), solicitud.correo_nuevo, solicitud.contrasenia
    )
    return jsonify({"mensaje": "Te enviamos un enlace al correo nuevo para confirmar el cambio."})


@perfil_bp.post("/correo/confirmacion")
def confirmar_cambio_correo():
    """Aplica el cambio de correo. No requiere sesión: el enlace prueba el acceso al correo."""
    solicitud = validar(SolicitudToken, request.get_json(silent=True))
    _servicio().confirmar_cambio_correo(solicitud.token)
    return jsonify({"mensaje": "Tu correo fue actualizado."})
