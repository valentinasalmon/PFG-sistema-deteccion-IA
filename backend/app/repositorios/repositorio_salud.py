"""Repositorio para verificar el estado de la base de datos.

Realiza: RNF15 (monitoreo de disponibilidad).
"""
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError

from app.extensiones import db
from app.modelos.imagen import Imagen
from app.modelos.informe import Informe
from app.modelos.version_sistema import VersionSistema

# Lo que se sella en Hedera, con la columna de su fecha de creación:
# imágenes (023), informes (026) y versiones desplegadas (029).
MODELOS_SELLADOS = (
    (Imagen, Imagen.cargada_en),
    (Informe, Informe.generado_en),
    (VersionSistema, VersionSistema.desplegada_en),
)


class RepositorioSalud:
    """Consultas técnicas sobre la base de datos, sin datos de negocio."""

    def verificar_conexion(self):
        """Ejecuta una consulta mínima para comprobar que la base responde.

        Returns:
            True si la base de datos respondió; False si hubo un error.
        """
        try:
            db.session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    def resumen_sellos(self, demorado_desde):
        """Cuenta los sellos fallidos y demorados y busca el último confirmado.

        Solo devuelve cantidades y una fecha: ni huellas ni recibos, porque la
        página de estado es pública.

        Args:
            demorado_desde: fecha (UTC, sin zona) antes de la cual un sello
                todavía sin confirmar se considera demorado.

        Returns:
            Diccionario con ``fallidos``, ``demorados`` y ``ultimo`` (datetime o None).
        """
        fallidos = demorados = 0
        ultimo = None
        for modelo, creado_en in MODELOS_SELLADOS:
            fallidos += modelo.query.filter(modelo.sello_estado == "fallido").count()
            demorados += modelo.query.filter(
                modelo.sello_estado.in_(("pendiente", "enviado")),
                creado_en < demorado_desde,
            ).count()
            fecha = db.session.query(func.max(modelo.sello_fecha)).scalar()
            if fecha and (ultimo is None or fecha > ultimo):
                ultimo = fecha
        return {"fallidos": fallidos, "demorados": demorados, "ultimo": ultimo}
