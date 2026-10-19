"""Predictor ONNX: el clasificador listo para usar en CPU.

Es la pieza que usa el backend en la funcionalidad 012 y la que usa la
evaluación del pipeline: ambos obtienen exactamente el mismo resultado para
la misma imagen. Los parámetros del preprocesamiento (tamaño de recorte,
media, desvío) se leen de los metadatos del propio archivo ONNX, de modo
que un modelo nunca se ejecuta con un preprocesamiento distinto del suyo.

Realiza: RF42 CA1, RN29, RNF24 CA1 y CA4. Ver ADR-0013.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

from clasificador.inferencia.preprocesamiento import (
    DESVIO_IMAGENET,
    MEDIA_IMAGENET,
    TAMANIO_RECORTE,
    preprocesar,
)

NOMBRE_ENTRADA = "entrada"
NOMBRE_SALIDA = "probabilidad"


class ErrorModelo(Exception):
    """El archivo no es un modelo del clasificador o le faltan metadatos."""


@dataclass(frozen=True)
class ParametrosEntrada:
    """Parámetros del contrato de entrada con que se entrenó el modelo."""

    tamanio_recorte: int = TAMANIO_RECORTE
    media: tuple[float, float, float] = MEDIA_IMAGENET
    desvio: tuple[float, float, float] = DESVIO_IMAGENET


@dataclass(frozen=True)
class MetadatosModelo:
    """Metadatos que viajan dentro del archivo ONNX (ADR-0013).

    Permiten saber, solo con el archivo, qué versión es, cómo preprocesar
    sus entradas y con qué datos y código se entrenó (RN29).
    """

    version: str
    arquitectura: str
    temperatura: float
    entrada: ParametrosEntrada
    huella_manifiesto: str
    commit: str

    def a_diccionario(self) -> dict[str, str]:
        """Serializa los valores como texto plano, que es lo que admite ONNX."""
        return {
            "version": self.version,
            "arquitectura": self.arquitectura,
            "temperatura": str(self.temperatura),
            "tamanio_recorte": str(self.entrada.tamanio_recorte),
            "media": json.dumps(list(self.entrada.media)),
            "desvio": json.dumps(list(self.entrada.desvio)),
            "huella_manifiesto": self.huella_manifiesto,
            "commit": self.commit,
        }

    @classmethod
    def desde_diccionario(cls, valores: dict[str, str]) -> "MetadatosModelo":
        """Reconstruye los metadatos leídos de un archivo ONNX."""
        try:
            return cls(
                version=valores["version"],
                arquitectura=valores["arquitectura"],
                temperatura=float(valores["temperatura"]),
                entrada=ParametrosEntrada(
                    tamanio_recorte=int(valores["tamanio_recorte"]),
                    media=tuple(json.loads(valores["media"])),
                    desvio=tuple(json.loads(valores["desvio"])),
                ),
                huella_manifiesto=valores["huella_manifiesto"],
                commit=valores["commit"],
            )
        except (KeyError, ValueError) as error:
            raise ErrorModelo(f"metadatos del modelo incompletos o inválidos: {error}") from error


@dataclass(frozen=True)
class Prediccion:
    """Resultado de la capa 4 para una imagen.

    Es una probabilidad estimada, no un veredicto (RN27): el texto que la
    acompaña en el informe se define en la funcionalidad 012.
    """

    probabilidad_sintetica: float
    version_modelo: str


class PredictorOnnx:
    """Ejecuta el clasificador en CPU con ONNX Runtime."""

    def __init__(self, ruta_modelo: Path | str) -> None:
        ruta_modelo = Path(ruta_modelo)
        if not ruta_modelo.is_file():
            raise ErrorModelo(f"no existe el modelo {ruta_modelo}")
        self.sesion = ort.InferenceSession(str(ruta_modelo), providers=["CPUExecutionProvider"])
        self.metadatos = MetadatosModelo.desde_diccionario(
            self.sesion.get_modelmeta().custom_metadata_map
        )

    @property
    def version(self) -> str:
        """Versión del modelo cargado (MAJOR.MINOR.PATCH)."""
        return self.metadatos.version

    def probabilidades_recortes(self, entrada: np.ndarray) -> np.ndarray:
        """Probabilidad de cada recorte de un tensor ``[N, 3, alto, ancho]``."""
        salida = self.sesion.run([NOMBRE_SALIDA], {NOMBRE_ENTRADA: entrada})[0]
        return np.asarray(salida, dtype=np.float64).ravel()

    def predecir(self, imagen: Image.Image) -> Prediccion:
        """Aplica el contrato de entrada y promedia los cinco recortes."""
        parametros = self.metadatos.entrada
        entrada = preprocesar(
            imagen,
            tamanio_recorte=parametros.tamanio_recorte,
            media=parametros.media,
            desvio=parametros.desvio,
        )
        probabilidad = float(self.probabilidades_recortes(entrada).mean())
        return Prediccion(probabilidad_sintetica=probabilidad, version_modelo=self.version)
