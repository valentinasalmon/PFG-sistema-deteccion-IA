"""Manifiesto de imágenes: la tabla que identifica cada conjunto de datos.

Las imágenes no se suben al repositorio (CA21); lo que se versiona es el
manifiesto, que lista cada imagen con su origen, clase, generador, partición
y huella SHA-256. La huella del manifiesto completo identifica de forma
única la versión del conjunto y queda registrada en la ficha del modelo.

Realiza: RNF24 CA2, RN29; CA3 de la funcionalidad 010.
"""

import csv
import hashlib
from dataclasses import asdict, dataclass, fields
from pathlib import Path

CLASE_REAL = 0
CLASE_SINTETICA = 1

PARTICIONES = ("entrenamiento", "validacion", "prueba", "no_visto", "sin_asignar")
VARIANTES = ("original", "whatsapp", "captura", "editada")


class ErrorManifiesto(Exception):
    """El manifiesto no existe, tiene columnas faltantes o valores inválidos."""


@dataclass(frozen=True)
class RegistroImagen:
    """Una imagen del manifiesto.

    ``ruta_relativa`` es relativa a la carpeta del conjunto, para que el
    manifiesto sirva igual en Kaggle, en la integración continua o en una
    computadora local.
    """

    huella_sha256: str
    ruta_relativa: str
    clase: int
    fuente: str
    generador: str
    particion: str = "sin_asignar"
    variante: str = "original"

    def __post_init__(self) -> None:
        if self.clase not in (CLASE_REAL, CLASE_SINTETICA):
            raise ErrorManifiesto(f"clase inválida {self.clase!r} en {self.ruta_relativa}")
        if self.particion not in PARTICIONES:
            raise ErrorManifiesto(f"partición inválida {self.particion!r} en {self.ruta_relativa}")
        if self.variante not in VARIANTES:
            raise ErrorManifiesto(f"variante inválida {self.variante!r} en {self.ruta_relativa}")


COLUMNAS = tuple(campo.name for campo in fields(RegistroImagen))


def huella_archivo(ruta: Path) -> str:
    """Calcula la huella SHA-256 de un archivo leyéndolo por bloques."""
    calculo = hashlib.sha256()
    with Path(ruta).open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1 << 20), b""):
            calculo.update(bloque)
    return calculo.hexdigest()


def _ordenar(registros: list[RegistroImagen]) -> list[RegistroImagen]:
    """Orden canónico: el mismo conjunto siempre se escribe igual."""
    return sorted(registros, key=lambda registro: (registro.ruta_relativa, registro.huella_sha256))


def escribir_manifiesto(registros: list[RegistroImagen], ruta: Path) -> Path:
    """Escribe el manifiesto como CSV en orden canónico y devuelve la ruta."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, lineterminator="\n")
        escritor.writeheader()
        for registro in _ordenar(registros):
            escritor.writerow(asdict(registro))
    return ruta


def leer_manifiesto(ruta: Path) -> list[RegistroImagen]:
    """Lee un manifiesto CSV y valida cada fila."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorManifiesto(f"no existe el manifiesto {ruta}")
    with ruta.open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        faltantes = set(COLUMNAS) - set(lector.fieldnames or [])
        if faltantes:
            raise ErrorManifiesto(f"al manifiesto {ruta} le faltan columnas: {sorted(faltantes)}")
        registros = []
        for numero, fila in enumerate(lector, start=2):
            try:
                fila["clase"] = int(fila["clase"])
            except ValueError as error:
                raise ErrorManifiesto(f"clase no numérica en la línea {numero}") from error
            registros.append(RegistroImagen(**{columna: fila[columna] for columna in COLUMNAS}))
    return registros


def huella_manifiesto(registros: list[RegistroImagen]) -> str:
    """Huella SHA-256 del contenido del manifiesto, independiente del orden.

    Dos manifiestos con las mismas filas tienen la misma huella aunque se
    hayan escrito en otro orden; cambiar cualquier valor la modifica.
    """
    calculo = hashlib.sha256()
    calculo.update(",".join(COLUMNAS).encode("utf-8"))
    for registro in _ordenar(registros):
        linea = "\n" + ",".join(str(valor) for valor in asdict(registro).values())
        calculo.update(linea.encode("utf-8"))
    return calculo.hexdigest()
