"""Acceso a los enlaces de carga desde el celular (patrón Repository).

Realiza: RF53 (CA2).
"""
from app.modelos.enlace_carga import EnlaceCarga
from app.repositorios.base import RepositorioBase


class RepositorioEnlacesCarga(RepositorioBase):
    """Consultas y persistencia de ``EnlaceCarga``."""

    def por_huella(self, huella_token):
        """El enlace con esa huella de token, o None."""
        return EnlaceCarga.query.filter_by(huella_token=huella_token).first()

    def sin_cancelar(self, id_caso, id_usuario):
        """Enlaces del usuario para el caso que todavía no se cancelaron."""
        return EnlaceCarga.query.filter_by(
            id_caso=id_caso, id_usuario=id_usuario, revocado_en=None
        ).all()
