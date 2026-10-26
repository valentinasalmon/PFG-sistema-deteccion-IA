"""Acceso a las versiones desplegadas de la plataforma (patrón Repository).

Realiza: RF56.
"""
from app.modelos.version_sistema import VersionSistema
from app.repositorios.base import RepositorioBase


class RepositorioVersiones(RepositorioBase):
    """Consultas y persistencia de ``VersionSistema``."""

    def por_commit(self, commit):
        """La versión con ese commit, o None."""
        return VersionSistema.query.filter_by(commit=commit).first()

    def con_sello_en_curso(self, estados):
        """Versiones cuyo sello de tiempo todavía no terminó."""
        return (
            VersionSistema.query.filter(VersionSistema.sello_estado.in_(estados))
            .order_by(VersionSistema.id).all()
        )
