"""Contrato de entrada del clasificador (ADR-0015).

Pasos, en este orden:

1. Conversión a RGB, componiendo la transparencia sobre fondo blanco.
2. Ajuste de tamaño solo en los extremos: si el lado mayor supera 1024 px se
   reduce, y si el lado menor es inferior al tamaño de recorte se amplía.
   En el resto de los casos la imagen **no se reescala**, para no borrar las
   huellas de alta frecuencia que deja la generación.
3. Cinco recortes del tamaño de entrada: las cuatro esquinas y el centro.
4. Normalización con la media y el desvío de ImageNet, en formato
   ``[N, 3, alto, ancho]`` y tipo ``float32``.

El backend y la evaluación usan estas mismas funciones. Cambiar cualquiera
de estos pasos obliga a publicar una versión MAJOR del modelo.

Realiza: RF42, RNF24 CA1; CA14 de la funcionalidad 010.
"""

import numpy as np
from PIL import Image

TAMANIO_RECORTE = 224
LADO_MAXIMO = 1024
MEDIA_IMAGENET = (0.485, 0.456, 0.406)
DESVIO_IMAGENET = (0.229, 0.224, 0.225)
CANTIDAD_RECORTES = 5
INDICE_RECORTE_CENTRAL = 4


def convertir_a_rgb(imagen: Image.Image) -> Image.Image:
    """Convierte a RGB componiendo la transparencia sobre fondo blanco.

    Sin este paso, Pillow descarta el canal alfa y las zonas transparentes
    quedan negras: un artefacto que solo tendrían las imágenes con alfa.
    """
    if imagen.mode in ("RGBA", "LA", "P", "PA"):
        con_alfa = imagen.convert("RGBA")
        fondo = Image.new("RGBA", con_alfa.size, (255, 255, 255, 255))
        return Image.alpha_composite(fondo, con_alfa).convert("RGB")
    return imagen.convert("RGB")


def ajustar_tamanio(
    imagen: Image.Image, tamanio_recorte: int = TAMANIO_RECORTE, lado_maximo: int = LADO_MAXIMO
) -> Image.Image:
    """Reescala solo si la imagen es demasiado grande o demasiado chica."""
    ancho, alto = imagen.size
    escala = 1.0
    if max(ancho, alto) > lado_maximo:
        escala = lado_maximo / max(ancho, alto)
    if min(ancho, alto) * escala < tamanio_recorte:
        escala = tamanio_recorte / min(ancho, alto)
    if escala == 1.0:
        return imagen
    nuevo = (
        max(tamanio_recorte, round(ancho * escala)),
        max(tamanio_recorte, round(alto * escala)),
    )
    return imagen.resize(nuevo, Image.Resampling.LANCZOS)


def cinco_recortes(imagen: Image.Image, tamanio: int = TAMANIO_RECORTE) -> list[Image.Image]:
    """Devuelve los recortes de las cuatro esquinas y del centro, en ese orden."""
    ancho, alto = imagen.size
    izquierda_centro = (ancho - tamanio) // 2
    arriba_centro = (alto - tamanio) // 2
    origenes = [
        (0, 0),
        (ancho - tamanio, 0),
        (0, alto - tamanio),
        (ancho - tamanio, alto - tamanio),
        (izquierda_centro, arriba_centro),
    ]
    return [imagen.crop((x, y, x + tamanio, y + tamanio)) for x, y in origenes]


def normalizar(
    recortes: list[Image.Image],
    media: tuple[float, ...] = MEDIA_IMAGENET,
    desvio: tuple[float, ...] = DESVIO_IMAGENET,
) -> np.ndarray:
    """Convierte los recortes a un tensor ``float32`` ``[N, 3, alto, ancho]``."""
    pila = np.stack([np.asarray(recorte, dtype=np.float32) / 255.0 for recorte in recortes])
    pila = (pila - np.asarray(media, dtype=np.float32)) / np.asarray(desvio, dtype=np.float32)
    return np.ascontiguousarray(pila.transpose(0, 3, 1, 2), dtype=np.float32)


def preprocesar(
    imagen: Image.Image,
    tamanio_recorte: int = TAMANIO_RECORTE,
    media: tuple[float, ...] = MEDIA_IMAGENET,
    desvio: tuple[float, ...] = DESVIO_IMAGENET,
) -> np.ndarray:
    """Aplica el contrato completo y devuelve los cinco recortes normalizados."""
    imagen = ajustar_tamanio(convertir_a_rgb(imagen), tamanio_recorte)
    return normalizar(cinco_recortes(imagen, tamanio_recorte), media, desvio)


def recorte_central(
    imagen: Image.Image,
    tamanio_recorte: int = TAMANIO_RECORTE,
    media: tuple[float, ...] = MEDIA_IMAGENET,
    desvio: tuple[float, ...] = DESVIO_IMAGENET,
) -> np.ndarray:
    """Solo el recorte central ``[3, alto, ancho]``.

    Se usa para la validación rápida durante el entrenamiento; la evaluación
    final y el backend usan los cinco recortes.
    """
    imagen = ajustar_tamanio(convertir_a_rgb(imagen), tamanio_recorte)
    central = cinco_recortes(imagen, tamanio_recorte)[INDICE_RECORTE_CENTRAL]
    return normalizar([central], media, desvio)[0]
