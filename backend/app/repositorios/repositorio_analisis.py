"""Acceso a los análisis y sus resultados (patrón Repository).

Realiza: RF38, RF43, RF46.
"""
from app.extensiones import db
from app.modelos.analisis import ESTADOS_EN_CURSO, Analisis, AnalisisImagen, ResultadoCapa
from app.repositorios.base import RepositorioBase


class RepositorioAnalisis(RepositorioBase):
    """Consultas y persistencia de ``Analisis`` y sus resultados."""

    def obtener(self, id_analisis):
        """Devuelve el análisis, o None."""
        return db.session.get(Analisis, id_analisis)

    def de_caso(self, id_caso):
        """Análisis del caso, del más reciente al más antiguo (historial, RN25)."""
        return (
            Analisis.query.filter_by(id_caso=id_caso)
            .order_by(Analisis.creado_en.desc(), Analisis.id.desc())
            .all()
        )

    def claves_de_imagenes_de_casos(self, ids_casos):
        """Claves de las imágenes de los resultados (mapas ELA) de varios casos (RN21)."""
        if not ids_casos:
            return []
        filas = (
            db.session.query(ResultadoCapa.clave_imagen)
            .join(AnalisisImagen, ResultadoCapa.id_analisis_imagen == AnalisisImagen.id)
            .join(Analisis, AnalisisImagen.id_analisis == Analisis.id)
            .filter(Analisis.id_caso.in_(ids_casos), ResultadoCapa.clave_imagen.isnot(None))
            .all()
        )
        return [clave for (clave,) in filas]

    def en_curso_de_casos(self, ids_casos):
        """Análisis en cola o en proceso de varios casos, del más antiguo al más nuevo."""
        if not ids_casos:
            return []
        return (
            Analisis.query.filter(
                Analisis.id_caso.in_(ids_casos), Analisis.estado.in_(ESTADOS_EN_CURSO)
            )
            .order_by(Analisis.creado_en)
            .all()
        )

    def en_curso_de_caso(self, id_caso):
        """El análisis en cola o en proceso del caso, o None (RF38 CA3)."""
        return Analisis.query.filter(
            Analisis.id_caso == id_caso, Analisis.estado.in_(ESTADOS_EN_CURSO)
        ).first()

    def agregar(self, entidad):
        """Suma la entidad a la transacción, sin confirmarla."""
        db.session.add(entidad)
        return entidad

    def descartar(self):
        """Deshace los cambios pendientes, para registrar una falla en limpio."""
        db.session.rollback()
