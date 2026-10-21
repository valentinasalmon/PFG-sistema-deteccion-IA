"""Ruta del panel principal (funcionalidad 013).

GET /api/panel    Resumen de los casos y actividad reciente del usuario (RF48)
"""
from flask import Blueprint, jsonify
from flask_login import login_required

from app.esquemas.panel import panel_a_dict
from app.seguridad.autenticacion import usuario_actual
from app.servicios.fabrica import crear_servicio_panel
from app.utilidades.tiempo import ahora_utc

panel_bp = Blueprint("panel", __name__, url_prefix="/api/panel")


@panel_bp.get("")
@login_required
def panel():
    """Panel principal del usuario con sesión (RF48, CU30)."""
    datos = crear_servicio_panel().panel(usuario_actual())
    return jsonify({"panel": panel_a_dict(datos, ahora_utc())})
