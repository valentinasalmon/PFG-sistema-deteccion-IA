"""Fuentes de imágenes del pipeline (patrón Strategy).

Cada conjunto de datos tiene su propio formato. Una ``FuenteDatos`` oculta
esas diferencias y entrega siempre ejemplos con la misma forma: bytes de la
imagen, clase, generador y variante. Las etapas del pipeline dependen solo
de esta interfaz, por lo que una fuente se agrega o se reemplaza sin tocar
el resto, y en las pruebas se simula sin acceder a la red (constitución,
sección 5).

Implementaciones:

- ``FuenteHuggingFace``: conjuntos públicos leídos en *streaming*.
- ``FuenteCarpetaLocal``: el conjunto propio (CA12, CA13) y las pruebas.

Realiza: CA2 y CA12 de la funcionalidad 010. Ver ADR-0014.
"""

import io
import os
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from clasificador.configuracion import ConfiguracionFuente
from clasificador.datos.manifiesto import CLASE_REAL, CLASE_SINTETICA, VARIANTES

EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".heic"}
_NOMBRES_CLASE = {"real": CLASE_REAL, "sintetica": CLASE_SINTETICA}


class ErrorFuente(Exception):
    """La fuente no está disponible o devuelve datos con forma inesperada."""


@dataclass(frozen=True)
class EjemploCrudo:
    """Una imagen tal como la entrega la fuente, sin modificar."""

    contenido: bytes
    extension: str        # con punto, en minúsculas: ".jpg", ".png"
    clase: int
    generador: str
    variante: str = "original"
    nombre: str | None = None  # ruta dentro de la fuente, si tiene nombre propio


class FuenteDatos(ABC):
    """Interfaz común de todas las fuentes de imágenes."""

    def __init__(self, configuracion: ConfiguracionFuente) -> None:
        self.configuracion = configuracion

    @property
    def nombre(self) -> str:
        """Nombre de la fuente, que queda registrado en el manifiesto."""
        return self.configuracion.nombre

    @abstractmethod
    def iterar(self) -> Iterator[EjemploCrudo]:
        """Recorre los ejemplos de la fuente en un orden reproducible."""


def _extension_de(contenido: bytes) -> str:
    """Detecta el formato real de la imagen a partir de su contenido."""
    try:
        with Image.open(io.BytesIO(contenido)) as imagen:
            formato = (imagen.format or "").lower()
    except (UnidentifiedImageError, OSError) as error:
        raise ErrorFuente("el contenido recibido no es una imagen válida") from error
    return {"jpeg": ".jpg", "tiff": ".tif"}.get(formato, f".{formato}")


def _a_bytes(valor: Any) -> bytes:
    """Convierte el valor de la columna de imagen de Hugging Face a bytes.

    Según cómo esté definida la columna, ``datasets`` entrega bytes, un
    diccionario ``{"bytes": ..., "path": ...}`` o una imagen ya decodificada.
    """
    if isinstance(valor, bytes):
        return valor
    if isinstance(valor, dict) and valor.get("bytes"):
        return valor["bytes"]
    if isinstance(valor, Image.Image):
        bufer = io.BytesIO()
        valor.save(bufer, format=valor.format or "PNG")
        return bufer.getvalue()
    raise ErrorFuente(f"formato de imagen no reconocido: {type(valor).__name__}")


def _cargar_desde_hugging_face(configuracion: ConfiguracionFuente) -> Iterable[dict]:
    """Abre el conjunto en *streaming* sin decodificar las imágenes.

    Se importa ``datasets`` acá adentro para que el resto del paquete no
    dependa de esa biblioteca. El *token* se toma de la variable de entorno
    ``HF_TOKEN`` (secreto de Colab); nunca de un archivo del repositorio.

    Si la receta fija ``archivos``, solo se leen esos archivos: en Parquet,
    leer una imagen obliga a bajar la columna de imágenes de todo el archivo,
    así que muestrear por archivos ahorra descargas (bitácora del 2026-10-19).

    """
    # pylint: disable-next=import-outside-toplevel
    from datasets import Image as ColumnaImagen, load_dataset

    conjunto = load_dataset(
        configuracion.conjunto,
        data_files=configuracion.archivos or None,
        split=configuracion.division,
        revision=configuracion.revision,
        streaming=True,
        token=os.environ.get("HF_TOKEN"),
    )
    return conjunto.cast_column(configuracion.columna_imagen, ColumnaImagen(decode=False))


