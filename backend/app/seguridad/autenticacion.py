"""Integración de Flask-Login con las sesiones del servidor.

- Recupera el usuario de cada solicitud a partir de la sesión.
- Responde 401 en JSON cuando falta iniciar sesión (CA22).
- Cierra la sesión que superó la duración máxima, aunque haya actividad (CA12),
  y registra el cierre en la auditoría (CA6 de la 003).
- Regenera el identificador de sesión al iniciar sesión (RNF01 CA6).

Realiza: RF03, RF04; RNF01 (CA4, CA6); RNF06.
"""
from datetime import datetime

from flask import current_app, jsonify, session
from flask_login import current_user, login_user, logout_user

from app.extensiones import gestor_sesiones
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.fabrica import crear_servicio_sesion
from app.servicios.servicio_sesion import (
    MOTIVO_CIERRE_DURACION_MAXIMA,
    MOTIVO_CIERRE_MANUAL,
)
from app.utilidades.tiempo import ahora_utc

CLAVE_INICIO_SESION = "inicio_sesion"


def _cargar_usuario(identificador):
    servicio = crear_servicio_sesion(current_app.config, current_app.extensions["enviador_correo"])
    return servicio.obtener_usuario_de_sesion(identificador)


def _sin_sesion():
    return jsonify({"mensaje": "Tenés que iniciar sesión.", "codigo": "sesion_requerida"}), 401


def _controlar_duracion_maxima():
    """Cierra la sesión si se superó la duración máxima configurada (CA12)."""
    if not current_user.is_authenticated:
        return
    inicio = session.get(CLAVE_INICIO_SESION)
    maximo = current_app.config["DURACION_MAXIMA_SESION"]
    if inicio is None or ahora_utc() - datetime.fromisoformat(inicio) > maximo:
        cerrar_sesion(MOTIVO_CIERRE_DURACION_MAXIMA)


def configurar_autenticacion(aplicacion):
    """Registra Flask-Login y el control de duración máxima en la aplicación."""
    gestor_sesiones.init_app(aplicacion)
    gestor_sesiones.user_loader(_cargar_usuario)
    gestor_sesiones.unauthorized_handler(_sin_sesion)
    aplicacion.before_request(_controlar_duracion_maxima)


def usuario_actual():
    """Devuelve el usuario de la sesión como objeto real del modelo.

    ``current_user`` es un intermediario (*proxy*) de Flask-Login; los
    servicios reciben el objeto real para no depender de Flask.
    """
    return current_user._get_current_object()  # pylint: disable=protected-access


def iniciar_sesion(usuario):
    """Abre la sesión del usuario con un identificador de sesión nuevo."""
    current_app.session_interface.regenerate(session)
    login_user(usuario)
    session[CLAVE_INICIO_SESION] = ahora_utc().isoformat()


def renovar_sesion(usuario):
    """Vuelve a asociar la sesión actual al usuario tras cambiar su versión de sesión.

    Conserva la hora de inicio, así el cambio de contraseña no extiende la
    duración máxima de la sesión (CA12).
    """
    inicio = session.get(CLAVE_INICIO_SESION)
    current_app.session_interface.regenerate(session)
    login_user(usuario)
    session[CLAVE_INICIO_SESION] = inicio


def cerrar_sesion(motivo=MOTIVO_CIERRE_MANUAL):
    """Registra el cierre en la auditoría, cierra la sesión y la borra del servidor (CA11).

    El registro va primero: si no puede guardarse, la sesión no se cierra y
    la persona recibe un error genérico (RNF06 CA8).
    """
    servicio = crear_servicio_sesion(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )
    servicio.registrar_cierre(usuario_actual(), motivo)
    logout_user()
    session.clear()


def terminar_sesion_de_cuenta_eliminada():
    """Cierra la sesión de una cuenta que acaba de eliminarse (RF08 CA3).

    No registra el cierre: la eliminación ya quedó en la auditoría. Las demás
    sesiones de la cuenta dejan de valer solas, porque la cuenta ya no existe.
    """
    logout_user()
    session.clear()
