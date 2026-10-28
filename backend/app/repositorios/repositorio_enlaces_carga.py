"""Acceso a los enlaces de carga sin sesión (patrón Repository).

Realiza: RF53 (CA2); CP-32.
"""
from app.extensiones import db
from app.modelos.enlace_carga import TIPO_CELULAR, TIPO_PERSONA_AFECTADA, EnlaceCarga
from app.repositorios.base import RepositorioBase


class RepositorioEnlacesCarga(RepositorioBase):
    """Consultas y persistencia de ``EnlaceCarga``."""

    def por_huella(self, huella_token):
        """El enlace con esa huella de token, o None."""
        return EnlaceCarga.query.filter_by(huella_token=huella_token).first()

    def obtener(self, id_enlace):
        """El enlace con ese identificador, o None."""
        return db.session.get(EnlaceCarga, id_enlace)

    def sin_cancelar(self, id_caso, id_usuario):
        """Enlaces del celular del usuario para el caso que todavía no se cancelaron."""
        return EnlaceCarga.query.filter_by(
            id_caso=id_caso, id_usuario=id_usuario, revocado_en=None, tipo=TIPO_CELULAR
        ).all()

    def vigentes_para_persona_afectada(self, id_caso, ahora):
        """Enlaces para la persona afectada del caso que no vencieron ni se anularon (028)."""
        return EnlaceCarga.query.filter(
            EnlaceCarga.id_caso == id_caso,
            EnlaceCarga.tipo == TIPO_PERSONA_AFECTADA,
            EnlaceCarga.revocado_en.is_(None),
            EnlaceCarga.vence_en > ahora,
        ).order_by(EnlaceCarga.creado_en.desc()).all()
