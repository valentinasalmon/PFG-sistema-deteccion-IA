"""Acceso a los informes PDF (patrón Repository).

Realiza: RF44, RF45; RN21.
"""
from app.extensiones import db
from app.modelos.informe import Informe
from app.repositorios.base import RepositorioBase


class RepositorioInformes(RepositorioBase):
    """Consultas y persistencia de ``Informe``."""

    def obtener(self, id_informe):
        """Devuelve el informe, o None."""
        return db.session.get(Informe, id_informe)

    def de_caso(self, id_caso):
        """Informes del caso, del más reciente al más antiguo (RF45 CA1)."""
        return (
            Informe.query.filter_by(id_caso=id_caso)
            .order_by(Informe.generado_en.desc(), Informe.id.desc())
            .all()
        )

    def de_casos(self, ids_casos):
        """Informes de varios casos, para borrar sus archivos con ellos (RN21)."""
        if not ids_casos:
            return []
        return Informe.query.filter(Informe.id_caso.in_(ids_casos)).all()

    def agregar(self, informe):
        """Suma el informe a la transacción, sin confirmarla."""
        db.session.add(informe)
        return informe
