"""Rutas de las imágenes de los casos.

GET    /api/casos/<id>/imagenes                       Imágenes con su vista previa (RF35)
POST   /api/casos/<id>/imagenes                       Cargar una imagen, campo ``archivo`` (RF34)
GET    /api/casos/<id>/imagenes/<id_imagen>/descarga  Enlace firmado al original
DELETE /api/casos/<id>/imagenes/<id_imagen>           Eliminar una imagen (RF36)
POST   /api/casos/<id>/imagenes/<id_imagen>/sello     Recibos de BFA del navegador (RF37)
GET    /api/archivos/<token>                          Archivo del almacenamiento local

La última ruta solo sirve al almacenamiento local (desarrollo y pruebas): con
S3, los enlaces apuntan directamente a S3 y vencen igual que estos.
"""
from flask import Blueprint, Response, current_app, jsonify, request
from flask_login import login_required

from app.esquemas.imagenes import imagen_a_dict
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_imagenes

imagenes_bp = Blueprint("imagenes", __name__, url_prefix="/api")


def _servicio():
    return crear_servicio_imagenes(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], origen_de_la_solicitud(),
    )


@imagenes_bp.get("/casos/<int:id_caso>/imagenes")
@login_required
def listar(id_caso):
    """Imágenes del caso, el límite del plan y si el usuario puede cargar o eliminar."""
    servicio = _servicio()
    caso, permiso, imagenes = servicio.listar(id_caso, usuario_actual())
    analizadas = servicio.analizadas(imagenes)
    return jsonify({
        "imagenes": [
            imagen_a_dict(i, servicio.enlace_miniatura(i), i.id in analizadas) for i in imagenes
        ],
        "limite": servicio.limite_de_imagenes(caso),
        "tamanio_maximo": current_app.config["TAMANIO_MAXIMO_IMAGEN"],
        "puede_modificar": servicio.puede_modificar(caso, permiso),
        "sello_en_navegador": servicio.sello_en_navegador,
    })


@imagenes_bp.post("/casos/<int:id_caso>/imagenes")
@login_required
def cargar(id_caso):
    """Carga un archivo; cada archivo va en su propia solicitud (RF34 CA5)."""
    archivo = request.files.get("archivo")
    nombre = archivo.filename if archivo else None
    contenido = archivo.read() if archivo else b""
    servicio = _servicio()
    imagen = servicio.cargar(id_caso, usuario_actual(), nombre, contenido)
    return jsonify({
        "imagen": imagen_a_dict(imagen, servicio.enlace_miniatura(imagen)),
        "mensaje": f"Se cargó «{imagen.nombre_original}».",
    }), 201


@imagenes_bp.get("/casos/<int:id_caso>/imagenes/<int:id_imagen>/descarga")
@login_required
def descargar(id_caso, id_imagen):
    """Enlace firmado de corta duración para descargar el original (RF35 CA2)."""
    return jsonify({"url": _servicio().enlace_original(id_caso, id_imagen, usuario_actual())})


@imagenes_bp.delete("/casos/<int:id_caso>/imagenes/<int:id_imagen>")
@login_required
def eliminar(id_caso, id_imagen):
    """Elimina la imagen y sus archivos (RF36)."""
    _servicio().eliminar(id_caso, id_imagen, usuario_actual())
    return jsonify({"mensaje": "La imagen fue eliminada."})


@imagenes_bp.post("/casos/<int:id_caso>/imagenes/<int:id_imagen>/sello")
@login_required
def registrar_sello(id_caso, id_imagen):
    """Guarda el recibo temporal o el definitivo que el navegador obtuvo de BFA (RF37)."""
    servicio = _servicio()
    datos = request.get_json(silent=True)
    imagen = servicio.registrar_sello(
        id_caso, id_imagen, usuario_actual(), datos if isinstance(datos, dict) else {}
    )
    return jsonify({"imagen": imagen_a_dict(imagen, servicio.enlace_miniatura(imagen))})


@imagenes_bp.get("/archivos/<token>")
def archivo_local(token):
    """Entrega un archivo del almacenamiento local con un enlace firmado vigente."""
    contenido, tipo_mime, disposicion = _servicio().abrir_enlace_local(token)
    cabeceras = {"Cache-Control": "private, max-age=300", "X-Content-Type-Options": "nosniff"}
    if disposicion:
        cabeceras["Content-Disposition"] = disposicion
    return Response(contenido, mimetype=tipo_mime, headers=cabeceras)