class FuenteHuggingFace(FuenteDatos):
    """Conjunto público de Hugging Face, leído en *streaming*.

    Las filas se mezclan con un búfer y una semilla fija: los conjuntos suelen
    venir ordenados por generador, y tomar las primeras N filas daría un solo
    generador.
    """

    def __init__(
        self,
        configuracion: ConfiguracionFuente,
        semilla: int,
        cargador: Callable[[ConfiguracionFuente], Iterable[dict]] = _cargar_desde_hugging_face,
        tamanio_bufer: int = 10_000,
    ) -> None:
        super().__init__(configuracion)
        self.semilla = semilla
        self.cargador = cargador
        self.tamanio_bufer = tamanio_bufer

    def iterar(self) -> Iterator[EjemploCrudo]:
        """Recorre las filas mezcladas y las convierte en ejemplos."""
        filas = self.cargador(self.configuracion)
        if hasattr(filas, "shuffle"):
            filas = filas.shuffle(seed=self.semilla, buffer_size=self.tamanio_bufer)
        incluidos = set(self.configuracion.generadores_incluidos)
        for fila in filas:
            if self._excluida(fila):
                continue
            ejemplo = self._convertir(fila)
            excluido = ejemplo.clase == CLASE_SINTETICA and ejemplo.generador not in incluidos
            if incluidos and excluido:
                continue
            yield ejemplo

    def _excluida(self, fila: dict) -> bool:
        """Indica si la fila cumple algún criterio de exclusión de la receta.

        Se usa, por ejemplo, para descartar imágenes marcadas como contenido
        explícito, que no deben formar parte del entrenamiento.
        """
        return any(
            str(fila.get(columna)) in valores
            for columna, valores in self.configuracion.excluir.items()
        )

    def _convertir(self, fila: dict) -> EjemploCrudo:
        config = self.configuracion
        for columna in (config.columna_imagen, config.columna_clase):
            if columna is not None and columna not in fila:
                raise ErrorFuente(
                    f"la fuente '{config.nombre}' no tiene la columna '{columna}'; "
                    f"columnas disponibles: {sorted(fila)}"
                )
        if config.clase_fija is not None:
            clase = _NOMBRES_CLASE[config.clase_fija]
        else:
            clase = (
                CLASE_SINTETICA
                if str(fila[config.columna_clase]) in config.valores_sinteticos
                else CLASE_REAL
            )
        if clase == CLASE_REAL:
            generador = "real"
        elif config.columna_generador and fila.get(config.columna_generador):
            generador = str(fila[config.columna_generador])
        else:
            generador = config.nombre
        contenido = _a_bytes(fila[config.columna_imagen])
        return EjemploCrudo(contenido, _extension_de(contenido), clase, generador)


class FuenteCarpetaLocal(FuenteDatos):
    """Imágenes organizadas en carpetas: ``<clase>/<generador>/<variante>/``.

    ``<clase>`` es ``real`` o ``sintetica``; ``<variante>`` es una de
    ``original``, ``whatsapp``, ``captura`` o ``editada``. Es la estructura
    del conjunto propio definida en el protocolo de recolección (T26).
    """

    def iterar(self) -> Iterator[EjemploCrudo]:
        """Recorre las imágenes en orden alfabético de ruta."""
        raiz = Path(self.configuracion.ruta)
        if not raiz.is_dir():
            raise ErrorFuente(f"no existe la carpeta de la fuente '{self.nombre}': {raiz}")
        for ruta in sorted(raiz.rglob("*")):
            if not ruta.is_file() or ruta.suffix.lower() not in EXTENSIONES_IMAGEN:
                continue
            partes = ruta.relative_to(raiz).parts
            if len(partes) != 4 or partes[0] not in _NOMBRES_CLASE or partes[2] not in VARIANTES:
                raise ErrorFuente(
                    f"la imagen {ruta} no respeta la estructura <clase>/<generador>/<variante>/"
                )
            contenido = ruta.read_bytes()
            yield EjemploCrudo(
                contenido=contenido,
                extension=_extension_de(contenido),
                clase=_NOMBRES_CLASE[partes[0]],
                generador=partes[1],
                variante=partes[2],
                nombre="/".join(partes),
            )


def crear_fuente(configuracion: ConfiguracionFuente, semilla: int) -> FuenteDatos:
    """Fábrica: crea la fuente que corresponde al tipo configurado."""
    if configuracion.tipo == "hugging_face":
        return FuenteHuggingFace(configuracion, semilla)
    return FuenteCarpetaLocal(configuracion)
