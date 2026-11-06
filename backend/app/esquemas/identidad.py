"""Esquemas de la verificación de identidad (funcionalidad 035).

Realiza: RN41.
"""
from typing import Literal

from app.esquemas.cuentas import EsquemaBase


class SolicitudSimulacionIdentidad(EsquemaBase):
    """Resultado elegido en la página de la verificación simulada (CA6)."""

    resultado: Literal["aprobada", "rechazada"]
