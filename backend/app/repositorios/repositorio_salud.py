"""Repositorio para verificar el estado de la base de datos.

Realiza: RNF15 (monitoreo de disponibilidad).
"""
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensiones import db


class RepositorioSalud:
    """Consultas técnicas sobre la base de datos, sin datos de negocio."""

    def verificar_conexion(self):
        """Ejecuta una consulta mínima para comprobar que la base responde.

        Returns:
            True si la base de datos respondió; False si hubo un error.
        """
        try:
            db.session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False