"""Pruebas de las fixtures compartidas y de la instalación del paquete.

Verifican que el paquete se importa y que los datos de prueba tienen la
forma que el resto de las pruebas espera.
"""

from PIL import Image

import clasificador


def test_el_paquete_expone_su_version():
    """El paquete instalado informa una versión con formato X.Y.Z."""
    partes = clasificador.__version__.split(".")
    assert len(partes) == 3
    assert all(parte.isdigit() for parte in partes)


def test_directorio_imagenes_esta_balanceado(directorio_imagenes):
    """Hay la misma cantidad de imágenes reales y sintéticas."""
    reales = [i for i in directorio_imagenes if i.clase == 0]
    sinteticas = [i for i in directorio_imagenes if i.clase == 1]
    assert len(reales) == len(sinteticas) == 20


def test_directorio_imagenes_tiene_formatos_variados(directorio_imagenes):
    """Las imágenes se abren y vienen en más de un formato."""
    formatos = set()
    for imagen in directorio_imagenes:
        with Image.open(imagen.ruta) as abierta:
            abierta.verify()
            formatos.add(abierta.format)
    assert len(formatos) >= 3


def test_imagen_corrupta_no_se_puede_abrir(imagen_corrupta):
    """La fixture de imagen corrupta realmente es inválida."""
    try:
        with Image.open(imagen_corrupta) as abierta:
            abierta.verify()
        abierta_ok = True
    except Exception:  # pylint: disable=broad-except
        abierta_ok = False
    assert not abierta_ok
