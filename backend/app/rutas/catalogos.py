"""Rutas de catálogos públicos.

GET /api/catalogos/aseguradoras    Aseguradoras de la SSN para el registro (CP-18)
"""
from flask import Blueprint, jsonify

from app.esquemas.organizaciones import aseguradora_de_catalogo_a_dict
from app.servicios.fabrica import crear_catalogo_aseguradoras

catalogos_bp = Blueprint("catalogos", __name__, url_prefix="/api/catalogos")


@catalogos_bp.get("/aseguradoras")
def aseguradoras():
    """Las 192 aseguradoras habilitadas, ordenadas por denominación. No requiere sesión."""
    return jsonify({
        "aseguradoras": [
            aseguradora_de_catalogo_a_dict(a) for a in crear_catalogo_aseguradoras().todas()
        ]
    })
