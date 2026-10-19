"""Capas de análisis activas, en el orden en que se ejecutan.

Una capa nueva (C2PA en la 009, ELA en la 011, red neuronal en la 012) se
agrega a esta lista sin modificar las existentes (ADR-0006, RNF18).

Realiza: RF39; RNF18 (CA1).
"""
from app.analisis.metadatos import CapaMetadatos


def crear_capas(configuracion):
    """Instancias de las capas activas según la configuración."""
    return [CapaMetadatos(configuracion["RUTA_EXIFTOOL"])]
