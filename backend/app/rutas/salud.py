"""Ruta de salud de la API.

GET /api/salud
    200: todos los componentes responden.
    503: algún componente no responde (indica cuál).

Realiza: CA2 y CA3 de la funcionalidad 001.
"""
from flask import Blueprint, current_app, jsonify

from app.servicios.servicio_salud import crear_servicio_salud

salud_bp = Blueprint("salud", __name__, url_prefix="/api")


@salud_bp.get("/salud")
def obtener_salud():
    """Informa el estado de la API, la base de datos y Redis."""
    servicio = crear_servicio_salud(current_app.config["URL_REDIS"])
    estado = servicio.obtener_estado()
    cuerpo = {
        "estado": "ok" if estado.saludable else "degradado",
        "componentes": estado.componentes,
        "entorno": current_app.config["NOMBRE"],
        "version": current_app.config["VERSION_APLICACION"],
    }
    return jsonify(cuerpo), 200 if estado.saludable else 503
