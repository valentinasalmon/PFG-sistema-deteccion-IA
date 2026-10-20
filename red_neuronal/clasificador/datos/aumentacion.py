"""Aumentaciones de datos para el entrenamiento.

Simulan lo que le pasa a una imagen antes de llegar al sistema: recompresión
JPEG y reducción de tamaño por aplicaciones de mensajería, y recortes de
distintas zonas. Así el modelo aprende huellas de generación que resisten
esas transformaciones (CA12 de la funcionalidad 010).

El azar se toma del generador de PyTorch: con ``torch.manual_seed`` el
resultado es reproducible, y el ``DataLoader`` da a cada proceso de carga
una semilla distinta, por lo que no repiten la misma secuencia.

La normalización final reutiliza la de la inferencia (ADR-0015).

Realiza: CA7 y CA12 de la funcionalidad 010.
"""

import io

import torch
from PIL import Image

from clasificador.inferencia.preprocesamiento import (
    TAMANIO_RECORTE,
    ajustar_tamanio,
    convertir_a_rgb,
    normalizar,
    recorte_central,
)


def _uniforme(minimo: float, maximo: float) -> float:
    """Número aleatorio uniforme en [minimo, maximo] con el azar de PyTorch."""
    return minimo + (maximo - minimo) * torch.rand(1).item()


def _entero(minimo: int, maximo: int) -> int:
    """Entero aleatorio en [minimo, maximo] con el azar de PyTorch."""
    return int(torch.randint(minimo, maximo + 1, (1,)).item())


class AumentacionEntrenamiento:
    """Transformación aleatoria que se aplica a cada imagen de entrenamiento.

    Pasos: reducción aleatoria de tamaño, recompresión JPEG aleatoria,
    recorte aleatorio del tamaño de entrada y volteo horizontal.
    """

    def __init__(
        self,
        tamanio_recorte: int = TAMANIO_RECORTE,
        calidad_jpeg: tuple[int, int] = (50, 95),
        probabilidad_jpeg: float = 0.5,
        escala: tuple[float, float] = (0.5, 1.0),
        probabilidad_escala: float = 0.3,
    ) -> None:
        self.tamanio_recorte = tamanio_recorte
        self.calidad_jpeg = calidad_jpeg
        self.probabilidad_jpeg = probabilidad_jpeg
        self.escala = escala
        self.probabilidad_escala = probabilidad_escala

    def _reducir(self, imagen: Image.Image) -> Image.Image:
        factor = _uniforme(*self.escala)
        ancho, alto = imagen.size
        # Nunca por debajo del recorte: no tendría sentido ampliar después.
        factor = max(factor, self.tamanio_recorte / min(ancho, alto))
        if factor >= 1.0:
            return imagen
        return imagen.resize(
            (round(ancho * factor), round(alto * factor)), Image.Resampling.BILINEAR
        )

    def _recomprimir(self, imagen: Image.Image) -> Image.Image:
        bufer = io.BytesIO()
        imagen.save(bufer, format="JPEG", quality=_entero(*self.calidad_jpeg))
        bufer.seek(0)
        with Image.open(bufer) as recomprimida:
            return recomprimida.convert("RGB")

    def _recortar(self, imagen: Image.Image) -> Image.Image:
        ancho, alto = imagen.size
        izquierda = _entero(0, ancho - self.tamanio_recorte)
        arriba = _entero(0, alto - self.tamanio_recorte)
        return imagen.crop(
            (izquierda, arriba, izquierda + self.tamanio_recorte, arriba + self.tamanio_recorte)
        )

    def __call__(self, imagen: Image.Image) -> torch.Tensor:
        """Devuelve el tensor ``[3, alto, ancho]`` aumentado y normalizado."""
        imagen = convertir_a_rgb(imagen)
        if torch.rand(1).item() < self.probabilidad_escala:
            imagen = self._reducir(imagen)
        if torch.rand(1).item() < self.probabilidad_jpeg:
            imagen = self._recomprimir(imagen)
        imagen = ajustar_tamanio(imagen, self.tamanio_recorte)
        imagen = self._recortar(imagen)
        if torch.rand(1).item() < 0.5:
            imagen = imagen.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return torch.from_numpy(normalizar([imagen])[0])


class TransformacionEvaluacion:
    """Recorte central sin azar, idéntico al de la inferencia (ADR-0015)."""

    def __init__(self, tamanio_recorte: int = TAMANIO_RECORTE) -> None:
        self.tamanio_recorte = tamanio_recorte

    def __call__(self, imagen: Image.Image) -> torch.Tensor:
        """Devuelve el tensor ``[3, alto, ancho]`` del recorte central."""
        return torch.from_numpy(recorte_central(imagen, self.tamanio_recorte))
