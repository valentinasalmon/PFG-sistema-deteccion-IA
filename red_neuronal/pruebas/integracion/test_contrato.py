"""Prueba del contrato de inferencia (tarea T22, ADR-0015).

La misma imagen debe dar la misma probabilidad con el predictor ONNX (lo
que usa el backend) y con el modelo de PyTorch más el preprocesamiento
compartido. Si alguien cambia el preprocesamiento en un solo lado, esta
prueba falla.
"""

import pytest
import torch
from PIL import Image

from clasificador.exportacion.onnx import exportar_onnx
from clasificador.inferencia.predictor import PredictorOnnx
from clasificador.inferencia.preprocesamiento import preprocesar
from clasificador.modelo.arquitecturas import ModeloExportable, crear_modelo
from pruebas.exportacion.utilidades import METADATOS


@pytest.mark.parametrize("tamanio", [(90, 70), (300, 200), (1500, 900)])
def test_onnx_y_pytorch_dan_la_misma_probabilidad(tmp_path, tamanio):
    """Diferencia menor a 1e-4 para imágenes chicas, medianas y grandes."""
    torch.manual_seed(4)
    modelo = crear_modelo("efficientnet_b0", preentrenado=False).eval()
    imagen = Image.effect_noise(tamanio, 50).convert("RGB")
    entrada = preprocesar(imagen, tamanio_recorte=METADATOS.entrada.tamanio_recorte)
    ruta = exportar_onnx(modelo, METADATOS, tmp_path / "modelo.onnx", entrada).ruta

    with torch.no_grad():
        esperado = ModeloExportable(modelo, METADATOS.temperatura).eval()(
            torch.from_numpy(entrada)
        ).mean().item()
    obtenido = PredictorOnnx(ruta).predecir(imagen).probabilidad_sintetica
    assert obtenido == pytest.approx(esperado, abs=1e-4)
