"""Pruebas del contrato de entrada del clasificador (tarea T14)."""

import subprocess
import sys

import numpy as np
import pytest
from PIL import Image

from clasificador.inferencia.preprocesamiento import (
    DESVIO_IMAGENET,
    MEDIA_IMAGENET,
    ajustar_tamanio,
    cinco_recortes,
    convertir_a_rgb,
    preprocesar,
    recorte_central,
)


@pytest.mark.parametrize(
    ("modo", "tamanio"),
    [
        ("RGB", (300, 300)),      # tamaño intermedio: no se reescala
        ("RGB", (100, 80)),       # chica: se amplía
        ("RGB", (4000, 3000)),    # grande: se reduce
        ("RGB", (300, 2000)),     # vertical alargada
        ("RGBA", (256, 256)),     # con transparencia
        ("L", (256, 300)),        # escala de grises
        ("P", (230, 230)),        # paleta
    ],
)
def test_cualquier_imagen_produce_cinco_recortes_normalizados(modo, tamanio):
    """La forma de salida es siempre [5, 3, 224, 224] en float32."""
    tensor = preprocesar(Image.new(modo, tamanio))
    assert tensor.shape == (5, 3, 224, 224)
    assert tensor.dtype == np.float32


def test_una_imagen_intermedia_no_se_reescala():
    """Entre 224 y 1024 px se conservan los píxeles originales."""
    imagen = Image.new("RGB", (500, 400))
    assert ajustar_tamanio(imagen).size == (500, 400)


def test_una_imagen_grande_se_reduce_a_1024():
    """El lado mayor queda en 1024 y se respeta la proporción."""
    assert ajustar_tamanio(Image.new("RGB", (4096, 2048))).size == (1024, 512)


def test_una_imagen_chica_se_amplia_al_recorte():
    """El lado menor llega al tamaño de recorte."""
    assert min(ajustar_tamanio(Image.new("RGB", (100, 200))).size) == 224


def test_una_imagen_muy_alargada_prioriza_el_lado_menor():
    """Aunque el lado mayor supere 1024, el menor nunca queda por debajo de 224."""
    ancho, alto = ajustar_tamanio(Image.new("RGB", (5000, 300))).size
    assert min(ancho, alto) >= 224


def test_los_recortes_son_esquinas_y_centro():
    """El orden es: superior izquierda, superior derecha, inferior izquierda,
    inferior derecha y centro."""
    imagen = Image.new("RGB", (448, 448), (0, 0, 0))
    for indice, (x, y) in enumerate([(0, 0), (224, 0), (0, 224), (224, 224)]):
        imagen.paste((indice * 50, 0, 0), (x, y, x + 224, y + 224))
    recortes = cinco_recortes(imagen)
    assert [recorte.getpixel((10, 10))[0] for recorte in recortes[:4]] == [0, 50, 100, 150]
    assert recortes[4].getpixel((0, 0))[0] == 0      # esquina del centro: cuadrante 0
    assert recortes[4].getpixel((223, 223))[0] == 150


def test_la_normalizacion_usa_la_media_y_el_desvio_de_imagenet():
    """Un píxel gris medio da el valor esperado en cada canal."""
    tensor = preprocesar(Image.new("RGB", (224, 224), (128, 128, 128)))
    esperado = (128 / 255 - np.array(MEDIA_IMAGENET)) / np.array(DESVIO_IMAGENET)
    np.testing.assert_allclose(tensor[0, :, 0, 0], esperado, rtol=1e-5)


def test_la_transparencia_se_compone_sobre_blanco():
    """Un píxel transparente queda blanco."""
    rgb = convertir_a_rgb(Image.new("RGBA", (2, 2), (0, 0, 0, 0)))
    assert rgb.getpixel((0, 0)) == (255, 255, 255)


def test_el_recorte_central_coincide_con_el_quinto_recorte():
    """La validación rápida usa exactamente el mismo recorte que la inferencia."""
    imagen = Image.effect_noise((400, 300), 50).convert("RGB")
    np.testing.assert_array_equal(recorte_central(imagen), preprocesar(imagen)[4])


def test_el_modulo_de_inferencia_no_importa_pytorch():
    """El backend puede usarlo sin instalar PyTorch (ADR-0013)."""
    codigo = (
        "import sys; import clasificador.inferencia.preprocesamiento; "
        "print('torch' in sys.modules)"
    )
    salida = subprocess.run(
        [sys.executable, "-c", codigo], capture_output=True, text=True, check=True
    )
    assert salida.stdout.strip() == "False"
