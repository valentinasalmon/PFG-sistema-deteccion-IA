"""Fixtures compartidas por todas las pruebas del clasificador.

Las pruebas no descargan datos ni usan GPU (plan técnico, estrategia de
pruebas): las imágenes se generan en memoria con Pillow y se guardan en una
carpeta temporal. Las "reales" son degradados suaves con ruido, parecidos a
una fotografía, y las "sintéticas" son figuras geométricas sobre fondo
plano. Al modelo diminuto de las pruebas le alcanza esa diferencia para
aprender algo en pocos pasos.

Realiza: RNF19 (pruebas automáticas sin servicios externos).
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw


@dataclass(frozen=True)
class ImagenDePrueba:
    """Una imagen generada para las pruebas, con su etiqueta."""

    ruta: Path
    clase: int          # 0 = real, 1 = sintética
    generador: str      # "real" o el nombre del generador simulado


def crear_imagen_real(ancho: int, alto: int, semilla: int) -> Image.Image:
    """Crea una imagen tipo fotografía: degradado suave más ruido gaussiano."""
    generador = np.random.default_rng(semilla)
    ejes_x = np.linspace(0, 1, ancho)[None, :, None]
    ejes_y = np.linspace(0, 1, alto)[:, None, None]
    colores = generador.uniform(0, 1, size=(1, 1, 3))
    base = 255 * (0.5 * ejes_x + 0.5 * ejes_y) * colores
    ruido = generador.normal(0, 12, size=(alto, ancho, 3))
    pixeles = np.clip(base + ruido, 0, 255).astype(np.uint8)
    return Image.fromarray(pixeles, mode="RGB")


def crear_imagen_sintetica(ancho: int, alto: int, semilla: int) -> Image.Image:
    """Crea una imagen 'generada': figuras de color plano sin ruido."""
    generador = np.random.default_rng(semilla)
    fondo = tuple(int(v) for v in generador.integers(0, 256, size=3))
    imagen = Image.new("RGB", (ancho, alto), fondo)
    dibujo = ImageDraw.Draw(imagen)
    for _ in range(4):
        x0, y0 = generador.integers(0, ancho // 2), generador.integers(0, alto // 2)
        x1, y1 = x0 + generador.integers(10, ancho // 2), y0 + generador.integers(10, alto // 2)
        color = tuple(int(v) for v in generador.integers(0, 256, size=3))
        dibujo.ellipse([int(x0), int(y0), int(x1), int(y1)], fill=color)
    return imagen


# Formatos y tamaños variados a propósito: la preparación de datos debe
# normalizarlos (CA5) y el preprocesamiento debe tolerarlos (ADR-0015).
_VARIANTES = [
    ("png", (320, 240)),
    ("jpg", (256, 256)),
    ("webp", (240, 320)),
    ("jpg", (400, 300)),
]

_GENERADORES_SIMULADOS = ["generador_a", "generador_b"]


@pytest.fixture
def directorio_imagenes(tmp_path: Path) -> list[ImagenDePrueba]:
    """Genera 40 imágenes (20 reales y 20 sintéticas de dos generadores).

    Devuelve la lista con la ruta, la clase y el generador de cada imagen.
    """
    imagenes: list[ImagenDePrueba] = []
    for indice in range(20):
        formato, (ancho, alto) = _VARIANTES[indice % len(_VARIANTES)]

        ruta_real = tmp_path / "real" / f"real_{indice:03d}.{formato}"
        ruta_real.parent.mkdir(parents=True, exist_ok=True)
        crear_imagen_real(ancho, alto, semilla=indice).save(ruta_real)
        imagenes.append(ImagenDePrueba(ruta_real, 0, "real"))

        nombre_generador = _GENERADORES_SIMULADOS[indice % len(_GENERADORES_SIMULADOS)]
        ruta_sintetica = tmp_path / nombre_generador / f"sint_{indice:03d}.{formato}"
        ruta_sintetica.parent.mkdir(parents=True, exist_ok=True)
        crear_imagen_sintetica(ancho, alto, semilla=1000 + indice).save(ruta_sintetica)
        imagenes.append(ImagenDePrueba(ruta_sintetica, 1, nombre_generador))
    return imagenes


@pytest.fixture
def imagen_corrupta(tmp_path: Path) -> Path:
    """Crea un archivo con extensión de imagen pero contenido inválido."""
    ruta = tmp_path / "corrupta.jpg"
    ruta.write_bytes(b"esto no es una imagen")
    return ruta
