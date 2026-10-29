"""Rutas del inicio de sesión y del registro con Google (funcionalidad 027).

GET  /api/google/estado      Si el inicio con Google está disponible
GET  /api/google/inicio      Redirige a Google (``?invitacion=<token>`` opcional)
GET  /api/google/retorno     Vuelta desde Google: inicia sesión o pide completar el registro
GET  /api/google/registro    Datos de Google del registro pendiente
POST /api/google/registro    Completa el registro (perfil, institución y Términos) e inicia sesión

``inicio`` y ``retorno`` son navegaciones del navegador, no llamadas de la
API: responden con redirecciones a la interfaz y los errores viajan en
``/iniciar-sesion?google=<código>``.

Realiza: RF52 (CA1 a CA3).
"""
from urllib.parse import urlencode

from flask import Blueprint, current_app, jsonify, redirect, request, session
from flask_wtf.csrf import generate_csrf

from app.esquemas import validar
from app.esquemas.cuentas import SolicitudRegistroGoogle, usuario_a_dict
from app.seguridad.autenticacion import iniciar_sesion
from app.seguridad.origen import origen_de_la_solicitud
from app.servicios.errores import CuentaDesactivada, InicioGoogleRechazado, NoEncontrado
from app.servicios.fabrica import crear_servicio_google

google_bp = Blueprint("google", __name__, url_prefix="/api/google")

CLAVE_FLUJO = "google_flujo"
CLAVE_REGISTRO = "google_registro"


def _servicio():
    return crear_servicio_google(
        current_app.config, current_app.extensions["enviador_correo"], origen_de_la_solicitud()
    )


def _a_la_interfaz(ruta, **parametros):
    """Redirección a una pantalla del frontend."""
    destino = current_app.config["URL_FRONTEND"].rstrip("/") + ruta
    if parametros:
        destino += "?" + urlencode(parametros)
    return redirect(destino)


@google_bp.get("/estado")
def estado():
    """Indica si se muestra el botón "Continuar con Google"."""
    return jsonify({"habilitado": _servicio().habilitado})


@google_bp.get("/inicio")
def inicio():
    """Guarda ``state``, ``nonce`` y el verificador PKCE en la sesión y redirige a Google."""
    try:
        url, flujo = _servicio().preparar_inicio()
    except NoEncontrado:
        return _a_la_interfaz("/iniciar-sesion", google="no_disponible")
    flujo["invitacion"] = (request.args.get("invitacion") or "")[:500] or None
    session[CLAVE_FLUJO] = flujo
    session.pop(CLAVE_REGISTRO, None)
    return redirect(url)


@google_bp.get("/retorno")
def retorno():
    """Inicia sesión, o lleva a completar el registro si el correo no tiene cuenta."""
    servicio = _servicio()
    flujo = session.pop(CLAVE_FLUJO, None)
    try:
        identidad = servicio.obtener_identidad(
            flujo, request.args.get("state"), request.args.get("code"),
            request.args.get("error"),
        )
        usuario = servicio.ingresar(identidad)
    except InicioGoogleRechazado as rechazo:
        return _a_la_interfaz("/iniciar-sesion", google=rechazo.codigo)
    except CuentaDesactivada:
        return _a_la_interfaz("/iniciar-sesion", google="cuenta_desactivada")
    except NoEncontrado:
        return _a_la_interfaz("/iniciar-sesion", google="no_disponible")
    if usuario is None:
        session[CLAVE_REGISTRO] = servicio.datos_pendientes(identidad, flujo.get("invitacion"))
        return _a_la_interfaz("/registro/google")
    iniciar_sesion(usuario)
    return _a_la_interfaz("/")


@google_bp.get("/registro")
def registro_pendiente():
    """Nombre, apellido y correo que informó Google, para completar el registro."""
    pendiente = session.get(CLAVE_REGISTRO)
    if not _servicio().vigente(pendiente):
        raise NoEncontrado(
            "No hay un registro con Google en curso. Volvé a elegir \"Continuar con Google\".",
            codigo="registro_google_vencido",
        )
    return jsonify({
        campo: pendiente.get(campo) for campo in ("nombre", "apellido", "correo", "invitacion")
    })


@google_bp.post("/registro")
def completar_registro():
    """Crea la cuenta con perfil, institución y Términos aceptados, e inicia sesión."""
    solicitud = validar(SolicitudRegistroGoogle, request.get_json(silent=True))
    usuario = _servicio().completar_registro(session.get(CLAVE_REGISTRO), solicitud)
    session.pop(CLAVE_REGISTRO, None)
    iniciar_sesion(usuario)
    return jsonify({"usuario": usuario_a_dict(usuario), "csrf": generate_csrf()}), 201
