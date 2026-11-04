"""Pruebas de la exportación a ONNX (tarea T15)."""

from dataclasses import replace

import numpy as np
import pytest
import torch
from PIL import Image

from clasificador.exportacion import onnx as modulo_onnx
from clasificador.exportacion.onnx import ErrorExportacion, exportar_onnx
from clasificador.inferencia.predictor import PredictorOnnx
from clasificador.inferencia.preprocesamiento import preprocesar
from clasificador.modelo.arquitecturas import ModeloExportable, crear_modelo
from pruebas.exportacion.utilidades import METADATOS


@pytest.fixture(scope="module")
def modelo():
    """EfficientNet-B0 sin preentrenar, con pesos fijos por semilla."""
    torch.manual_seed(0)
    return crear_modelo("efficientnet_b0", preentrenado=False).eval()


@pytest.fixture(scope="module")
def muestra():
    """Cinco recortes de 64 px de una imagen de ruido."""
    imagen = Image.effect_noise((128, 96), 60).convert("RGB")
    return preprocesar(imagen, tamanio_recorte=64)


@pytest.fixture(scope="module")
def exportado(modelo, muestra, tmp_path_factory):
    """Modelo exportado una sola vez para todas las pruebas del módulo."""
    destino = tmp_path_factory.mktemp("onnx") / "modelo.onnx"
    return exportar_onnx(modelo, METADATOS, destino, muestra)


def test_la_exportacion_coincide_con_pytorch(exportado):
    """La diferencia máxima queda dentro de la tolerancia y se mide la latencia."""
    assert exportado.diferencia_maxima <= 1e-3
    assert exportado.latencia_ms_por_imagen > 0


def test_el_modelo_es_un_unico_archivo(exportado):
    """No quedan pesos en un archivo .data aparte."""
    assert exportado.ruta.is_file()
    assert list(exportado.ruta.parent.glob("*.data")) == []


def test_los_metadatos_viajan_en_el_archivo(exportado):
    """El predictor lee la versión y el preprocesamiento del propio modelo."""
    predictor = PredictorOnnx(exportado.ruta)
    assert predictor.metadatos == METADATOS
    assert predictor.version == "0.0.1"


def test_el_lote_es_variable(exportado, modelo, muestra):
    """El grafo acepta lotes de 1 y de 5 recortes con la misma salida que PyTorch."""
    predictor = PredictorOnnx(exportado.ruta)
    exportable = ModeloExportable(modelo, METADATOS.temperatura).eval()
    with torch.no_grad():
        esperado = exportable(torch.from_numpy(muestra)).numpy().ravel()
    uno = predictor.probabilidades_recortes(muestra[:1])
    cinco = predictor.probabilidades_recortes(muestra)
    np.testing.assert_allclose(uno, esperado[:1], atol=1e-4)
    np.testing.assert_allclose(cinco, esperado, atol=1e-4)


def test_una_diferencia_excesiva_hace_fallar_la_exportacion(
    modelo, muestra, tmp_path, monkeypatch
):
    """Si ONNX no reproduce a PyTorch, la exportación se rechaza."""
    original = PredictorOnnx.probabilidades_recortes
    monkeypatch.setattr(
        modulo_onnx.PredictorOnnx,
        "probabilidades_recortes",
        lambda self, entrada: original(self, entrada) + 0.01,
    )
    with pytest.raises(ErrorExportacion, match="difiere"):
        exportar_onnx(modelo, replace(METADATOS), tmp_path / "m.onnx", muestra)
