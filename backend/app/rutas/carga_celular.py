"""Rutas de la carga de fotos desde el celular con un enlace de un solo uso (024).

POST   /api/casos/<id>/enlace-carga   Generar el enlace y su QR (sesión iniciada)
DELETE /api/casos/<id>/enlace-carga   Cancelar los enlaces vigentes (sesión iniciada)
GET    /api/carga/<token>             Datos para la página del celular (pública)
POST   /api/carga/<token>             Cargar una foto, campo ``archivo`` (pública)

Las dos últimas no usan sesión: el token del enlace es la credencial. Por eso
no llevan protección CSRF, que solo tiene sentido con cookies de sesión.

Realiza: RF53 (CA2).
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.extensiones import proteccion_csrf
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_enlaces_carga
from app.servicios.servicio_enlaces_carga import MAXIMO_CARGAS
from app.utilidades.qr import qr_svg

enlaces_carga_bp = Blueprint("enlaces_carga", __name__, url_prefix="/api")
carga_celular_bp = Blueprint("carga_celular", __name__, url_prefix="/api/carga")
proteccion_csrf.exempt(carga_celular_bp)


def _servicio():
    return crear_servicio_enlaces_carga(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], origen_de_la_solicitud(),
    )


@enlaces_carga_bp.post("/casos/<int:id_caso>/enlace-carga")
@login_required
def crear(id_caso):
    """Genera el enlace de carga del caso y su código QR."""
    enlace, token = _servicio().crear(id_caso, usuario_actual())
    url = f"{current_app.config['URL_FRONTEND'].rstrip('/')}/cargar/{token}"
    return jsonify({
        "enlace": {
            "url": url, "qr": qr_svg(url),
            "vence_en": enlace.vence_en.isoformat(timespec="seconds"),
            "maximo": MAXIMO_CARGAS,
        },
    }), 201


@enlaces_carga_bp.delete("/casos/<int:id_caso>/enlace-carga")
@login_required
def cancelar(id_caso):
    """Cancela los enlaces vigentes del usuario para el caso."""
    _servicio().cancelar(id_caso, usuario_actual())
    return jsonify({"mensaje": "El enlace de carga se canceló."})


@carga_celular_bp.get("/<token>")
def consultar(token):
    """Caso, vencimiento y fotos que todavía se pueden cargar con el enlace."""
    datos = _servicio().consultar(token)
    return jsonify({**datos, "tamanio_maximo": current_app.config["TAMANIO_MAXIMO_IMAGEN"]})


@carga_celular_bp.post("/<token>")
def cargar(token):
    """Carga una foto con el enlace; solo devuelve lo necesario para confirmarla."""
    archivo = request.files.get("archivo")
    nombre = archivo.filename if archivo else None
    contenido = archivo.read() if archivo else b""
    imagen = _servicio().cargar(token, nombre, contenido)
    return jsonify({
        "imagen": {"nombre": imagen.nombre_original, "huella": imagen.huella},
        "mensaje": f"Se cargó «{imagen.nombre_original}».",
    }), 201
