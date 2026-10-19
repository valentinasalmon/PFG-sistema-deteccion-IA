"""Pruebas del predictor ONNX (tarea T15)."""

import onnx
import pytest
import torch
from PIL import Image

from clasificador.exportacion.onnx import exportar_onnx
from clasificador.inferencia.predictor import ErrorModelo, MetadatosModelo, PredictorOnnx
from clasificador.inferencia.preprocesamiento import preprocesar
from clasificador.modelo.arquitecturas import crear_modelo
from pruebas.exportacion.utilidades import METADATOS


@pytest.fixture(scope="module")
def ruta_modelo(tmp_path_factory):
    """Modelo diminuto exportado para las pruebas del predictor."""
    torch.manual_seed(1)
    modelo = crear_modelo("efficientnet_b0", preentrenado=False).eval()
    muestra = preprocesar(Image.new("RGB", (80, 80)), tamanio_recorte=64)
    destino = tmp_path_factory.mktemp("predictor") / "modelo.onnx"
    return exportar_onnx(modelo, METADATOS, destino, muestra).ruta


def test_predecir_devuelve_una_probabilidad_y_la_version(ruta_modelo):
    """La predicción incluye la versión del modelo (RN29)."""
    prediccion = PredictorOnnx(ruta_modelo).predecir(Image.effect_noise((300, 200), 40))
    assert 0.0 <= prediccion.probabilidad_sintetica <= 1.0
    assert prediccion.version_modelo == "0.0.1"


def test_predecir_promedia_los_cinco_recortes(ruta_modelo):
    """La probabilidad es el promedio de los recortes del contrato de entrada."""
    predictor = PredictorOnnx(ruta_modelo)
    imagen = Image.effect_noise((200, 150), 40).convert("RGB")
    recortes = predictor.probabilidades_recortes(preprocesar(imagen, tamanio_recorte=64))
    assert predictor.predecir(imagen).probabilidad_sintetica == pytest.approx(recortes.mean())


def test_un_modelo_inexistente_falla(tmp_path):
    """Se informa la ruta que no existe."""
    with pytest.raises(ErrorModelo, match="no existe"):
        PredictorOnnx(tmp_path / "nada.onnx")


def test_un_modelo_sin_metadatos_falla(ruta_modelo, tmp_path):
    """Un ONNX ajeno, sin los metadatos del clasificador, se rechaza."""
    grafo = onnx.load(str(ruta_modelo))
    del grafo.metadata_props[:]
    ajeno = tmp_path / "ajeno.onnx"
    onnx.save_model(grafo, str(ajeno))
    with pytest.raises(ErrorModelo, match="metadatos"):
        PredictorOnnx(ajeno)


def test_los_metadatos_van_y_vuelven_como_texto():
    """La serialización a texto conserva todos los valores."""
    assert MetadatosModelo.desde_diccionario(METADATOS.a_diccionario()) == METADATOS
