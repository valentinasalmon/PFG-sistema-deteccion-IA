"""Acceso al registro de auditoría (patrón Repository).

Es la única puerta de escritura del registro y, a propósito, solo permite
agregar entradas: no hay operaciones para modificarlas ni eliminarlas
(RNF06 CA3). La eliminación por antigüedad es de la funcionalidad 015.

Realiza: RNF06 (CA3, CA8).
"""
from app.extensiones import db


class RepositorioAuditoria:
    """Agrega entradas a la transacción en curso."""

    def agregar(self, entrada):
        """Suma la entrada a la transacción en curso, sin confirmarla.

        Así la entrada se confirma junto con la acción que registra: si una
        de las dos falla, no se guarda ninguna (RNF06 CA8).
        """
        db.session.add(entrada)
        return entrada

    def confirmar(self):
        """Confirma la transacción en curso.

        Se usa cuando la acción no cambió otros datos, por ejemplo un intento
        rechazado, y la entrada debe guardarse antes de informar el error.
        """
        db.session.commit()
