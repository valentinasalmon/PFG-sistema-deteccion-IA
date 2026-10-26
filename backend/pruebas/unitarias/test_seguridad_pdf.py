"""Pruebas del obtenedor de recursos de WeasyPrint (funcionalidad 030).

Los PDF solo pueden incrustar recursos ``data:``: ni direcciones de red
(SSRF, por ejemplo el servicio de metadatos de la EC2) ni archivos locales.
"""
import pytest

from app.informes.plantillas import obtenedor_de_recursos

PNG_1X1 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "YAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


@pytest.mark.parametrize("url", [
    "http://169.254.169.254/latest/meta-data/",
    "https://ejemplo.com/imagen.png",
    "file:///etc/passwd",
    "ftp://ejemplo.com/a",
])
def test_rechaza_red_y_archivos(url):
    """Una dirección de red o un archivo local no se descarga."""
    with pytest.raises(ValueError, match="disallowed protocol"):
        obtenedor_de_recursos()(url)


def test_acepta_recursos_incrustados():
    """Las imágenes incrustadas (logo, QR, mapa ELA) siguen funcionando."""
    respuesta = obtenedor_de_recursos()(PNG_1X1)
    try:
        assert respuesta.read().startswith(b"\x89PNG")
    finally:
        respuesta.close()
