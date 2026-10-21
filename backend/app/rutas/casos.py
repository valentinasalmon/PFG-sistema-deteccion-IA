"""Rutas de casos y accesos compartidos (funcionalidad 005).

GET    /api/casos                                   Listado con búsqueda y filtros (RF26)
POST   /api/casos                                   Crear (RF23)
GET    /api/casos/resumen                           Cantidad de casos por estado
GET    /api/casos/transferencias                    Transferencias que esperan mi respuesta
GET    /api/casos/<id>                              Detalle y accesos (RF24)
PATCH  /api/casos/<id>                              Editar (RF25)
DELETE /api/casos/<id>                              Eliminar con confirmación (RF32)
POST   /api/casos/<id>/estado                       Cerrar, archivar, desarchivar o reabrir
POST   /api/casos/<id>/accesos                      Compartir (RF30)
PATCH  /api/casos/<id>/accesos/<id_acceso>          Cambiar el nivel (RF31)
DELETE /api/casos/<id>/accesos/<id_acceso>          Revocar (RF31)
POST   /api/casos/<id>/transferencia                Transferir (RF33)
DELETE /api/casos/<id>/transferencia                Cancelar una transferencia pendiente
POST   /api/casos/<id>/transferencia/aceptacion     Aceptar un caso personal
POST   /api/casos/<id>/transferencia/rechazo        Rechazar un caso personal
"""
import math

from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.casos import (
    FiltrosCasos,
    SolicitudCaso,
    SolicitudCompartir,
    SolicitudEdicionCaso,
    SolicitudEstado,
    SolicitudProrroga,
    SolicitudNivel,
    SolicitudTransferencia,
    acceso_a_dict,
    caso_a_dict,
    transferencia_a_dict,
)
from app.esquemas.organizaciones import SolicitudEliminacion
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_casos, crear_tareas_de_retencion

casos_bp = Blueprint("casos", __name__, url_prefix="/api/casos")

POR_PAGINA = 20
MENSAJES_ESTADO = {
    "cerrar": "El caso fue cerrado. Comenzó el plazo de retención de 5 años.",
    "archivar": "El caso fue archivado.",
    "desarchivar": "El caso volvió a Cerrado.",
    "reabrir": "El caso fue reabierto.",
}


def _servicio():
    return crear_servicio_casos(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud(),
        current_app.extensions["almacenamiento"],
    )


def _cuerpo():
    return request.get_json(silent=True)


def _detalle(servicio, caso, permiso, mensaje=None):
    datos = {"caso": caso_a_dict(caso, permiso)}
    accesos = [] if caso.es_personal else servicio.accesos(caso)
    datos["accesos"] = [acceso_a_dict(a) for a in accesos]
    if mensaje:
        datos["mensaje"] = mensaje
    return jsonify(datos)


@casos_bp.get("")
@login_required
def listar():
    """Casos accesibles, paginados, con búsqueda y filtros (RF26)."""
    filtros = validar(FiltrosCasos, request.args.to_dict())
    servicio = _servicio()
    usuario = usuario_actual()
    casos, total = servicio.listar(
        usuario, filtros.model_dump(exclude={"pagina"}), filtros.pagina, POR_PAGINA
    )
    return jsonify({
        "casos": [caso_a_dict(c, servicio.permiso(c, usuario)) for c in casos],
        "total": total,
        "pagina": filtros.pagina,
        "paginas": max(1, math.ceil(total / POR_PAGINA)),
    })


@casos_bp.post("")
@login_required
def crear():
    """Crea un caso en Borrador (RF23)."""
    solicitud = validar(SolicitudCaso, _cuerpo())
    servicio = _servicio()
    caso = servicio.crear(usuario_actual(), solicitud.model_dump())
    return _detalle(servicio, caso, "responsable", f"Se creó el caso {caso.numero}."), 201


@casos_bp.get("/resumen")
@login_required
def resumen():
    """Cantidad de casos accesibles por estado."""
    return jsonify({"por_estado": _servicio().resumen(usuario_actual())})


@casos_bp.get("/transferencias")
@login_required
def transferencias():
    """Casos personales que esperan que el usuario acepte su transferencia (RF33 CA2)."""
    pendientes = _servicio().transferencias_pendientes(usuario_actual())
    return jsonify({"transferencias": [transferencia_a_dict(c) for c in pendientes]})


@casos_bp.get("/<int:id_caso>")
@login_required
def obtener(id_caso):
    """Detalle del caso con las acciones que habilita el permiso (RF24)."""
    servicio = _servicio()
    caso, permiso = servicio.detalle(id_caso, usuario_actual())
    return _detalle(servicio, caso, permiso)


@casos_bp.patch("/<int:id_caso>")
@login_required
def editar(id_caso):
    """Modifica los datos del caso (RF25)."""
    solicitud = validar(SolicitudEdicionCaso, _cuerpo())
    servicio = _servicio()
    usuario = usuario_actual()
    caso = servicio.editar(id_caso, usuario, solicitud.model_dump(exclude_unset=True))
    return _detalle(
        servicio, caso, servicio.permiso(caso, usuario), "Los datos del caso fueron actualizados."
    )


