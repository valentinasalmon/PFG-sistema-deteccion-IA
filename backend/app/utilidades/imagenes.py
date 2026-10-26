"""Lectura de imágenes: formato real, dimensiones y miniatura.

El formato se determina por la firma binaria del contenido, no por la
extensión ni por el tipo que declara el navegador (RN22). Ninguna función
modifica el contenido recibido: la miniatura es una copia nueva (RN23).

Las fotos HEIC/HEIF del iPhone se leen con ``pillow-heif``: el original se
guarda tal cual y solo la miniatura se convierte a JPEG (funcionalidad 024).

Realiza: RF34 (CA1, CA2), RF35 (vista previa), RF53 (CA3); RN22, RN23.
"""
import io
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

register_heif_opener()  # Pillow puede abrir HEIC/HEIF desde acá en adelante

FIRMAS = {
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG\r\n\x1a\n": "png",
}
FORMATOS_PILLOW = {"jpeg": "JPEG", "png": "PNG", "heic": "HEIF"}
# Marcas de la caja "ftyp" de un HEIC/HEIF (ISO/IEC 23008-12). AVIF usa otras.
MARCAS_HEIC = {b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis"}
MARCAS_HEIF_GENERICAS = {b"mif1", b"msf1"}


class ImagenInvalida(Exception):
    """El contenido no es una imagen JPEG, PNG o HEIC legible."""


def _es_heic(contenido):
    """True si la caja ``ftyp`` declara HEIC (o HEIF genérico con HEIC entre las compatibles)."""
    if len(contenido) < 16 or contenido[4:8] != b"ftyp":
        return False
    tamanio = int.from_bytes(contenido[0:4], "big")
    marca = contenido[8:12]
    compatibles = {
        contenido[i:i + 4] for i in range(16, min(tamanio, len(contenido), 64) - 3, 4)
    }
    return marca in MARCAS_HEIC or (
        marca in MARCAS_HEIF_GENERICAS and bool(compatibles & MARCAS_HEIC)
    )


def detectar_formato(contenido):
    """Devuelve ``"jpeg"``, ``"png"`` o ``"heic"`` según la firma binaria, o None.

    No se confía en la extensión: algunos celulares entregan un HEIC con
    nombre ``.jpg`` (RN22).
    """
    for firma, formato in FIRMAS.items():
        if contenido.startswith(firma):
            return formato
    return "heic" if _es_heic(contenido) else None


def _abrir(contenido):
    """Abre la imagen; convierte las bombas de descompresión en un error (RNF04)."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            return Image.open(io.BytesIO(contenido))
        except (UnidentifiedImageError, Image.DecompressionBombError,
                Image.DecompressionBombWarning, OSError) as error:
            raise ImagenInvalida("No se pudo leer la imagen.") from error


def leer_dimensiones(contenido, formato):
    """Verifica que la imagen esté completa y devuelve ``(ancho, alto)``.

    Raises:
        ImagenInvalida: si está dañada o su contenido no coincide con el formato.
    """
    imagen = _abrir(contenido)
    if imagen.format != FORMATOS_PILLOW[formato]:
        raise ImagenInvalida("El contenido no coincide con el formato.")
    try:
        imagen.verify()
    except Exception as error:  # Pillow lanza distintos errores según el daño
        raise ImagenInvalida("La imagen está dañada.") from error
    return imagen.size


def generar_miniatura(contenido, lado):
    """Copia reducida en JPEG para la vista previa, respetando la orientación EXIF."""
    imagen = _abrir(contenido)
    try:
        imagen = ImageOps.exif_transpose(imagen)
        imagen.thumbnail((lado, lado))
        if imagen.mode != "RGB":
            fondo = Image.new("RGB", imagen.size, (255, 255, 255))
            fondo.paste(imagen, mask=imagen.convert("RGBA").getchannel("A"))
            imagen = fondo
        salida = io.BytesIO()
        imagen.save(salida, format="JPEG", quality=80)
    except OSError as error:
        raise ImagenInvalida("No se pudo generar la vista previa.") from error
    return salida.getvalue()
