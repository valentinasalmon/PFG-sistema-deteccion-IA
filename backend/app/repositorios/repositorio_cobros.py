"""Acceso a los cobros del plan de las organizaciones (patrón Repository).

Realiza: RF20; CP-34.
"""
from app.modelos.cobro import COBRO_ACREDITADO, COBRO_PENDIENTE, Cobro
from app.repositorios.base import RepositorioBase


class RepositorioCobros(RepositorioBase):
    """Consultas y persistencia de ``Cobro``."""

    def por_huella(self, huella_token):
        """El cobro con esa huella de token, o None."""
        return Cobro.query.filter_by(huella_token=huella_token).first()

    def existe_referencia(self, referencia):
        """True si ya hay un cobro con esa referencia."""
        return Cobro.query.filter_by(referencia=referencia).first() is not None

    def pendientes_de(self, id_organizacion):
        """Cobros todavía sin acreditar de la organización."""
        return Cobro.query.filter_by(
            id_organizacion=id_organizacion, estado=COBRO_PENDIENTE
        ).all()

    def acreditados_de(self, id_organizacion):
        """Cobros acreditados de la organización (los que se devuelven al rechazarla)."""
        return Cobro.query.filter_by(
            id_organizacion=id_organizacion, estado=COBRO_ACREDITADO
        ).all()
