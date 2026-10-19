"""Instancias compartidas de las extensiones de Flask.

Se crean sin aplicación asociada y se vinculan dentro de ``crear_app``
mediante ``init_app``. Tenerlas en un módulo propio evita importaciones
circulares entre la fábrica, los modelos y los repositorios.
"""
import sqlite3

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
"""Acceso a la base de datos mediante SQLAlchemy (ORM)."""

migrar = Migrate()
"""Gestor de migraciones de esquema (Alembic), ADR-0008."""

gestor_sesiones = LoginManager()
"""Autenticación con Flask-Login: qué usuario corresponde a cada sesión (ADR-0003)."""

sesiones_servidor = Session()
"""Sesiones guardadas del lado del servidor (Redis), ADR-0003."""

proteccion_csrf = CSRFProtect()
"""Protección contra falsificación de solicitudes entre sitios (RNF02 CA3)."""


@event.listens_for(Engine, "connect")
def _activar_claves_foraneas_en_sqlite(conexion, _registro):
    """Activa las claves foráneas en SQLite (pruebas).

    SQLite no las aplica por defecto; sin esto, las pruebas no verían el
    ``ON DELETE CASCADE`` ni el ``ON DELETE SET NULL`` que PostgreSQL aplica,
    por ejemplo, al anonimizar la auditoría de una cuenta eliminada (RN34).
    """
    if isinstance(conexion, sqlite3.Connection):
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
