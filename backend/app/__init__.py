"""Paquete principal del backend.

Expone la fábrica de la aplicación (patrón *Application Factory*): la
aplicación Flask no se crea al importar el paquete, sino al invocar
``crear_app``. Esto permite crear instancias distintas para desarrollo,
pruebas y producción, y evita estado global compartido entre pruebas.

Realiza: RNF17, RNF22.
"""
import os

from flask import Flask

from app.configuracion import obtener_configuracion
from app.extensiones import db, migrar
from app.rutas import registrar_rutas

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

    db.init_app(aplicacion)
    migrar.init_app(aplicacion, db, directory=DIRECTORIO_MIGRACIONES)

    registrar_rutas(aplicacion)
    return aplicacion