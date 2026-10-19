"""Rutas de los informes PDF de un caso.

GET  /api/casos/<id>/informes                          Historial de informes (RF45)
GET  /api/casos/<id>/informes/<id_informe>/descarga    Enlace firmado de 5 minutos
POST /api/casos/<id>/analisis/<id_analisis>/informe    Volver a generar un informe que faltó
"""
from flask import Blueprint, current_app, jsonify
from flask_login import login_required

from app.esquemas.analisis import informe_a_dict
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_informes

informes_bp = Blueprint("informes", __name__, url_prefix="/api/casos/<int:id_caso>")


def _servicio():
    return crear_servicio_informes(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], origen_de_la_solicitud(),
    )


@informes_bp.get("/informes")
@login_required
def listar(id_caso):
    """Informes del caso, del más reciente al más antiguo."""
    informes = _servicio().listar(id_caso, usuario_actual())
    return jsonify({"informes": [informe_a_dict(informe) for informe in informes]})


@informes_bp.get("/informes/<int:id_informe>/descarga")
@login_required
def descargar(id_caso, id_informe):
    """Enlace firmado de corta duración al PDF; queda en la auditoría (RF45 CA2)."""
    url = _servicio().enlace_de_descarga(id_caso, id_informe, usuario_actual())
    return jsonify({"url": url})


@informes_bp.post("/analisis/<int:id_analisis>/informe")
@login_required
def regenerar(id_caso, id_analisis):
    """Genera el informe de un análisis finalizado que no lo tiene (CA6 de la 008)."""
    informe = _servicio().regenerar(id_caso, id_analisis, usuario_actual())
    return jsonify({"informe": informe_a_dict(informe), "mensaje": "Se generó el informe."}), 201
