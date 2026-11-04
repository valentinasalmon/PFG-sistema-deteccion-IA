"""Exportación a ONNX con verificación de coincidencia y medición de latencia.

Pasos:

1. Se envuelve el modelo con la temperatura y la sigmoide
   (``ModeloExportable``), para que el grafo devuelva probabilidades.
2. Se exporta con el exportador de ``torch.export`` (el predeterminado desde
   PyTorch 2.9), con el tamaño de lote variable.
3. Se agregan los metadatos y se guarda como **un único archivo**, para que
   tenga una sola huella SHA-256 en el registro de modelos.
4. Se verifica que ONNX Runtime devuelva lo mismo que PyTorch sobre una
   muestra (diferencia máxima ≤ tolerancia). Si no, la exportación falla.
5. Se mide el tiempo de inferencia por imagen en CPU, con los cinco recortes.

Realiza: RNF24 CA1; CA14 de la funcionalidad 010.
"""

import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnx
import torch
from torch import nn

from clasificador.configuracion import ConfiguracionExportacion
from clasificador.inferencia.predictor import (
    NOMBRE_ENTRADA,
    NOMBRE_SALIDA,
    MetadatosModelo,
    PredictorOnnx,
)
from clasificador.inferencia.preprocesamiento import CANTIDAD_RECORTES
from clasificador.modelo.arquitecturas import ModeloExportable


class ErrorExportacion(Exception):
    """El modelo ONNX no reproduce la salida del modelo original."""


@dataclass(frozen=True)
class ResultadoExportacion:
    """Datos de la exportación que van a la ficha del modelo."""

    ruta: Path
    diferencia_maxima: float
    latencia_ms_por_imagen: float


def _exportar_grafo(exportable: nn.Module, ejemplo: torch.Tensor, opset: int) -> onnx.ModelProto:
    """Exporta a un archivo temporal y devuelve el grafo con los pesos incluidos."""
    with tempfile.TemporaryDirectory() as temporal:
        ruta_temporal = Path(temporal) / "modelo.onnx"
        torch.onnx.export(
            exportable,
            (ejemplo,),
            str(ruta_temporal),
            input_names=[NOMBRE_ENTRADA],
            output_names=[NOMBRE_SALIDA],
            dynamic_shapes=({0: torch.export.Dim("lote", min=1, max=1024)},),
            opset_version=opset,
            dynamo=True,
            verbose=False,
        )
        # onnx.load incorpora los pesos guardados aparte (modelo.onnx.data).
        return onnx.load(str(ruta_temporal))


def medir_latencia(predictor: PredictorOnnx, tamanio: int, repeticiones: int = 10) -> float:
    """Milisegundos por imagen (cinco recortes) en CPU, tras un calentamiento."""
    entrada = np.random.default_rng(0).standard_normal(
        (CANTIDAD_RECORTES, 3, tamanio, tamanio)
    ).astype(np.float32)
    predictor.probabilidades_recortes(entrada)
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        predictor.probabilidades_recortes(entrada)
    return (time.perf_counter() - inicio) * 1000 / repeticiones


def verificar_coincidencia(
    exportable: nn.Module, predictor: PredictorOnnx, muestra: np.ndarray, tolerancia: float
) -> float:
    """Compara ONNX Runtime con PyTorch y falla si difieren más de lo tolerado."""
    with torch.no_grad():
        esperado = exportable(torch.from_numpy(muestra)).numpy().ravel()
    diferencia = float(np.abs(esperado - predictor.probabilidades_recortes(muestra)).max())
    if diferencia > tolerancia:
        raise ErrorExportacion(
            f"la salida ONNX difiere de PyTorch en {diferencia:.2e} (tolerancia {tolerancia:.0e})"
        )
    return diferencia


def exportar_onnx(
    modelo: nn.Module,
    metadatos: MetadatosModelo,
    destino: Path,
    muestra: np.ndarray,
    configuracion: ConfiguracionExportacion | None = None,
) -> ResultadoExportacion:
    """Exporta, verifica y mide el modelo; devuelve el resultado o falla.

    ``muestra`` es un tensor ``[N, 3, alto, ancho]`` ya preprocesado (por
    ejemplo, recortes del conjunto de prueba) para comparar las salidas.
    """
    configuracion = configuracion or ConfiguracionExportacion()
    exportable = ModeloExportable(modelo, metadatos.temperatura).cpu().eval()
    tamanio = metadatos.entrada.tamanio_recorte
    grafo = _exportar_grafo(exportable, torch.zeros(2, 3, tamanio, tamanio), configuracion.opset)
    for clave, valor in metadatos.a_diccionario().items():
        grafo.metadata_props.add(key=clave, value=valor)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    onnx.save_model(grafo, str(destino), save_as_external_data=False)

    predictor = PredictorOnnx(destino)
    diferencia = verificar_coincidencia(exportable, predictor, muestra, configuracion.tolerancia)
    return ResultadoExportacion(destino, diferencia, medir_latencia(predictor, tamanio))
