"""Acceso al registro de auditoría (patrón Repository).

Es la única puerta de escritura del registro y, a propósito, solo permite
agregar entradas: no hay operaciones para modificarlas ni eliminarlas
(RNF06 CA3). La eliminación por antigüedad es de la funcionalidad 015.

Realiza: RNF06 (CA3, CA8).
"""
from app.extensiones import db
from app.modelos.entrada_auditoria import EntradaAuditoria
from app.modelos.usuario import Usuario


class RepositorioAuditoria:
    """Agrega entradas a la transacción en curso y consulta las de un usuario."""

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

    def recientes_de_recursos(self, tipo_recurso, ids_recursos, acciones, resultado, cantidad):
        """Últimas entradas de esos recursos, con el usuario que actuó (panel, RF48 CA2).

        Returns:
            Lista de ``(entrada, usuario o None)``, de la más reciente a la más antigua.
        """
        if not ids_recursos:
            return []
        return (
            db.session.query(EntradaAuditoria, Usuario)
            .outerjoin(Usuario, Usuario.id == EntradaAuditoria.id_usuario)
            .filter(
                EntradaAuditoria.tipo_recurso == tipo_recurso,
                EntradaAuditoria.id_recurso.in_([str(i) for i in ids_recursos]),
                EntradaAuditoria.accion.in_(acciones),
                EntradaAuditoria.resultado == resultado,
            )
            .order_by(EntradaAuditoria.fecha.desc(), EntradaAuditoria.id.desc())
            .limit(cantidad)
            .all()
        )

    def de_usuario(self, id_usuario):
        """Entradas de las acciones del usuario, de la más antigua a la más reciente.

        Se usan para la copia de sus datos personales (RF09).
        """
        return (
            EntradaAuditoria.query.filter_by(id_usuario=id_usuario)
            .order_by(EntradaAuditoria.fecha, EntradaAuditoria.id)
            .all()
        )
