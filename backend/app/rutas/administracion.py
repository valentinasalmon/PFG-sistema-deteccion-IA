"""Rutas del Administrador de la plataforma (funcionalidad 021).

GET  /api/administracion/aseguradoras-pendientes                 Aseguradoras por aprobar
POST /api/administracion/organizaciones/<id>/aprobacion          Aprobar (RN38)
POST /api/administracion/organizaciones/<id>/rechazo             Rechazar con motivo (RN38)

El tablero completo de administración es de la funcionalidad 014.
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.organizaciones import SolicitudRechazo, aseguradora_pendiente_a_dict
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_organizaciones

administracion_bp = Blueprint("administracion", __name__, url_prefix="/api/administracion")


def _servicio():
    return crear_servicio_organizaciones(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


@administracion_bp.get("/aseguradoras-pendientes")
@login_required
def aseguradoras_pendientes():
    """Aseguradoras que esperan aprobación, con su Referente (CA7 de la 021)."""
    pendientes = _servicio().pendientes_de_aprobacion(usuario_actual())
    return jsonify(
        {"aseguradoras": [aseguradora_pendiente_a_dict(o, r) for o, r in pendientes]}
    )


@administracion_bp.post("/organizaciones/<int:id_organizacion>/aprobacion")
@login_required
def aprobar(id_organizacion):
    """Aprueba una aseguradora pendiente (CA8 de la 021)."""
    organizacion = _servicio().aprobar(usuario_actual(), id_organizacion)
    return jsonify({"mensaje": f"{organizacion.nombre} fue aprobada."})


@administracion_bp.post("/organizaciones/<int:id_organizacion>/rechazo")
@login_required
def rechazar(id_organizacion):
    """Rechaza una aseguradora pendiente indicando el motivo (CA9 de la 021)."""
    solicitud = validar(SolicitudRechazo, request.get_json(silent=True))
    _servicio().rechazar(usuario_actual(), id_organizacion, solicitud.motivo)
    return jsonify({"mensaje": "La aseguradora fue rechazada y se avisó a quien la registró."})
