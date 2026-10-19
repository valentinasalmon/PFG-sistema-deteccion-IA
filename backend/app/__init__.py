"""Paquete principal del backend.

Expone la fábrica de la aplicación (patrón *Application Factory*): la
aplicación Flask no se crea al importar el paquete, sino al invocar
``crear_app``. Esto permite crear instancias distintas para desarrollo,
pruebas y producción, y evita estado global compartido entre pruebas.

Realiza: RNF17, RNF22.
"""
import os

import redis
from flask import Flask

# Se importan los modelos para que Alembic los detecte al generar migraciones.
from app import modelos  # noqa: F401  pylint: disable=unused-import
from app.comandos import registrar_comandos
from app.configuracion import obtener_configuracion
from app.extensiones import db, migrar, proteccion_csrf, sesiones_servidor
from app.integraciones.almacenamiento import crear_almacenamiento
from app.integraciones.cola import crear_cola
from app.integraciones.correo import crear_enviador
from app.rutas import registrar_rutas
from app.seguridad.autenticacion import configurar_autenticacion

# Carpeta de migraciones de Alembic, ubicada en backend/migraciones (ADR-0008).
DIRECTORIO_MIGRACIONES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migraciones"
)


def crear_app(nombre_entorno=None):
    """Construye y devuelve una aplicación Flask configurada.

    Args:
        nombre_entorno: "desarrollo", "pruebas" o "produccion". Si se omite,
            se toma de la variable de entorno ENTORNO.

    Returns:
        La instancia de Flask lista para usarse.

    Raises:
        ErrorConfiguracion: si el entorno no existe o falta una variable
            obligatoria (por ejemplo, la clave secreta en producción).
    """
    configuracion = obtener_configuracion(nombre_entorno)

    aplicacion = Flask(__name__)
    aplicacion.config.from_object(configuracion)
    if aplicacion.config["SESSION_TYPE"] == "redis":
        aplicacion.config["SESSION_REDIS"] = redis.Redis.from_url(aplicacion.config["URL_REDIS"])

    db.init_app(aplicacion)
    migrar.init_app(aplicacion, db, directory=DIRECTORIO_MIGRACIONES)
    sesiones_servidor.init_app(aplicacion)
    proteccion_csrf.init_app(aplicacion)
    configurar_autenticacion(aplicacion)
    aplicacion.extensions["enviador_correo"] = crear_enviador(aplicacion.config)
    aplicacion.extensions["almacenamiento"] = crear_almacenamiento(aplicacion.config)
    aplicacion.extensions["cola_analisis"] = crear_cola(aplicacion)

    registrar_rutas(aplicacion)
    registrar_comandos(aplicacion)
    return aplicacion
