"""Pruebas del evaluador (tarea T16)."""

import json

import pytest
import torch
from PIL import Image

from clasificador.datos.manifiesto import RegistroImagen
from clasificador.evaluacion.evaluador import evaluar
from clasificador.exportacion.onnx import exportar_onnx
from clasificador.inferencia.predictor import PredictorOnnx
from clasificador.inferencia.preprocesamiento import preprocesar
from clasificador.modelo.arquitecturas import crear_modelo
from pruebas.exportacion.utilidades import METADATOS


@pytest.fixture(scope="module")
def predictor(tmp_path_factory):
    """Predictor sobre un modelo diminuto sin entrenar."""
    torch.manual_seed(2)
    modelo = crear_modelo("efficientnet_b0", preentrenado=False).eval()
    muestra = preprocesar(Image.new("RGB", (80, 80)), tamanio_recorte=64)
    ruta = tmp_path_factory.mktemp("evaluador") / "modelo.onnx"
    return PredictorOnnx(exportar_onnx(modelo, METADATOS, ruta, muestra).ruta)


def test_evaluar_produce_metricas_predicciones_y_graficos(
    predictor, directorio_imagenes, tmp_path
):
    """Se guardan los tres tipos de salida con todos los grupos."""
    registros = [
        RegistroImagen(
            "0" * 64, str(i.ruta.relative_to(tmp_path)), i.clase, "prueba", i.generador,
            "prueba", "whatsapp" if indice % 2 else "original",
        )
        for indice, i in enumerate(directorio_imagenes)
    ]
    salida = tmp_path / "evaluacion"
    informe = evaluar(predictor, registros, tmp_path, salida)

    assert informe.total["cantidad"] == 40
    assert set(informe.por_generador) == {"generador_a", "generador_b"}
    assert set(informe.por_variante) == {"original", "whatsapp"}
    guardado = json.loads((salida / "metricas.json").read_text(encoding="utf-8"))
    assert guardado["version_modelo"] == "0.0.1"
    assert guardado["umbral_reporte"] == 0.5
    lineas = (salida / "predicciones.csv").read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 41
    assert (salida / "curva_roc.png").is_file()
    assert (salida / "matriz_confusion.png").is_file()


def test_evaluar_con_una_sola_clase_no_genera_curva_roc(predictor, directorio_imagenes, tmp_path):
    """Sin las dos clases no hay curva ROC, pero sí matriz y métricas."""
    registros = [
        RegistroImagen("0" * 64, str(i.ruta.relative_to(tmp_path)), 0, "p", "real", "prueba")
        for i in directorio_imagenes if i.clase == 0
    ]
    salida = tmp_path / "solo_reales"
    informe = evaluar(predictor, registros, tmp_path, salida)
    assert informe.total["auc"] is None
    assert not (salida / "curva_roc.png").exists()
    assert (salida / "matriz_confusion.png").is_file()
