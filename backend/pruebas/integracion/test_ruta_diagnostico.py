"""Pruebas de la ruta POST /api/diagnostico/foto (funcionalidad 047, CA1)."""
import io

from PIL import Image


def _foto():
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), (30, 90, 150)).save(salida, "JPEG")
    salida.seek(0)
    return salida


def test_describe_la_foto_sin_sesion(cliente):
    """Sin cuenta: devuelve qué llegó y no guarda nada."""
    respuesta = cliente.post(
        "/api/diagnostico/foto", data={"foto": (_foto(), "foto.jpg")},
        content_type="multipart/form-data",
        headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) Safari"},
    )
    assert respuesta.status_code == 200
    datos = respuesta.get_json()["diagnostico"]
    assert datos["formato"] == "JPEG"
    assert datos["dispositivo"]["sistema"] == "iPhone o iPad (iOS 18.1)"
    assert datos["tiene_ubicacion"] is False


def test_sin_archivo_es_un_error_de_validacion(cliente):
    """Sin el campo ``foto`` responde 400 con un mensaje claro."""
    respuesta = cliente.post("/api/diagnostico/foto", data={}, content_type="multipart/form-data")
    assert respuesta.status_code == 400
    assert "foto" in respuesta.get_json()["mensaje"].lower()
