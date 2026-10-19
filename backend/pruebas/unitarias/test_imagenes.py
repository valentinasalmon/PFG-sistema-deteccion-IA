"""Pruebas de la lectura de imágenes: formato real, dimensiones y miniatura (006)."""
import io

import pytest
from PIL import Image

from app.utilidades.imagenes import (
    ImagenInvalida,
    detectar_formato,
    generar_miniatura,
    leer_dimensiones,
)


def _imagen(formato, tamanio=(40, 30), modo="RGB"):
    salida = io.BytesIO()
    Image.new(modo, tamanio).save(salida, format=formato)
    return salida.getvalue()


def test_el_formato_se_detecta_por_la_firma():
    """RN22: la firma binaria decide, no la extensión."""
    assert detectar_formato(_imagen("JPEG")) == "jpeg"
    assert detectar_formato(_imagen("PNG")) == "png"
    assert detectar_formato(_imagen("GIF")) is None
    assert detectar_formato(b"%PDF-1.7") is None


def test_un_contenido_que_no_coincide_con_su_firma_se_rechaza():
    """La firma de PNG seguida de otro contenido no es una imagen válida."""
    with pytest.raises(ImagenInvalida):
        leer_dimensiones(b"\x89PNG\r\n\x1a\n" + b"x" * 100, "png")
    with pytest.raises(ImagenInvalida):
        leer_dimensiones(_imagen("PNG"), "jpeg")


def test_una_imagen_truncada_se_rechaza():
    """Un archivo cortado a la mitad no pasa la verificación."""
    contenido = _imagen("PNG", (300, 300))
    with pytest.raises(ImagenInvalida):
        leer_dimensiones(contenido[: len(contenido) // 2], "png")


def test_una_bomba_de_descompresion_se_rechaza(monkeypatch):
    """RNF04: imágenes con demasiados píxeles no se procesan."""
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)
    with pytest.raises(ImagenInvalida):
        leer_dimensiones(_imagen("PNG", (40, 30)), "png")


def test_la_miniatura_es_un_jpeg_reducido_y_no_toca_el_original():
    """RN23: la miniatura es una copia nueva."""
    original = _imagen("PNG", (1000, 500), "RGBA")
    copia = bytes(original)
    miniatura = generar_miniatura(original, 480)
    assert original == copia
    imagen = Image.open(io.BytesIO(miniatura))
    assert (imagen.format, imagen.size) == ("JPEG", (480, 240))


def test_la_miniatura_de_un_contenido_ilegible_falla():
    """Un contenido que no es imagen no genera miniatura."""
    with pytest.raises(ImagenInvalida):
        generar_miniatura(b"nada", 480)
