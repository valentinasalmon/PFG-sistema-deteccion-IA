"""Esquemas de la copia de datos personales y de la eliminación de la cuenta.

Realiza: RF08, RF09; RNF04 (CA1).
"""
from app.esquemas.casos import NOMBRES_ESTADO
from app.esquemas.cuentas import Contrasenia, EsquemaBase


class SolicitudEliminacionCuenta(EsquemaBase):
    """Confirmación de la baja con la contraseña (RF08 CA3)."""

    contrasenia: Contrasenia


def situacion_a_dict(situacion, cantidad_de_casos):
    """Lo que la persona tiene que resolver antes de eliminar la cuenta (RF08 CA1, CA2).

    Args:
        cantidad_de_casos: función que devuelve cuántos casos tiene una organización.
    """
    return {
        "casos": [
            {
                "id": caso.id,
                "numero": caso.numero,
                "estado_nombre": NOMBRES_ESTADO[caso.estado],
                "espacio": "Personal" if caso.es_personal else caso.organizacion.nombre,
            }
            for caso in situacion["casos"]
        ],
        "referente_de": [
            {"id": organizacion.id, "nombre": organizacion.nombre}
            for organizacion in situacion["referente_de"]
        ],
        "a_eliminar": [
            {
                "id": organizacion.id,
                "nombre": organizacion.nombre,
                "cantidad_casos": cantidad_de_casos(organizacion),
            }
            for organizacion in situacion["a_eliminar"]
        ],
        "puede_eliminar": not situacion["casos"] and not situacion["referente_de"],
    }
