"""Operaciones de transacción comunes a los repositorios.

Realiza: RNF06 (CA8): la acción y su entrada de auditoría se confirman juntas.
"""
from app.extensiones import db


class RepositorioBase:
    """Agregar, quitar y confirmar dentro de la transacción en curso."""

    def preparar(self, entidad):
        """Agrega la entidad a la transacción y le asigna identificador, sin confirmar."""
        db.session.add(entidad)
        db.session.flush()
        return entidad

    def quitar(self, entidad):
        """Marca la entidad para eliminarla al confirmar."""
        db.session.delete(entidad)

    def confirmar(self):
        """Confirma la transacción en curso (la acción y su entrada de auditoría)."""
        db.session.commit()
