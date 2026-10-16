"""Instancias compartidas de las extensiones de Flask.

Se crean sin aplicación asociada y se vinculan dentro de ``crear_app``
mediante ``init_app``. Tenerlas en un módulo propio evita importaciones
circulares entre la fábrica, los modelos y los repositorios.
"""
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

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
