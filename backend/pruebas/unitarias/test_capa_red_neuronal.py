"""Pruebas de la capa 4, red neuronal (funcionalidad 012).

Usan el modelo ONNX diminuto de ``pruebas/modelo_diminuto.py`` en un registro
local: nunca acceden a la red ni necesitan PyTorch.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import io
from datetime import datetime

import pytest
from PIL import Image

from app.analisis.base import (
    RECOMENDACION,
    SEVERIDAD_FUERTE,
    SEVERIDAD_MODERADO,
    TERMINOS_DE_VEREDICTO,
    CapaNoDisponible,
    ContextoImagen,
)
from app.analisis.red_neuronal import (
    ACLARACION_PROBABILIDAD_BAJA,
    LIMITACIONES,
    CapaRedNeuronal,
    calcular_nivel_red,
)
from app.analisis.registro import crear_capas
from app.integraciones.modelo_red_neuronal import vaciar_cache
from clasificador.inferencia.predictor import PredictorOnnx
from pruebas.modelo_diminuto import armar_registro, imagen_gris

CONTEXTO = ContextoImagen("jpeg", 320, 240, datetime(2026, 11, 6, 12, 0))


@pytest.fixture(autouse=True)
def cache_limpia():
    """Cada prueba carga su propio modelo diminuto."""
    vaciar_cache()
    yield
    vaciar_cache()


def _configuracion(tmp_path, **opciones):
    armar_registro(tmp_path / "registro", **opciones)
    return {
        "MODELO_RED_NEURONAL_REGISTRO": f"local:{tmp_path / 'registro'}",
        "MODELO_RED_NEURONAL_VERSION": "1.0.0",
        "CARPETA_MODELOS_ONNX": str(tmp_path / "descargas"),
    }


def _analizar(tmp_path, probabilidad):
    capa = CapaRedNeuronal(_configuracion(tmp_path, probabilidad=probabilidad))
    return capa.analizar(imagen_gris(), CONTEXTO)


@pytest.mark.parametrize("probabilidad, nivel", [
    (0.0, 0), (0.49, 0), (0.5, 50), (0.73, 73), (0.9, 90), (0.97, 90), (1.0, 90),
])
def test_nivel_es_la_probabilidad_con_tope_de_90(probabilidad, nivel):
    """CA1: 0 por debajo de 50 %; desde ahí el porcentaje, con un máximo de 90 (RN28)."""
    assert calcular_nivel_red(probabilidad) == nivel


@pytest.mark.parametrize("probabilidad, severidad", [
    (0.6, SEVERIDAD_MODERADO), (0.8, SEVERIDAD_FUERTE),
])
def test_probabilidad_alta_da_una_anomalia(tmp_path, probabilidad, severidad):
    """CA1: la anomalía es moderada por debajo de 70 % y fuerte desde ahí."""
    resultado = _analizar(tmp_path, probabilidad)
    assert resultado.nivel == round(100 * probabilidad)
    assert len(resultado.anomalias) == 1
    assert resultado.anomalias[0].severidad == severidad
    assert resultado.anomalias[0].valor == f"{round(100 * probabilidad)} %"


def test_probabilidad_baja_no_aporta_indicios(tmp_path):
    """CA4: sin anomalías y con la aclaración de que no significa que la foto sea real."""
    resultado = _analizar(tmp_path, 0.2)
    assert (resultado.nivel, resultado.anomalias) == (0, [])
    assert "20 %" in resultado.conclusion
    assert ACLARACION_PROBABILIDAD_BAJA in resultado.conclusion


@pytest.mark.parametrize("probabilidad", [0.2, 0.6, 0.95])
def test_conclusion_es_un_indicio_con_limitaciones(tmp_path, probabilidad):
    """CA5 y RN27: sin veredictos, con las limitaciones del modelo y la recomendación."""
    conclusion = _analizar(tmp_path, probabilidad).conclusion
    assert LIMITACIONES in conclusion
    assert conclusion.endswith(RECOMENDACION)
    assert not any(termino in conclusion.lower() for termino in TERMINOS_DE_VEREDICTO)


def test_detalle_registra_el_modelo_y_la_tabla(tmp_path):
    """CA6 y RN29: versión, huellas, commit y ONNX Runtime; tabla con umbrales y desempeño."""
    detalle = _analizar(tmp_path, 0.8).detalle
    modelo = detalle["modelo"]
    assert modelo["version"] == "1.0.0"
    assert len(modelo["huella"]) == 64
    assert modelo["huella_manifiesto"].startswith("9ad67940")
    assert modelo["commit"].startswith("0ee4e9e")
    assert modelo["onnxruntime"]
    assert detalle["probabilidad"] == pytest.approx(0.8, abs=1e-4)
    campos = {fila["campo"]: fila["valor"] for fila in detalle["tabla"]}
    assert campos["Probabilidad estimada de imagen generada con IA"] == "80 %"
    assert campos["Umbral a partir del cual la capa aporta indicios"] == "50 %"
    assert campos["Versión del modelo"] == "1.0.0"
    assert "AUC 0,961" in campos["Desempeño publicado del modelo"]


def test_version_desconocida_no_muestra_desempenio(tmp_path):
    """Una versión sin ficha publicada en la tabla no inventa métricas."""
    configuracion = _configuracion(tmp_path, version="1.1.0")
    configuracion["MODELO_RED_NEURONAL_VERSION"] = "1.1.0"
    detalle = CapaRedNeuronal(configuracion).analizar(imagen_gris(), CONTEXTO).detalle
    assert all(fila["campo"] != "Desempeño publicado del modelo" for fila in detalle["tabla"])


def test_probabilidad_igual_a_la_del_predictor_de_la_010(tmp_path):
    """CA2: la capa usa el mismo preprocesamiento que la evaluación (ADR-0015)."""
    configuracion = _configuracion(tmp_path, pendiente=4.0, probabilidad=0.3)
    contenido = imagen_gris(nivel=200)
    resultado = CapaRedNeuronal(configuracion).analizar(contenido, CONTEXTO)
    predictor = PredictorOnnx(tmp_path / "registro" / "v1.0.0" / "modelo.onnx")
    with Image.open(io.BytesIO(contenido)) as imagen:
        esperada = predictor.predecir(imagen).probabilidad_sintetica
    assert resultado.detalle["probabilidad"] == pytest.approx(round(esperada, 4))
    assert esperada != pytest.approx(0.3, abs=0.01)


def test_imagen_ilegible_deja_la_capa_no_disponible(tmp_path):
    """RN26: si la imagen no se puede leer, la capa se informa como no disponible."""
    capa = CapaRedNeuronal(_configuracion(tmp_path))
    with pytest.raises(CapaNoDisponible, match="No se pudo leer la imagen"):
        capa.analizar(b"no es una imagen", CONTEXTO)


def test_sin_modelo_configurado_la_capa_no_esta_disponible():
    """CA7: sin configuración, el motivo llega como capa no disponible."""
    capa = CapaRedNeuronal({"MODELO_RED_NEURONAL_REGISTRO": "", "MODELO_RED_NEURONAL_VERSION": ""})
    with pytest.raises(CapaNoDisponible, match="todavía no está configurado"):
        capa.analizar(imagen_gris(), CONTEXTO)


def test_version_no_carga_el_modelo():
    """RN29: la versión se informa al crear el análisis sin bajar el modelo."""
    assert CapaRedNeuronal({"MODELO_RED_NEURONAL_VERSION": "1.0.0"}).version().startswith(
        "1.0 (modelo 1.0.0, ONNX Runtime "
    )
    assert "sin configurar" in CapaRedNeuronal({}).version()


def test_la_capa_4_esta_registrada_al_final():
    """ADR-0006: la capa nueva se agrega al registro sin cambiar las anteriores."""
    capas = crear_capas({
        "RUTA_EXIFTOOL": "exiftool", "CARPETA_CONFIANZA_C2PA": "/tmp/x",
        "MODELO_RED_NEURONAL_VERSION": "",
    })
    assert [c.nombre for c in capas] == ["metadatos", "c2pa", "ela", "red_neuronal"]
