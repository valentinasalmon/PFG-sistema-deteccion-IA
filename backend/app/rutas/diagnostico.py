"""Página pública «Probar mi celular» (funcionalidad 047).

POST /api/diagnostico/foto   Recibe una foto (campo ``foto``) y devuelve qué llegó:
                             formato, metadatos, cámara, fecha y ubicación.

No requiere sesión ni guarda la foto: sirve para medir qué entrega cada
celular según el camino que se use para elegir la foto. Los límites de
pedidos por minuto de Nginx (030) la protegen como al resto de la API.

Realiza: CA1 de la funcionalidad 047.
"""
from flask import Blueprint, current_app, jsonify, request

from app.servicios.fabrica import crear_servicio_diagnostico

diagnostico_bp = Blueprint("diagnostico", __name__, url_prefix="/api/diagnostico")


@diagnostico_bp.post("/foto")
def diagnosticar_foto():
    """Lee la foto subida y devuelve lo que trae, sin guardarla."""
    archivo = request.files.get("foto")
    contenido = archivo.read() if archivo else b""
    resultado = crear_servicio_diagnostico(current_app.config).diagnosticar(
        contenido, request.headers.get("User-Agent")
    )
    return jsonify({"diagnostico": resultado})
