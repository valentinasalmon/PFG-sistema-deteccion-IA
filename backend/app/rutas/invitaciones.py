"""Rutas de la persona invitada a una organización.

GET  /api/invitaciones                         Mis invitaciones pendientes (CU11 3a)
POST /api/invitaciones/consulta                Ver la invitación del enlace, sin sesión
POST /api/invitaciones/<id>/aceptacion         Aceptar (RF13)
POST /api/invitaciones/<id>/rechazo            Rechazar (CU11 4a)
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.esquemas import validar
from app.esquemas.cuentas import SolicitudToken
from app.esquemas.organizaciones import invitacion_a_dict
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_organizaciones
from app.utilidades.tiempo import ahora_utc

invitaciones_bp = Blueprint("invitaciones", __name__, url_prefix="/api/invitaciones")


def _servicio():
    return crear_servicio_organizaciones(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


@invitaciones_bp.get("")
@login_required
def pendientes():
    """Invitaciones vigentes dirigidas al correo del usuario."""
    momento = ahora_utc()
    return jsonify({
        "invitaciones": [
            invitacion_a_dict(i, momento) for i in _servicio().pendientes_de(usuario_actual())
        ]
    })


@invitaciones_bp.post("/consulta")
def consultar():
    """Datos de la invitación del enlace. No requiere sesión (CU11 paso 2).

    Indica además si la sesión actual corresponde al correo invitado, para
    que la pantalla ofrezca responder, iniciar sesión o crear una cuenta.
    """
    solicitud = validar(SolicitudToken, request.get_json(silent=True))
    invitacion = _servicio().consultar_invitacion(solicitud.token)
    datos = invitacion_a_dict(invitacion, ahora_utc())
    datos["sesion_con_el_correo"] = (
        current_user.is_authenticated and current_user.correo == invitacion.correo
    )
    return jsonify({"invitacion": datos})


@invitaciones_bp.post("/<int:id_invitacion>/aceptacion")
@login_required
def aceptar(id_invitacion):
    """Acepta la invitación y suma al usuario como Miembro (RF13 CA1)."""
    organizacion = _servicio().responder(id_invitacion, usuario_actual(), aceptar=True)
    return jsonify({
        "mensaje": f"Ya sos miembro de {organizacion.nombre}.",
        "id_organizacion": organizacion.id,
    })


@invitaciones_bp.post("/<int:id_invitacion>/rechazo")
@login_required
def rechazar(id_invitacion):
    """Rechaza la invitación (CU11 4a)."""
    _servicio().responder(id_invitacion, usuario_actual(), aceptar=False)
    return jsonify({"mensaje": "Rechazaste la invitación."})
