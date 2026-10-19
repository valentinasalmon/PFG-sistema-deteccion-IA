"""Fábrica de configuración (patrón Factory).

Traduce el nombre de un entorno en una instancia de su clase de
configuración, ya validada. Agregar un entorno nuevo consiste en crear una
clase en ``entornos.py`` y registrarla en ``ENTORNOS``, sin condicionales
dispersos por el código (constitución, principio 2).
"""
import os

from app.configuracion.entornos import (
    ConfiguracionDesarrollo,
    ConfiguracionProduccion,
    ConfiguracionPruebas,
    ErrorConfiguracion,
)

ENTORNOS = {
    "desarrollo": ConfiguracionDesarrollo,
    "pruebas": ConfiguracionPruebas,
    "produccion": ConfiguracionProduccion,
}
"""Registro de entornos disponibles: nombre -> clase de configuración."""


def obtener_configuracion(nombre_entorno=None):
    """Devuelve la configuración validada del entorno indicado.

    Args:
        nombre_entorno: nombre del entorno. Si se omite, se usa la variable
            de entorno ENTORNO y, en su ausencia, "desarrollo".

    Raises:
        ErrorConfiguracion: si el entorno no existe o faltan variables.
    """
    nombre = nombre_entorno or os.getenv("ENTORNO", "desarrollo")
    clase = ENTORNOS.get(nombre)
    if clase is None:
        raise ErrorConfiguracion(
            f"Entorno desconocido: '{nombre}'. Opciones válidas: {', '.join(ENTORNOS)}"
        )
    configuracion = clase()
    configuracion.validar()
    return configuracion
