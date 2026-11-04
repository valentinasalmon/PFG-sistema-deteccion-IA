"""Acceso a las verificaciones de identidad (funcionalidad 035, patrón Repository).

Realiza: RN41.
"""
from app.modelos.verificacion_identidad import VerificacionIdentidad
from app.repositorios.base import RepositorioBase


class RepositorioVerificaciones(RepositorioBase):
    """Consultas y persistencia de ``VerificacionIdentidad``."""

    def por_huella(self, huella_token):
        """La verificación con esa huella de token, o None."""
        return VerificacionIdentidad.query.filter_by(huella_token=huella_token).first()

    def ultima_de(self, id_organizacion):
        """La verificación más reciente de la organización, o None."""
        return (
            VerificacionIdentidad.query.filter_by(id_organizacion=id_organizacion)
            .order_by(VerificacionIdentidad.creada_en.desc(), VerificacionIdentidad.id.desc())
            .first()
        )

    def ultimas_de(self, ids_organizaciones):
        """La verificación más reciente de cada organización pedida, como diccionario por id."""
        resultado = {}
        if not ids_organizaciones:
            return resultado
        verificaciones = (
            VerificacionIdentidad.query
            .filter(VerificacionIdentidad.id_organizacion.in_(ids_organizaciones))
            .order_by(VerificacionIdentidad.creada_en, VerificacionIdentidad.id)
            .all()
        )
        for verificacion in verificaciones:
            resultado[verificacion.id_organizacion] = verificacion
        return resultado
