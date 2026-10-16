"""Capa de modelos: entidades de dominio mapeadas con SQLAlchemy.

Importar los modelos acá permite que Alembic los detecte al generar migraciones.
"""
from app.modelos.usuario import Usuario

__all__ = ["Usuario"]
