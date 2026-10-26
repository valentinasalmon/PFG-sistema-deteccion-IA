"""Rutas del Administrador de la plataforma (funcionalidad 021).

GET  /api/administracion/aseguradoras-pendientes                 Aseguradoras por aprobar
POST /api/administracion/organizaciones/<id>/aprobacion          Aprobar (RN38)
POST /api/administracion/organizaciones/<id>/rechazo             Rechazar con motivo (RN38)
GET  /api/administracion/tablero?desde=&hasta=                   Indicadores (RF21, 014)
GET  /api/administracion/usuarios?busqueda=&perfil=&pagina=      Listado de cuentas (RF22)
GET  /api/administracion/organizaciones?busqueda=&tipo=&pagina=  Listado de organizaciones (RF22)
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.administracion import (
    organizacion_de_listado_a_dict,
    rango_de_fechas,
    usuario_de_listado_a_dict,
)
from app.esquemas.organizaciones import SolicitudRechazo, aseguradora_pendiente_a_dict
from app.seguridad.autenticacion import usuario_actual
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_administracion, crear_servicio_organizaciones

administracion_bp = Blueprint("administracion", __name__, url_prefix="/api/administracion")


def _servicio():
    return crear_servicio_organizaciones(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


@administracion_bp.get("/aseguradoras-pendientes")
@login_required
def aseguradoras_pendientes():
    """Aseguradoras que esperan aprobación, con su Referente (CA7 de la 021)."""
    pendientes = _servicio().pendientes_de_aprobacion(usuario_actual())
    return jsonify(
        {"aseguradoras": [aseguradora_pendiente_a_dict(o, r) for o, r in pendientes]}
    )


@administracion_bp.post("/organizaciones/<int:id_organizacion>/aprobacion")
@login_required
def aprobar(id_organizacion):
    """Aprueba una aseguradora pendiente (CA8 de la 021)."""
    organizacion = _servicio().aprobar(usuario_actual(), id_organizacion)
    return jsonify({"mensaje": f"{organizacion.nombre} fue aprobada."})


@administracion_bp.post("/organizaciones/<int:id_organizacion>/rechazo")
@login_required
def rechazar(id_organizacion):
    """Rechaza una aseguradora pendiente indicando el motivo (CA9 de la 021)."""
    solicitud = validar(SolicitudRechazo, request.get_json(silent=True))
    _servicio().rechazar(usuario_actual(), id_organizacion, solicitud.motivo)
    return jsonify({"mensaje": "La aseguradora fue rechazada y se avisó a quien la registró."})


def _pagina():
    try:
        return max(1, int(request.args.get("pagina", 1)))
    except ValueError:
        return 1


def _paginado(clave, filas, total, por_pagina, pagina):
    return jsonify({
        clave: filas, "total": total, "pagina": pagina,
        "paginas": max(1, -(-total // por_pagina)),
    })


@administracion_bp.get("/tablero")
@login_required
def tablero():
    """Indicadores agregados de la plataforma (RF21)."""
    desde, hasta = rango_de_fechas(request.args.get("desde"), request.args.get("hasta"))
    servicio = crear_servicio_administracion(current_app.config)
    return jsonify({"tablero": servicio.tablero(usuario_actual(), desde, hasta)})


@administracion_bp.get("/usuarios")
@login_required
def usuarios():
    """Listado de cuentas, de solo lectura (RF22)."""
    pagina = _pagina()
    filas, total, por_pagina = crear_servicio_administracion(current_app.config).usuarios(
        usuario_actual(), request.args.get("busqueda"), request.args.get("perfil"), pagina
    )
    return _paginado("usuarios", [usuario_de_listado_a_dict(u) for u in filas], total,
                     por_pagina, pagina)


@administracion_bp.get("/organizaciones")
@login_required
def organizaciones():
    """Listado de organizaciones, de solo lectura (RF22)."""
    pagina = _pagina()
    filas, total, por_pagina = crear_servicio_administracion(current_app.config).organizaciones(
        usuario_actual(), request.args.get("busqueda"), request.args.get("tipo"), pagina
    )
    planes = current_app.config["PLANES"]
    return _paginado(
        "organizaciones", [organizacion_de_listado_a_dict(o, m, planes) for o, m in filas],
        total, por_pagina, pagina,
    )
