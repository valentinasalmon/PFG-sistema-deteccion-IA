"""Traducción de errores a respuestas JSON.

Los servicios lanzan excepciones de dominio sin saber de HTTP; acá se
convierten en el código de estado y el cuerpo JSON que espera el frontend:
``{"mensaje": "...", "codigo": "...", "errores": {...}}``.
"""
from flask import jsonify
from flask_wtf.csrf import CSRFError

from app.servicios.errores import (
    ConflictoDatos,
    CredencialesInvalidas,
    CuentaNoVerificada,
    ErrorDominio,
    ErrorValidacion,
    TokenInvalido,
)

CODIGOS_HTTP = {
    ErrorValidacion: 400,
    TokenInvalido: 400,
    CredencialesInvalidas: 401,
    CuentaNoVerificada: 403,
    ConflictoDatos: 409,
}


def _respuesta(mensaje, codigo, estado, errores=None):
    cuerpo = {"mensaje": mensaje, "codigo": codigo}
    if errores:
        cuerpo["errores"] = errores
    return jsonify(cuerpo), estado


def _error_dominio(error):
    estado = CODIGOS_HTTP.get(type(error), 400)
    return _respuesta(error.mensaje, error.codigo, estado, error.errores)


def _error_csrf(_error):
    return _respuesta(
        "La sesión de seguridad expiró. Volvé a intentarlo.", "csrf_invalido", 400
    )


def _no_encontrado(_error):
    return _respuesta("El recurso solicitado no existe.", "no_encontrado", 404)


def _metodo_no_permitido(_error):
    return _respuesta("Operación no permitida.", "metodo_no_permitido", 405)


def registrar_manejadores(aplicacion):
    """Registra los manejadores de errores en la aplicación."""
    aplicacion.register_error_handler(ErrorDominio, _error_dominio)
    aplicacion.register_error_handler(CSRFError, _error_csrf)
    aplicacion.register_error_handler(404, _no_encontrado)
    aplicacion.register_error_handler(405, _metodo_no_permitido)
