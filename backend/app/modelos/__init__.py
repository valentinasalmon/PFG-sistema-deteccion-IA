"""Capa de modelos: entidades de dominio mapeadas con SQLAlchemy.

Importar los modelos acá permite que Alembic los detecte al generar migraciones.
"""
from app.modelos.analisis import Analisis, AnalisisImagen, Anomalia, ResultadoCapa
from app.modelos.caso import AccesoCaso, Caso
from app.modelos.entrada_auditoria import EntradaAuditoria
from app.modelos.imagen import Imagen
from app.modelos.informe import Informe
from app.modelos.organizacion import Invitacion, Membresia, Organizacion
from app.modelos.usuario import Usuario

__all__ = [
    "AccesoCaso", "Analisis", "AnalisisImagen", "Anomalia", "Caso", "EntradaAuditoria",
    "Imagen", "Informe", "Invitacion", "Membresia", "Organizacion", "ResultadoCapa", "Usuario",
]
