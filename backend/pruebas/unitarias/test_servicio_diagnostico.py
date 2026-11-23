"""Pruebas del diagnóstico de fotos subidas desde el celular (funcionalidad 047, CA1)."""
import io

import pytest
from PIL import Image

from app.analisis.base import CapaNoDisponible
from app.servicios.errores import ErrorValidacion
from app.servicios.servicio_diagnostico import ServicioDiagnostico, describir_navegador

IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1"
)


def _jpeg():
    salida = io.BytesIO()
    Image.new("RGB", (40, 30), (120, 80, 40)).save(salida, "JPEG")
    return salida.getvalue()


class LectorFalso:
    """Lector de metadatos de prueba: devuelve los datos dados o falla."""

    def __init__(self, datos=None, falla=False):
        self.datos = datos or {}
        self.falla = falla

    def extraer(self, _contenido):
        """Imita a ``CapaMetadatos.extraer``."""
        if self.falla:
            raise CapaNoDisponible("sin ExifTool")
        return self.datos


def test_describe_una_foto_con_metadatos_y_ubicacion():
    """Formato, cámara, fecha y ubicación salen de los metadatos."""
    datos = {"EXIF:IFD0:Make": "Apple", "Make": "Apple", "Model": "iPhone 15",
             "EXIF:ExifIFD:DateTimeOriginal": "2026:11:18 10:00:00",
             "DateTimeOriginal": "2026:11:18 10:00:00", "GPSLatitude": "27 deg 28' S"}
    resultado = ServicioDiagnostico(LectorFalso(datos), 10_000_000).diagnosticar(_jpeg(), IPHONE)
    assert resultado["formato"] == "JPEG"
    assert resultado["es_heic"] is False
    assert resultado["campos_exif"] == 2
    assert resultado["marca"] == "Apple"
    assert resultado["modelo"] == "iPhone 15"
    assert resultado["fecha_captura"] == "2026:11:18 10:00:00"
    assert resultado["tiene_ubicacion"] is True
    assert resultado["dispositivo"] == {
        "sistema": "iPhone o iPad (iOS 18.1)", "navegador": "Safari",
    }


def test_foto_sin_metadatos():
    """Una foto que llegó limpia se informa sin cámara ni ubicación."""
    resultado = ServicioDiagnostico(LectorFalso({}), 10_000_000).diagnosticar(_jpeg())
    assert resultado["campos_exif"] == 0
    assert resultado["marca"] is None
    assert resultado["tiene_ubicacion"] is False


def test_sin_exiftool_igual_responde():
    """Si ExifTool no está, se informa que no se pudieron leer los metadatos."""
    resultado = ServicioDiagnostico(LectorFalso(falla=True), 10_000_000).diagnosticar(_jpeg())
    assert resultado["metadatos_leidos"] is False


@pytest.mark.parametrize("contenido, tamanio", [(b"", 100), (b"no es una imagen", 100)])
def test_rechaza_vacio_o_no_imagen(contenido, tamanio):
    """Sin archivo o con un archivo que no es imagen, error de validación."""
    with pytest.raises(ErrorValidacion):
        ServicioDiagnostico(LectorFalso(), tamanio).diagnosticar(contenido)


def test_rechaza_una_foto_demasiado_grande():
    """Respeta el tamaño máximo de la plataforma (RN22)."""
    with pytest.raises(ErrorValidacion):
        ServicioDiagnostico(LectorFalso(), 10).diagnosticar(_jpeg())


@pytest.mark.parametrize("agente, esperado", [
    ("Mozilla/5.0 (Linux; Android 14) Chrome/130.0 Mobile Safari/537.36", ("Android", "Chrome")),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) CriOS/130.0 Mobile Safari",
     ("iPhone o iPad (iOS 17.5)", "Chrome")),
    (None, ("otro", "otro")),
])
def test_describe_el_navegador(agente, esperado):
    """Sistema y navegador sin guardar el texto completo."""
    datos = describir_navegador(agente)
    assert (datos["sistema"], datos["navegador"]) == esperado
