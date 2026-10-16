"""Traducción de errores a respuestas JSON.

Los servicios lanzan excepciones de dominio sin saber de HTTP; acá se
convierten en el código de estado y el cuerpo JSON que espera el frontend:
``{"mensaje": "...", "codigo": "...", "errores": {...}}``.
"""
from flask import current_app, jsonify
from flask_wtf.csrf import CSRFError
from sqlalchemy.exc import SQLAlchemyError

from app.extensiones import db

from app.servicios.errores import (
    AccesoDenegado,
    ConflictoDatos,
    CredencialesInvalidas,
    CuentaDesactivada,
    CuentaNoVerificada,
    ErrorDominio,
    ErrorValidacion,
    NoEncontrado,
    TokenInvalido,
)

CODIGOS_HTTP = {
    ErrorValidacion: 400,
    TokenInvalido: 400,
    CredencialesInvalidas: 401,
    CuentaNoVerificada: 403,
    CuentaDesactivada: 403,
    AccesoDenegado: 403,
    NoEncontrado: 404,
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


def _error_base_de_datos(error):
    """Deshace la transacción y responde con un mensaje genérico.

    Si una acción o su entrada de auditoría no pudieron guardarse, no se
    aplica ninguna de las dos (RNF06 CA8) y no se exponen detalles internos.
    """
    db.session.rollback()
    current_app.logger.exception("Error de base de datos: %s", error)
    return _respuesta(
        "Ocurrió un error inesperado. Intentá de nuevo.", "error_interno", 500
    )


def registrar_manejadores(aplicacion):
    """Registra los manejadores de errores en la aplicación."""
    aplicacion.register_error_handler(ErrorDominio, _error_dominio)
    aplicacion.register_error_handler(CSRFError, _error_csrf)
    aplicacion.register_error_handler(SQLAlchemyError, _error_base_de_datos)
    aplicacion.register_error_handler(404, _no_encontrado)
    aplicacion.register_error_handler(405, _metodo_no_permitido)
