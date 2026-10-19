"""Acceso a las imágenes de los casos (patrón Repository).

Realiza: RF34 a RF36; RN21.
"""
from app.extensiones import db
from app.modelos.analisis import ESTADO_FINALIZADO, Analisis, AnalisisImagen
from app.modelos.imagen import Imagen
from app.repositorios.base import RepositorioBase


class RepositorioImagenes(RepositorioBase):
    """Consultas y persistencia de ``Imagen``."""

    def obtener(self, id_imagen):
        """Devuelve la imagen, o None."""
        return db.session.get(Imagen, id_imagen)

    def de_caso(self, id_caso):
        """Imágenes del caso en el orden en que se cargaron."""
        return Imagen.query.filter_by(id_caso=id_caso).order_by(Imagen.id).all()

    def cantidad_de_caso(self, id_caso):
        """Cantidad de imágenes del caso, para el límite del plan (RN15)."""
        return Imagen.query.filter_by(id_caso=id_caso).count()

    def por_huella(self, id_caso, huella):
        """La imagen del caso con esa huella, o None (RF34 CA4)."""
        return Imagen.query.filter_by(id_caso=id_caso, huella=huella).first()

    def de_casos(self, ids_casos):
        """Imágenes de varios casos, para borrar sus archivos con ellos (RN21)."""
        if not ids_casos:
            return []
        return Imagen.query.filter(Imagen.id_caso.in_(ids_casos)).all()

    def analizadas(self, ids_imagenes):
        """Ids de las imágenes que ya forman parte de un análisis finalizado (CU27 paso 1)."""
        if not ids_imagenes:
            return set()
        filas = (
            db.session.query(AnalisisImagen.id_imagen)
            .join(Analisis)
            .filter(
                AnalisisImagen.id_imagen.in_(ids_imagenes),
                Analisis.estado == ESTADO_FINALIZADO,
            )
            .distinct()
            .all()
        )
        return {fila[0] for fila in filas}
