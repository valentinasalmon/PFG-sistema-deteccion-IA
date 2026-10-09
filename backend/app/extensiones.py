"""Instancias compartidas de las extensiones de Flask.

Se crean sin aplicación asociada y se vinculan dentro de ``crear_app``
mediante ``init_app``. Tenerlas en un módulo propio evita importaciones
circulares entre la fábrica, los modelos y los repositorios.
"""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
"""Acceso a la base de datos mediante SQLAlchemy (ORM)."""

migrar = Migrate()
"""Gestor de migraciones de esquema (Alembic), ADR-0008."""
