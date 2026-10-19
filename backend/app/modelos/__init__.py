"""Capa de modelos: entidades de dominio mapeadas con SQLAlchemy.

Importar los modelos acá permite que Alembic los detecte al generar migraciones.
"""
from app.modelos.caso import AccesoCaso, Caso
from app.modelos.entrada_auditoria import EntradaAuditoria
from app.modelos.organizacion import Invitacion, Membresia, Organizacion
from app.modelos.usuario import Usuario

__all__ = [
    "AccesoCaso", "Caso", "EntradaAuditoria", "Invitacion", "Membresia", "Organizacion",
    "Usuario",
]
