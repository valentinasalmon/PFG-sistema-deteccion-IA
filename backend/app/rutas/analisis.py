"""Rutas de los análisis de un caso.

POST /api/casos/<id>/analisis                Pedir el análisis de imágenes (RF38)
GET  /api/casos/<id>/analisis                Historial de análisis del caso
GET  /api/casos/<id>/analisis/<id_analisis>  Estado, progreso y resultados (RF43, RF46)
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.analisis import (
    SolicitudAnalisis,
    analisis_a_dict,
    analisis_resumen_a_dict,
)
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_analisis

analisis_bp = Blueprint("analisis", __name__, url_prefix="/api/casos/<int:id_caso>/analisis")


def _servicio():
    return crear_servicio_analisis(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], current_app.extensions["cola_analisis"],
        origen_de_la_solicitud(),
    )


@analisis_bp.post("")
@login_required
def solicitar(id_caso):
    """Encola el análisis de las imágenes elegidas; el caso pasa a En análisis (RF38)."""
    solicitud = validar(SolicitudAnalisis, request.get_json(silent=True))
    analisis = _servicio().solicitar(id_caso, usuario_actual(), solicitud.imagenes)
    return jsonify({
        "analisis": analisis_resumen_a_dict(analisis),
        "mensaje": "El análisis quedó en cola. Te avisamos por correo cuando termine.",
    }), 202


@analisis_bp.get("")
@login_required
def listar(id_caso):
    """Historial de análisis del caso, del más reciente al más antiguo."""
    historial = _servicio().listar(id_caso, usuario_actual())
    return jsonify({"analisis": [analisis_resumen_a_dict(a) for a in historial]})


@analisis_bp.get("/<int:id_analisis>")
@login_required
def detalle(id_caso, id_analisis):
    """Estado, progreso y resultados de cada capa por imagen."""
    analisis = _servicio().detalle(id_caso, id_analisis, usuario_actual())
    return jsonify({"analisis": analisis_a_dict(analisis)})
