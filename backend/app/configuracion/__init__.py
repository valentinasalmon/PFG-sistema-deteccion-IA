"""Configuración de la aplicación por entorno.

Aplica los patrones *Factory* (``obtener_configuracion`` elige la clase) y
*Strategy* (cada entorno es una clase intercambiable con su propio
comportamiento).

Realiza: RNF22.
"""
from app.configuracion.entornos import (
    ConfiguracionBase,
    ConfiguracionDesarrollo,
    ConfiguracionProduccion,
    ConfiguracionPruebas,
    ErrorConfiguracion,
)
from app.configuracion.fabrica import ENTORNOS, obtener_configuracion

__all__ = [
    "ENTORNOS",
    "ConfiguracionBase",
    "ConfiguracionDesarrollo",
    "ConfiguracionProduccion",
    "ConfiguracionPruebas",
    "ErrorConfiguracion",
    "obtener_configuracion",
]
