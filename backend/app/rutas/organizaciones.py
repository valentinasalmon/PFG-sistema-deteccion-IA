"""Rutas de organizaciones, miembros e invitaciones de una organización.

GET    /api/organizaciones                                      Mis organizaciones
POST   /api/organizaciones                                      Crear (RF10)
GET    /api/organizaciones/<id>                                 Ver (miembro)
PATCH  /api/organizaciones/<id>                                 Editar (RF11, Referente)
DELETE /api/organizaciones/<id>                                 Eliminar (RF18, Referente)
GET    /api/organizaciones/<id>/miembros                        Miembros (RF16)
PATCH  /api/organizaciones/<id>/miembros/<id_usuario>           Cargo (RF15, Referente)
DELETE /api/organizaciones/<id>/miembros/<id_usuario>           Desvincular (RF14, Referente)
POST   /api/organizaciones/<id>/referente                       Designar Referente (RF15)
POST   /api/organizaciones/<id>/abandono                        Abandonar (RF17)
GET    /api/organizaciones/<id>/invitaciones                    Pendientes (Referente)
POST   /api/organizaciones/<id>/invitaciones                    Invitar (RF12, Referente)
POST   /api/organizaciones/<id>/invitaciones/<id_inv>/reenvio   Reenviar (RF12 CA4)
DELETE /api/organizaciones/<id>/invitaciones/<id_inv>           Cancelar (RF12 CA4)
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.organizaciones import (
    SolicitudAbandono,
    SolicitudCargo,
    SolicitudEdicionOrganizacion,
    SolicitudEliminacion,
    SolicitudInvitacion,
    SolicitudOrganizacion,
    SolicitudReferente,
    invitacion_a_dict,
    miembro_a_dict,
    organizacion_a_dict,
)
from app.seguridad.autenticacion import cerrar_sesion, usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.esquemas.administracion import SolicitudCambioPlan
from app.servicios.fabrica import crear_servicio_organizaciones, crear_servicio_planes
from app.servicios.servicio_sesion import MOTIVO_CIERRE_CUENTA_DESACTIVADA
from app.utilidades.tiempo import ahora_utc

organizaciones_bp = Blueprint("organizaciones", __name__, url_prefix="/api/organizaciones")


def _servicio():
    return crear_servicio_organizaciones(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud(),
        current_app.extensions["almacenamiento"],
    )


def _cuerpo():
    return request.get_json(silent=True)


@organizaciones_bp.get("")
@login_required
def listar():
    """Organizaciones a las que pertenece el usuario, con su rol (RN06)."""
    membresias = _servicio().listar(usuario_actual())
    return jsonify(
        {"organizaciones": [organizacion_a_dict(m.organizacion, m) for m in membresias]}
    )


@organizaciones_bp.post("")
@login_required
def crear():
    """Crea una organización con el usuario como Referente (RF10)."""
    solicitud = validar(SolicitudOrganizacion, _cuerpo())
    servicio = _servicio()
    usuario = usuario_actual()
    organizacion = servicio.crear(usuario, solicitud.model_dump())
    _, membresia = servicio.obtener(organizacion.id, usuario)
    return jsonify({"organizacion": organizacion_a_dict(organizacion, membresia, servicio)}), 201


@organizaciones_bp.get("/<int:id_organizacion>")
@login_required
def obtener(id_organizacion):
    """Datos de la organización, su plan y el rol del usuario."""
    servicio = _servicio()
    organizacion, membresia = servicio.obtener(id_organizacion, usuario_actual())
    return jsonify({"organizacion": organizacion_a_dict(organizacion, membresia, servicio)})


@organizaciones_bp.patch("/<int:id_organizacion>")
@login_required
def editar(id_organizacion):
    """Modifica los datos de la organización (RF11)."""
    solicitud = validar(SolicitudEdicionOrganizacion, _cuerpo())
    servicio = _servicio()
    usuario = usuario_actual()
    servicio.editar(id_organizacion, usuario, solicitud.model_dump(exclude_unset=True))
    organizacion, membresia = servicio.obtener(id_organizacion, usuario)
    return jsonify({
        "organizacion": organizacion_a_dict(organizacion, membresia, servicio),
        "mensaje": "Los datos de la organización fueron actualizados.",
    })


@organizaciones_bp.delete("/<int:id_organizacion>")
@login_required
def eliminar(id_organizacion):
    """Elimina la organización con la confirmación de su nombre (RF18)."""
    solicitud = validar(SolicitudEliminacion, _cuerpo())
    desactivada = _servicio().eliminar(id_organizacion, usuario_actual(), solicitud.confirmacion)
    return _respuesta_de_salida("La organización fue eliminada.", True, desactivada)


@organizaciones_bp.get("/<int:id_organizacion>/miembros")
@login_required
def miembros(id_organizacion):
    """Miembros de la organización (RF16)."""
    membresias = _servicio().miembros(id_organizacion, usuario_actual())
    return jsonify({"miembros": [miembro_a_dict(m) for m in membresias]})


@organizaciones_bp.patch("/<int:id_organizacion>/miembros/<int:id_usuario>")
@login_required
def editar_membresia(id_organizacion, id_usuario):
    """Cambia el cargo de un miembro (RF15 CA1)."""
    solicitud = validar(SolicitudCargo, _cuerpo())
    membresia = _servicio().editar_membresia(
        id_organizacion, usuario_actual(), id_usuario, solicitud.cargo
    )
    return jsonify({"miembro": miembro_a_dict(membresia), "mensaje": "El cargo fue actualizado."})


@organizaciones_bp.delete("/<int:id_organizacion>/miembros/<int:id_usuario>")
@login_required
def desvincular(id_organizacion, id_usuario):
    """Desvincula a un miembro (RF14)."""
    _servicio().desvincular(id_organizacion, usuario_actual(), id_usuario)
    return jsonify({"mensaje": "El miembro fue desvinculado de la organización."})


@organizaciones_bp.post("/<int:id_organizacion>/referente")
@login_required
def designar_referente(id_organizacion):
    """Transfiere el rol de Referente a otro miembro (RF15 CA2)."""
    solicitud = validar(SolicitudReferente, _cuerpo())
    _servicio().designar_referente(id_organizacion, usuario_actual(), solicitud.id_usuario)
    return jsonify({"mensaje": "Designaste un nuevo Referente. Ahora sos miembro."})


@organizaciones_bp.post("/<int:id_organizacion>/abandono")
@login_required
def abandonar(id_organizacion):
    """El usuario abandona la organización (RF17)."""
    solicitud = validar(SolicitudAbandono, _cuerpo())
    eliminada, desactivada = _servicio().abandonar(
        id_organizacion, usuario_actual(), solicitud.confirmar_eliminacion
    )
    mensaje = (
        "Abandonaste la organización y, como eras su único miembro, se eliminó."
        if eliminada else "Abandonaste la organización."
    )
    return _respuesta_de_salida(mensaje, eliminada, desactivada)


def _respuesta_de_salida(mensaje, eliminada, desactivada):
    """Si la cuenta quedó desactivada (RN39), cierra la sesión actual."""
    if desactivada:
        cerrar_sesion(MOTIVO_CIERRE_CUENTA_DESACTIVADA)
        mensaje += " Tu cuenta quedó desactivada porque ya no pertenecés a ninguna aseguradora."
    return jsonify(
        {"mensaje": mensaje, "organizacion_eliminada": eliminada, "cuenta_desactivada": desactivada}
    )


@organizaciones_bp.get("/<int:id_organizacion>/invitaciones")
@login_required
def invitaciones(id_organizacion):
    """Invitaciones pendientes de la organización (Referente)."""
    pendientes = _servicio().invitaciones(id_organizacion, usuario_actual())
    momento = ahora_utc()
    return jsonify({"invitaciones": [invitacion_a_dict(i, momento) for i in pendientes]})


@organizaciones_bp.post("/<int:id_organizacion>/invitaciones")
@login_required
def invitar(id_organizacion):
    """Invita a una persona por correo (RF12)."""
    solicitud = validar(SolicitudInvitacion, _cuerpo())
    invitacion = _servicio().invitar(
        id_organizacion, usuario_actual(), solicitud.correo, solicitud.cargo
    )
    return jsonify({
        "invitacion": invitacion_a_dict(invitacion, ahora_utc()),
        "mensaje": f"Enviamos la invitación a {invitacion.correo}.",
    }), 201


@organizaciones_bp.post("/<int:id_organizacion>/invitaciones/<int:id_invitacion>/reenvio")
@login_required
def reenviar_invitacion(id_organizacion, id_invitacion):
    """Reenvía una invitación y renueva su vencimiento (RF12 CA4)."""
    invitacion = _servicio().reenviar_invitacion(id_organizacion, usuario_actual(), id_invitacion)
    return jsonify({
        "invitacion": invitacion_a_dict(invitacion, ahora_utc()),
        "mensaje": f"Reenviamos la invitación a {invitacion.correo}.",
    })


@organizaciones_bp.delete("/<int:id_organizacion>/invitaciones/<int:id_invitacion>")
@login_required
def cancelar_invitacion(id_organizacion, id_invitacion):
    """Cancela una invitación pendiente (RF12 CA4)."""
    _servicio().cancelar_invitacion(id_organizacion, usuario_actual(), id_invitacion)
    return jsonify({"mensaje": "La invitación fue cancelada."})


def _planes():
    return crear_servicio_planes(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


@organizaciones_bp.get("/<int:id_organizacion>/plan")
@login_required
def plan(id_organizacion):
    """Plan, límites y consumo de la organización (RF20 CA1, funcionalidad 014)."""
    return jsonify({"plan": _planes().plan_de_organizacion(id_organizacion, usuario_actual())})


@organizaciones_bp.post("/<int:id_organizacion>/plan")
@login_required
def cambiar_plan(id_organizacion):
    """Cambia el plan después del pago simulado (RF20 CA2). Solo el Referente."""
    solicitud = validar(SolicitudCambioPlan, request.get_json(silent=True))
    servicio = _planes()
    organizacion = servicio.cambiar_plan(id_organizacion, usuario_actual(), solicitud.plan)
    return jsonify({
        "plan": servicio.plan_de_organizacion(organizacion.id, usuario_actual()),
        "mensaje": "Listo: el plan nuevo ya está activo. El pago fue simulado; no se cobró nada.",
    })
