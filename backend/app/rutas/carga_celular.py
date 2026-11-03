"""Rutas de la carga de fotos con un enlace, sin iniciar sesión (024 y 028).

POST   /api/casos/<id>/enlace-carga   Generar el enlace y su QR (sesión iniciada)
DELETE /api/casos/<id>/enlace-carga   Cancelar los enlaces vigentes (sesión iniciada)
GET    /api/casos/<id>/enlaces-persona-afectada        Enlaces vigentes (sesión)
POST   /api/casos/<id>/enlaces-persona-afectada        Crear uno, ``dias`` y
                                                       ``destinatario`` (sesión)
DELETE /api/casos/<id>/enlaces-persona-afectada/<id>   Anularlo (sesión)
GET    /api/carga/<token>             Datos para la página del enlace (pública)
POST   /api/carga/<token>             Cargar una foto, campo ``archivo`` y, para la
                                      persona afectada, ``declaracion`` (pública)

Las dos últimas no usan sesión: el token del enlace es la credencial. Por eso
no llevan protección CSRF, que solo tiene sentido con cookies de sesión.

Realiza: RF53 (CA2); CP-32.
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.extensiones import proteccion_csrf
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_enlaces_carga
from app.servicios.servicio_enlaces_carga import DIAS_MAXIMOS
from app.utilidades.qr import qr_svg

enlaces_carga_bp = Blueprint("enlaces_carga", __name__, url_prefix="/api")
carga_celular_bp = Blueprint("carga_celular", __name__, url_prefix="/api/carga")
proteccion_csrf.exempt(carga_celular_bp)


def _servicio():
    return crear_servicio_enlaces_carga(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], origen_de_la_solicitud(),
    )


def _url_de(token):
    return f"{current_app.config['URL_FRONTEND'].rstrip('/')}/cargar/{token}"


@enlaces_carga_bp.post("/casos/<int:id_caso>/enlace-carga")
@login_required
def crear(id_caso):
    """Genera el enlace de carga del caso y su código QR."""
    enlace, token = _servicio().crear(id_caso, usuario_actual())
    url = _url_de(token)
    return jsonify({
        "enlace": {
            "url": url, "qr": qr_svg(url),
            "vence_en": enlace.vence_en.isoformat(timespec="seconds"),
        },
    }), 201


@enlaces_carga_bp.delete("/casos/<int:id_caso>/enlace-carga")
@login_required
def cancelar(id_caso):
    """Cancela los enlaces vigentes del usuario para el caso."""
    _servicio().cancelar(id_caso, usuario_actual())
    return jsonify({"mensaje": "El enlace de carga se canceló."})


def _enlace_persona_afectada(enlace):
    return {
        "id": enlace.id,
        "destinatario": enlace.destinatario,
        "creado_en": enlace.creado_en.isoformat(timespec="seconds"),
        "vence_en": enlace.vence_en.isoformat(timespec="seconds"),
        "creado_por": f"{enlace.usuario.nombre} {enlace.usuario.apellido}",
        "cargas": enlace.cargas,
        "declaracion_aceptada": enlace.declaracion_aceptada_en is not None,
    }


@enlaces_carga_bp.get("/casos/<int:id_caso>/enlaces-persona-afectada")
@login_required
def listar_para_persona_afectada(id_caso):
    """Enlaces vigentes para la persona afectada; el enlace en sí no se puede volver a ver."""
    enlaces = _servicio().listar_para_persona_afectada(id_caso, usuario_actual())
    return jsonify({
        "enlaces": [_enlace_persona_afectada(enlace) for enlace in enlaces],
        "dias_maximos": DIAS_MAXIMOS,
    })


@enlaces_carga_bp.post("/casos/<int:id_caso>/enlaces-persona-afectada")
@login_required
def crear_para_persona_afectada(id_caso):
    """Genera un enlace para que la persona afectada suba sus fotos (028, CP-32)."""
    datos = request.get_json(silent=True) or {}
    enlace, token = _servicio().crear_para_persona_afectada(
        id_caso, usuario_actual(), datos.get("dias"), datos.get("destinatario")
    )
    return jsonify({
        "enlace": {**_enlace_persona_afectada(enlace), "url": _url_de(token)},
        "mensaje": "El enlace está listo. Copialo y mandáselo a la persona.",
    }), 201


@enlaces_carga_bp.delete("/casos/<int:id_caso>/enlaces-persona-afectada/<int:id_enlace>")
@login_required
def anular(id_caso, id_enlace):
    """Anula un enlace para la persona afectada."""
    _servicio().anular(id_caso, id_enlace, usuario_actual())
    return jsonify({"mensaje": "El enlace se anuló: ya no sirve para subir fotos."})


@carga_celular_bp.get("/<token>")
def consultar(token):
    """Vencimiento, fotos que todavía se pueden cargar y, según el tipo, caso o solicitante."""
    datos = _servicio().consultar(token)
    return jsonify({**datos, "tamanio_maximo": current_app.config["TAMANIO_MAXIMO_IMAGEN"]})


@carga_celular_bp.post("/<token>")
def cargar(token):
    """Carga una foto con el enlace; solo devuelve lo necesario para confirmarla."""
    archivo = request.files.get("archivo")
    nombre = archivo.filename if archivo else None
    contenido = archivo.read() if archivo else b""
    declaracion = request.form.get("declaracion") == "true"
    imagen = _servicio().cargar(token, nombre, contenido, declaracion)
    return jsonify({
        "imagen": {"nombre": imagen.nombre_original, "huella": imagen.huella},
        "mensaje": f"Se cargó «{imagen.nombre_original}».",
    }), 201
