"""Pruebas de la obtención del modelo de la capa 4 (funcionalidad 012).

Usan un registro local con un modelo ONNX diminuto: nunca acceden a la red
ni a Hugging Face (constitución, sección 5).
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import pytest

from app.integraciones import modelo_red_neuronal
from app.integraciones.modelo_red_neuronal import (
    ModeloNoDisponible,
    obtener_modelo,
    vaciar_cache,
)
from pruebas.modelo_diminuto import armar_registro


@pytest.fixture(autouse=True)
def cache_limpia():
    """Cada prueba empieza sin modelos cargados."""
    vaciar_cache()
    yield
    vaciar_cache()


@pytest.fixture
def configuracion(tmp_path):
    """Registro local con la versión 1.0.0 publicada y una carpeta de descarga vacía."""
    armar_registro(tmp_path / "registro")
    return {
        "MODELO_RED_NEURONAL_REGISTRO": f"local:{tmp_path / 'registro'}",
        "MODELO_RED_NEURONAL_VERSION": "1.0.0",
        "CARPETA_MODELOS_ONNX": str(tmp_path / "descargas"),
    }


def test_obtiene_el_modelo_verificado_con_sus_datos(configuracion):
    """Devuelve el predictor con la versión, la huella y los metadatos (RN29)."""
    modelo = obtener_modelo(configuracion)
    assert modelo.version == "1.0.0"
    assert len(modelo.huella) == 64
    assert modelo.metadatos.huella_manifiesto.startswith("9ad67940")


def test_carga_el_modelo_una_sola_vez_por_proceso(configuracion, monkeypatch):
    """La segunda llamada reutiliza el predictor sin volver a cargarlo (RF42 CA3)."""
    primero = obtener_modelo(configuracion)
    monkeypatch.setattr(
        modelo_red_neuronal, "PredictorOnnx",
        lambda *_: pytest.fail("no debía volver a cargar el modelo"),
    )
    assert obtener_modelo(configuracion) is primero


def test_reutiliza_el_modelo_ya_bajado_sin_ir_al_registro(configuracion, tmp_path):
    """Si el modelo ya está en la carpeta y su huella coincide, no se vuelve a pedir."""
    obtener_modelo(configuracion)
    vaciar_cache()
    configuracion["MODELO_RED_NEURONAL_REGISTRO"] = f"local:{tmp_path / 'no_existe'}"
    assert obtener_modelo(configuracion).version == "1.0.0"


@pytest.mark.parametrize("cambios, motivo", [
    ({"MODELO_RED_NEURONAL_REGISTRO": ""}, "todavía no está configurado"),
    ({"MODELO_RED_NEURONAL_VERSION": ""}, "todavía no está configurado"),
    ({"MODELO_RED_NEURONAL_VERSION": "9.9.9"}, "No se pudo verificar la versión 9.9.9"),
    ({"MODELO_RED_NEURONAL_REGISTRO": "ftp:algo"}, "no es válida"),
])
def test_informa_el_motivo_si_no_hay_modelo(configuracion, cambios, motivo):
    """Sin configuración o con una versión inexistente, el motivo es legible (CA7)."""
    configuracion.update(cambios)
    with pytest.raises(ModeloNoDisponible, match=motivo):
        obtener_modelo(configuracion)


def test_rechaza_un_modelo_alterado(configuracion, tmp_path):
    """Si el modelo no coincide con su huella publicada, no se usa (ADR-0014)."""
    modelo = tmp_path / "registro" / "v1.0.0" / "modelo.onnx"
    modelo.write_bytes(modelo.read_bytes() + b"alterado")
    with pytest.raises(ModeloNoDisponible, match="No se pudo verificar"):
        obtener_modelo(configuracion)


def test_rechaza_un_archivo_que_no_es_un_modelo(configuracion, tmp_path):
    """Un archivo inválido con huellas coherentes se informa como modelo no válido."""
    # pylint: disable-next=import-outside-toplevel
    from clasificador.datos.manifiesto import huella_archivo

    carpeta = tmp_path / "registro" / "v1.0.0"
    (carpeta / "modelo.onnx").write_bytes(b"no es un modelo")
    (carpeta / "huellas.json").write_text(
        f'{{"modelo.onnx": "{huella_archivo(carpeta / "modelo.onnx")}"}}', encoding="utf-8"
    )
    with pytest.raises(ModeloNoDisponible):
        obtener_modelo(configuracion)


def test_una_falla_inesperada_del_registro_no_rompe_el_analisis(configuracion, monkeypatch):
    """Errores de red o de permisos se convierten en un motivo legible (RN26)."""
    def fallar(*_):
        raise ConnectionError("sin conexión")

    monkeypatch.setattr(modelo_red_neuronal, "_ruta_verificada", fallar)
    with pytest.raises(ModeloNoDisponible, match="No se pudo obtener la versión 1.0.0"):
        obtener_modelo(configuracion)
