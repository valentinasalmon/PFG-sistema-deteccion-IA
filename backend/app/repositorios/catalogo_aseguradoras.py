"""Catálogo de aseguradoras habilitadas por la Superintendencia de Seguros.

Hay dos copias del mismo archivo:

- la del repositorio (``recursos/catalogos/aseguradoras_ssn.csv``), que viaja con
  cada versión y sirve de punto de partida;
- la actualizada (052), que la tarea semanal baja de los datos abiertos de la
  SSN y guarda en ``CARPETA_CATALOGOS``, fuera de la carpeta de la versión, así
  no se pierde en cada despliegue.

Se usa la actualizada si existe. El archivo se lee una vez y se vuelve a leer
solo si cambió (por la fecha de modificación), así todos los procesos ven la
versión nueva sin reiniciarse.

Realiza: RN36, RN37 (CP-18); 052.
"""
import csv
import json
import os
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ARCHIVO_CATALOGO = (
    Path(__file__).resolve().parents[2] / "recursos" / "catalogos" / "aseguradoras_ssn.csv"
)
NOMBRE_ARCHIVO = "aseguradoras_ssn.csv"
NOMBRE_METADATOS = "aseguradoras_ssn.json"
COLUMNAS = ("cia_id", "cia_denominacion", "cia_cuit", "cia_actividad_principal")


@dataclass(frozen=True)
class Aseguradora:
    """Una aseguradora del catálogo de la SSN."""

    id: int  # pylint: disable=invalid-name
    denominacion: str
    cuit: str
    actividad: str


@lru_cache(maxsize=4)
def _leer(ruta, _modificado):
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


def _escribir_atomico(ruta, texto):
    """Escribe en un temporal y lo renombra: nadie lee nunca un archivo a medias."""
    descriptor, temporal = tempfile.mkstemp(dir=ruta.parent, prefix=".tmp-")
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as archivo:
        archivo.write(texto)
    os.replace(temporal, ruta)


class CatalogoAseguradoras:
    """Consulta y actualización del catálogo, ordenado por denominación."""

    def __init__(self, ruta=ARCHIVO_CATALOGO, carpeta_actualizada=None):
        self.ruta_base = Path(ruta)
        self.carpeta = Path(carpeta_actualizada) if carpeta_actualizada else None

    def _ruta_vigente(self):
        if self.carpeta and (self.carpeta / NOMBRE_ARCHIVO).exists():
            return self.carpeta / NOMBRE_ARCHIVO
        return self.ruta_base

    def todas(self):
        """Todas las aseguradoras del catálogo vigente."""
        ruta = self._ruta_vigente()
        return _leer(str(ruta), ruta.stat().st_mtime_ns)

    def obtener(self, id_aseguradora):
        """La aseguradora con ese número de registro de la SSN, o None."""
        return next((a for a in self.todas() if a.id == id_aseguradora), None)

    def metadatos(self):
        """De dónde y cuándo es el catálogo vigente (para ``/estado``)."""
        if self.carpeta and (self.carpeta / NOMBRE_METADATOS).exists():
            with open(self.carpeta / NOMBRE_METADATOS, encoding="utf-8") as archivo:
                return {**json.load(archivo), "total": len(self.todas())}
        return {"origen": "repositorio", "total": len(self.todas())}

    def guardar(self, aseguradoras, metadatos):
        """Guarda una versión nueva del catálogo en la carpeta de la copia actualizada."""
        if not self.carpeta:
            raise RuntimeError("No hay carpeta para guardar el catálogo (CARPETA_CATALOGOS).")
        self.carpeta.mkdir(parents=True, exist_ok=True)
        with tempfile.SpooledTemporaryFile(mode="w+", newline="", encoding="utf-8") as memoria:
            escritor = csv.writer(memoria, lineterminator="\n")
            escritor.writerow(COLUMNAS)
            for aseguradora in sorted(aseguradoras, key=lambda a: a.denominacion):
                escritor.writerow((aseguradora.id, aseguradora.denominacion, aseguradora.cuit,
                                   aseguradora.actividad))
            memoria.seek(0)
            filas = memoria.read()
        _escribir_atomico(self.carpeta / NOMBRE_ARCHIVO, filas)
        _escribir_atomico(
            self.carpeta / NOMBRE_METADATOS,
            json.dumps({**metadatos, "origen": "datos_abiertos"}, ensure_ascii=False, indent=2),
        )