@casos_bp.delete("/<int:id_caso>")
@login_required
def eliminar(id_caso):
    """Elimina el caso de forma definitiva (RF32)."""
    solicitud = validar(SolicitudEliminacion, _cuerpo())
    _servicio().eliminar(id_caso, usuario_actual(), solicitud.confirmacion)
    return jsonify({"mensaje": "El caso fue eliminado."})


@casos_bp.post("/<int:id_caso>/estado")
@login_required
def cambiar_estado(id_caso):
    """Cierra, archiva, desarchiva o reabre el caso (RF27 a RF29)."""
    solicitud = validar(SolicitudEstado, _cuerpo())
    servicio = _servicio()
    caso = servicio.cambiar_estado(id_caso, usuario_actual(), solicitud.operacion)
    return _detalle(servicio, caso, "responsable", MENSAJES_ESTADO[solicitud.operacion])


@casos_bp.post("/<int:id_caso>/prorroga")
@login_required
def prorrogar(id_caso):
    """Extiende 1 año la retención indicando el motivo (RF51, funcionalidad 015)."""
    solicitud = validar(SolicitudProrroga, _cuerpo())
    servicio = _servicio()
    caso, vence = crear_tareas_de_retencion(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], origen_de_la_solicitud(),
    ).prorrogar(id_caso, usuario_actual(), solicitud.motivo)
    return _detalle(
        servicio, caso, "responsable",
        f"Listo: el caso se conserva hasta el {vence.strftime('%d/%m/%Y')}.",
    )


@casos_bp.post("/<int:id_caso>/accesos")
@login_required
def compartir(id_caso):
    """Comparte el caso con un miembro o con toda la organización (RF30)."""
    solicitud = validar(SolicitudCompartir, _cuerpo())
    servicio = _servicio()
    usuario = usuario_actual()
    servicio.compartir(id_caso, usuario, solicitud.nivel, solicitud.id_usuario)
    caso, permiso = servicio.detalle(id_caso, usuario)
    return _detalle(servicio, caso, permiso, "El caso fue compartido.")


@casos_bp.patch("/<int:id_caso>/accesos/<int:id_acceso>")
@login_required
def modificar_acceso(id_caso, id_acceso):
    """Cambia el nivel de un acceso (RF31 CA2)."""
    solicitud = validar(SolicitudNivel, _cuerpo())
    servicio = _servicio()
    usuario = usuario_actual()
    servicio.modificar_acceso(id_caso, usuario, id_acceso, solicitud.nivel)
    caso, permiso = servicio.detalle(id_caso, usuario)
    return _detalle(servicio, caso, permiso, "El permiso fue actualizado.")


@casos_bp.delete("/<int:id_caso>/accesos/<int:id_acceso>")
@login_required
def revocar_acceso(id_caso, id_acceso):
    """Revoca un acceso (RF31 CA1)."""
    servicio = _servicio()
    usuario = usuario_actual()
    servicio.revocar_acceso(id_caso, usuario, id_acceso)
    caso, permiso = servicio.detalle(id_caso, usuario)
    return _detalle(servicio, caso, permiso, "El acceso fue revocado.")


@casos_bp.post("/<int:id_caso>/transferencia")
@login_required
def transferir(id_caso):
    """Transfiere la responsabilidad del caso (RF33)."""
    solicitud = validar(SolicitudTransferencia, _cuerpo())
    servicio = _servicio()
    usuario = usuario_actual()
    aplicada = servicio.transferir(
        id_caso, usuario, solicitud.destino, solicitud.conservar_colaboracion
    )
    mensaje = (
        "El caso fue transferido." if aplicada
        else "Enviamos la solicitud: el caso pasa cuando la otra persona la acepte."
    )
    caso, permiso = servicio.detalle(id_caso, usuario)
    return _detalle(servicio, caso, permiso, mensaje)


@casos_bp.delete("/<int:id_caso>/transferencia")
@login_required
def cancelar_transferencia(id_caso):
    """Cancela una transferencia pendiente de un caso personal."""
    servicio = _servicio()
    usuario = usuario_actual()
    servicio.cancelar_transferencia(id_caso, usuario)
    caso, permiso = servicio.detalle(id_caso, usuario)
    return _detalle(servicio, caso, permiso, "La transferencia fue cancelada.")


@casos_bp.post("/<int:id_caso>/transferencia/aceptacion")
@login_required
def aceptar_transferencia(id_caso):
    """Acepta un caso personal transferido (RF33 CA2)."""
    caso = _servicio().responder_transferencia(id_caso, usuario_actual(), aceptar=True)
    return jsonify(
        {"mensaje": f"Ahora sos Responsable del caso {caso.numero}.", "id_caso": caso.id}
    )


@casos_bp.post("/<int:id_caso>/transferencia/rechazo")
@login_required
def rechazar_transferencia(id_caso):
    """Rechaza un caso personal transferido."""
    caso = _servicio().responder_transferencia(id_caso, usuario_actual(), aceptar=False)
    return jsonify({"mensaje": f"Rechazaste el caso {caso.numero}."})
