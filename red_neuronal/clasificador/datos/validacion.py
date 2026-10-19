"""Validación automática de un conjunto de datos antes de entrenar.

Si alguna verificación falla, el pipeline se detiene (CA4): es mucho más
barato descubrir una imagen corrupta, un duplicado o una fuga entre
particiones acá que después de horas de GPU. Todas las verificaciones se
ejecutan siempre y los errores se informan juntos.

Realiza: CA4 y CA6 de la funcionalidad 010.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from clasificador.datos.manifiesto import (
    CLASE_REAL,
    CLASE_SINTETICA,
    RegistroImagen,
    huella_archivo,
)

# Particiones donde el modelo aprende o se ajusta: un generador reservado
# como "no visto" nunca puede aparecer en ellas.
_PARTICIONES_DE_AJUSTE = ("entrenamiento", "validacion")
# Particiones que deben estar balanceadas entre clases.
_PARTICIONES_BALANCEADAS = ("entrenamiento", "validacion", "prueba")


class ErrorValidacionDatos(Exception):
    """El conjunto de datos no pasó la validación."""


@dataclass(frozen=True)
class ResultadoValidacion:
    """Resultado de validar un manifiesto: errores y conteos para el informe."""

    errores: list[str] = field(default_factory=list)
    resumen: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def es_valido(self) -> bool:
        """Verdadero si no se encontró ningún error."""
        return not self.errores


def _verificar_imagenes(registros: list[RegistroImagen], raiz: Path) -> list[str]:
    """Comprueba que cada imagen exista, se pueda abrir y conserve su huella."""
    errores = []
    for registro in registros:
        ruta = raiz / registro.ruta_relativa
        if not ruta.is_file():
            errores.append(f"imagen inexistente: {registro.ruta_relativa}")
            continue
        try:
            with Image.open(ruta) as imagen:
                imagen.verify()
        except (UnidentifiedImageError, OSError, SyntaxError):
            errores.append(f"imagen corrupta: {registro.ruta_relativa}")
            continue
        if huella_archivo(ruta) != registro.huella_sha256:
            errores.append(f"la huella no coincide (archivo modificado): {registro.ruta_relativa}")
    return errores


def _verificar_duplicados(registros: list[RegistroImagen]) -> list[str]:
    """Detecta imágenes repetidas y fugas entre particiones.

    Una misma imagen en entrenamiento y en prueba infla las métricas: el
    modelo la "recuerda" en lugar de generalizar.
    """
    errores = []
    por_huella: dict[str, list[RegistroImagen]] = defaultdict(list)
    for registro in registros:
        por_huella[registro.huella_sha256].append(registro)
    for huella, repetidos in por_huella.items():
        if len(repetidos) < 2:
            continue
        particiones = sorted({registro.particion for registro in repetidos})
        rutas = ", ".join(registro.ruta_relativa for registro in repetidos)
        if len(particiones) > 1:
            errores.append(
                f"solapamiento entre particiones {particiones} (huella {huella[:12]}): {rutas}"
            )
        else:
            errores.append(f"imagen duplicada (huella {huella[:12]}): {rutas}")
    return errores


def _verificar_reservados(
    registros: list[RegistroImagen], generadores_reservados: list[str]
) -> list[str]:
    """Un generador reservado como no visto no puede usarse para ajustar."""
    reservados = set(generadores_reservados)
    filtrados = Counter(
        (registro.generador, registro.particion)
        for registro in registros
        if registro.generador in reservados and registro.particion in _PARTICIONES_DE_AJUSTE
    )
    return [
        f"el generador reservado '{generador}' aparece {cantidad} veces en '{particion}'"
        for (generador, particion), cantidad in sorted(filtrados.items())
    ]


def _verificar_balance(registros: list[RegistroImagen], tolerancia: float) -> list[str]:
    """Las particiones de ajuste y prueba deben tener clases balanceadas."""
    errores = []
    for particion in _PARTICIONES_BALANCEADAS:
        clases = Counter(r.clase for r in registros if r.particion == particion)
        total = clases[CLASE_REAL] + clases[CLASE_SINTETICA]
        if total == 0:
            continue
        diferencia = abs(clases[CLASE_REAL] - clases[CLASE_SINTETICA]) / total
        if diferencia > tolerancia:
            errores.append(
                f"desbalance en '{particion}': {clases[CLASE_REAL]} reales y "
                f"{clases[CLASE_SINTETICA]} sintéticas (diferencia {diferencia:.1%}, "
                f"tolerado {tolerancia:.1%})"
            )
    return errores


def _resumir(registros: list[RegistroImagen]) -> dict[str, dict[str, int]]:
    """Conteos por clase, partición, generador y fuente para el informe."""
    return {
        "clase": dict(Counter("sintetica" if r.clase else "real" for r in registros)),
        "particion": dict(Counter(r.particion for r in registros)),
        "generador": dict(Counter(r.generador for r in registros)),
        "fuente": dict(Counter(r.fuente for r in registros)),
    }


def validar(
    registros: list[RegistroImagen],
    raiz: Path,
    generadores_reservados: list[str] | None = None,
    desbalance_tolerado: float = 0.05,
    verificar_archivos: bool = True,
) -> ResultadoValidacion:
    """Ejecuta todas las verificaciones y devuelve los errores juntos.

    ``verificar_archivos`` puede desactivarse para validar solo la
    estructura del manifiesto sin tener las imágenes descargadas.
    """
    if not registros:
        return ResultadoValidacion(errores=["el manifiesto está vacío"])
    errores: list[str] = []
    if verificar_archivos:
        errores += _verificar_imagenes(registros, Path(raiz))
    errores += _verificar_duplicados(registros)
    errores += _verificar_reservados(registros, generadores_reservados or [])
    errores += _verificar_balance(registros, desbalance_tolerado)
    return ResultadoValidacion(errores=errores, resumen=_resumir(registros))


def exigir_valido(resultado: ResultadoValidacion) -> None:
    """Detiene el pipeline si la validación encontró errores."""
    if not resultado.es_valido:
        detalle = "\n  - ".join(resultado.errores)
        raise ErrorValidacionDatos(
            f"la validación encontró {len(resultado.errores)} errores:\n  - {detalle}"
        )
