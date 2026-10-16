"""Catálogo de aseguradoras habilitadas por la Superintendencia de Seguros.

Lee ``recursos/catalogos/aseguradoras_ssn.csv`` una sola vez y lo mantiene en
memoria: son 192 filas que solo cambian cuando se reemplaza el archivo (ver el
README de esa carpeta).

Realiza: RN35, RN36 (CP-18).
"""
import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ARCHIVO_CATALOGO = (
    Path(__file__).resolve().parents[2] / "recursos" / "catalogos" / "aseguradoras_ssn.csv"
)


@dataclass(frozen=True)
class Aseguradora:
    """Una aseguradora del catálogo de la SSN."""

    id: int  # pylint: disable=invalid-name
    denominacion: str
    cuit: str
    actividad: str


@lru_cache(maxsize=1)
def _leer(ruta):
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return tuple(
            Aseguradora(
                id=int(fila["cia_id"]),
                denominacion=fila["cia_denominacion"],
                cuit=fila["cia_cuit"],
                actividad=fila["cia_actividad_principal"],
            )
            for fila in csv.DictReader(archivo)
        )


class CatalogoAseguradoras:
    """Consulta del catálogo, ordenado por denominación."""

    def __init__(self, ruta=ARCHIVO_CATALOGO):
        self.ruta = str(ruta)

    def todas(self):
        """Todas las aseguradoras del catálogo."""
        return _leer(self.ruta)

    def obtener(self, id_aseguradora):
        """La aseguradora con ese número de registro de la SSN, o None."""
        return next((a for a in self.todas() if a.id == id_aseguradora), None)
