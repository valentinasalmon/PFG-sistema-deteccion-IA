"""Rutas del perfil propio.

GET   /api/perfil                         Ver mis datos
PATCH /api/perfil                         Editar nombre, apellido, colegio o empresa (RF07)
POST  /api/perfil/contrasenia             Cambiar la contraseña (RF06)
POST  /api/perfil/correo                  Pedir cambio de correo (RF07 CA2)
POST  /api/perfil/correo/confirmacion     Confirmar el correo nuevo con el enlace recibido
POST  /api/perfil/copia                   Pedir una copia de mis datos (RF09)
GET   /api/perfil/copia/<json|pdf>        Descargar la copia con el token recibido
GET   /api/perfil/baja                    Qué falta resolver para eliminar la cuenta (RF08)
DELETE /api/perfil                        Eliminar la cuenta con la contraseña (RF08)
"""
from flask import Blueprint, Response, current_app, jsonify, request
from flask_login import login_required

from app.esquemas import validar
from app.esquemas.cuentas import (
    SolicitudActualizacionPerfil,
    SolicitudCambioContrasenia,
    SolicitudCambioCorreo,
    SolicitudToken,
    usuario_a_dict,
)
from app.esquemas.datos_personales import SolicitudEliminacionCuenta, situacion_a_dict
from app.seguridad.autenticacion import (
    renovar_sesion,
    terminar_sesion_de_cuenta_eliminada,
    usuario_actual,
)
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_datos_personales, crear_servicio_perfil
from app.utilidades.tiempo import ahora_utc

perfil_bp = Blueprint("perfil", __name__, url_prefix="/api/perfil")


def _servicio():
    return crear_servicio_perfil(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


def _servicio_datos():
    return crear_servicio_datos_personales(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


@perfil_bp.get("")
@login_required
def obtener():
    """Devuelve los datos del perfil propio."""
    return jsonify({"usuario": usuario_a_dict(usuario_actual())})


@perfil_bp.patch("")
@login_required
def actualizar():
    """Actualiza solo los campos enviados. El perfil no puede cambiarse (RF07 CA4)."""
    solicitud = validar(SolicitudActualizacionPerfil, request.get_json(silent=True))
    cambios = solicitud.model_dump(exclude_unset=True)
    usuario = _servicio().actualizar_datos(usuario_actual(), cambios)
    return jsonify(
        {"usuario": usuario_a_dict(usuario), "mensaje": "Tus datos fueron actualizados."}
    )


@perfil_bp.post("/contrasenia")
@login_required
def cambiar_contrasenia():
    """Cambia la contraseña verificando la actual y cierra las demás sesiones (RF06)."""
    solicitud = validar(SolicitudCambioContrasenia, request.get_json(silent=True))
    usuario = _servicio().cambiar_contrasenia(
        usuario_actual(), solicitud.contrasenia_actual, solicitud.contrasenia_nueva
    )
    # Las demás sesiones quedaron cerradas; la actual se mantiene.
    renovar_sesion(usuario)
    return jsonify({"mensaje": "Tu contraseña fue actualizada."})


@perfil_bp.post("/correo")
@login_required
def solicitar_cambio_correo():
    """Envía la confirmación a la dirección nueva y un aviso a la actual (RF07 CA2)."""
    solicitud = validar(SolicitudCambioCorreo, request.get_json(silent=True))
    _servicio().solicitar_cambio_correo(
        usuario_actual(), solicitud.correo_nuevo, solicitud.contrasenia
    )
    return jsonify({"mensaje": "Te enviamos un enlace al correo nuevo para confirmar el cambio."})


@perfil_bp.post("/correo/confirmacion")
def confirmar_cambio_correo():
    """Aplica el cambio de correo. No requiere sesión: el enlace prueba el acceso al correo."""
    solicitud = validar(SolicitudToken, request.get_json(silent=True))
    _servicio().confirmar_cambio_correo(solicitud.token)
    return jsonify({"mensaje": "Tu correo fue actualizado."})


@perfil_bp.post("/copia")
@login_required
def solicitar_copia():
    """Genera los enlaces de descarga de la copia y avisa por correo (RF09 CA1, CA2)."""
    token, vence_en = _servicio_datos().solicitar_copia(usuario_actual())
    return jsonify({
        "enlaces": {
            formato: f"/api/perfil/copia/{formato}?token={token}" for formato in ("json", "pdf")
        },
        "vence_en": vence_en.isoformat(),
        "mensaje": "Tu copia está lista. Los enlaces vencen en 15 minutos.",
    })


@perfil_bp.get("/copia/<any(json, pdf):formato>")
@login_required
def descargar_copia(formato):
    """Entrega la copia como archivo; exige el token vigente y la sesión de la misma persona."""
    contenido, tipo_mime = _servicio_datos().descargar_copia(
        usuario_actual(), request.args.get("token", ""), formato
    )
    nombre = f"mis-datos-{ahora_utc().date().isoformat()}.{formato}"
    return Response(
        contenido, mimetype=tipo_mime,
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Cache-Control": "no-store",
        },
    )


@perfil_bp.get("/baja")
@login_required
def situacion_para_baja():
    """Casos y organizaciones que hay que resolver antes de eliminar la cuenta (RF08 CA1, CA2)."""
    servicio = _servicio_datos()
    situacion = servicio.situacion_para_baja(usuario_actual())
    return jsonify(situacion_a_dict(situacion, servicio.cantidad_de_casos))


@perfil_bp.delete("")
@login_required
def eliminar_cuenta():
    """Elimina la cuenta propia, confirmada con la contraseña, y cierra la sesión (RF08 CA3)."""
    solicitud = validar(SolicitudEliminacionCuenta, request.get_json(silent=True))
    _servicio_datos().eliminar_cuenta(usuario_actual(), solicitud.contrasenia)
    terminar_sesion_de_cuenta_eliminada()
    return jsonify({"mensaje": "Tu cuenta fue eliminada. Te enviamos una confirmación por correo."})
