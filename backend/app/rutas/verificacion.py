"""Verificación pública de los informes PDF (funcionalidad 026).

GET /api/verificacion?codigo=<código>   Datos del informe con ese código
GET /api/verificacion?huella=<sha256>   Datos del informe cuyo PDF tiene esa huella

También muestra con qué versión de la plataforma se hizo el análisis y su
sello en Hedera (funcionalidad 029). No requiere sesión: la usa quien recibe
el PDF (un juzgado, un perito, un liquidador). La huella del archivo se calcula en el navegador, así el PDF
nunca se sube al servidor.

Realiza: RF55 (CA3).
"""
from flask import Blueprint, current_app, jsonify, request

from app.esquemas.verificacion import informe_verificado_a_dict
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_informes, crear_servicio_versiones

verificacion_bp = Blueprint("verificacion", __name__, url_prefix="/api/verificacion")


@verificacion_bp.get("")
def verificar():
    """Busca el informe por código o por huella y devuelve sus datos públicos."""
    servicio = crear_servicio_informes(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], origen_de_la_solicitud(),
    )
    informe = servicio.verificar(
        codigo=request.args.get("codigo"), huella=request.args.get("huella")
    )
    commit = (informe.analisis.versiones or {}).get("commit") if informe.analisis else None
    version = crear_servicio_versiones(current_app.config).por_commit(commit)
    return jsonify({"informe": informe_verificado_a_dict(informe, version)})
