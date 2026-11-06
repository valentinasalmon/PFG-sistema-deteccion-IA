"""Modelo ONNX diminuto para probar la capa 4 sin PyTorch (funcionalidad 012).

Tiene la misma entrada, la misma salida y los mismos metadatos que el modelo
real de la funcionalidad 010 (contrato de ADR-0015), pero en lugar de una red
calcula ``sigmoide(pendiente · brillo_medio + desplazamiento)``. Con la
pendiente en 0 devuelve una probabilidad fija; con pendiente distinta de 0, la
probabilidad depende de la imagen.
"""
import json
import math

import numpy as np
import onnx
from onnx import TensorProto, helper

from clasificador.datos.manifiesto import huella_archivo
from clasificador.registro.registro_modelos import ARCHIVO_HUELLAS, ARCHIVO_MODELO

HUELLA_MANIFIESTO = "9ad6794031e1d1fdac773a927a364d6f96e66451266c234eb1a4e385f929c480"


def logit(probabilidad):
    """Desplazamiento que hace que el modelo devuelva esa probabilidad con pendiente 0."""
    return math.log(probabilidad / (1 - probabilidad))


def armar_modelo(ruta, probabilidad=0.8, pendiente=0.0, version="1.0.0"):
    """Escribe el ONNX en ``ruta`` y la devuelve."""
    nodos = [
        helper.make_node("ReduceMean", ["entrada"], ["media"], axes=[1, 2, 3], keepdims=0),
        helper.make_node("Mul", ["media", "pendiente"], ["escalada"]),
        helper.make_node("Add", ["escalada", "desplazamiento"], ["logit"]),
        helper.make_node("Sigmoid", ["logit"], ["plana"]),
        helper.make_node("Unsqueeze", ["plana", "eje"], ["probabilidad"]),
    ]
    constantes = [
        helper.make_tensor("pendiente", TensorProto.FLOAT, [], [pendiente]),
        helper.make_tensor("desplazamiento", TensorProto.FLOAT, [], [logit(probabilidad)]),
        helper.make_tensor("eje", TensorProto.INT64, [1], [1]),
    ]
    grafo = helper.make_graph(
        nodos, "capa4_diminuta",
        [helper.make_tensor_value_info("entrada", TensorProto.FLOAT, ["N", 3, 224, 224])],
        [helper.make_tensor_value_info("probabilidad", TensorProto.FLOAT, ["N", 1])],
        initializer=constantes,
    )
    modelo = helper.make_model(grafo, opset_imports=[helper.make_opsetid("", 17)])
    modelo.ir_version = 8
    metadatos = {
        "version": version,
        "arquitectura": "diminuta_de_prueba",
        "temperatura": "2.36",
        "tamanio_recorte": "224",
        "media": json.dumps([0.485, 0.456, 0.406]),
        "desvio": json.dumps([0.229, 0.224, 0.225]),
        "huella_manifiesto": HUELLA_MANIFIESTO,
        "commit": "0ee4e9e5a59ab24c234b4f4308def6c575d03e2f",
    }
    onnx.helper.set_model_props(modelo, metadatos)
    onnx.checker.check_model(modelo)
    onnx.save(modelo, str(ruta))
    return ruta


def armar_registro(raiz, version="1.0.0", **opciones):
    """Paquete publicado en un registro local: ``<raiz>/v<versión>/`` con sus huellas."""
    carpeta = raiz / f"v{version}"
    carpeta.mkdir(parents=True)
    modelo = armar_modelo(carpeta / ARCHIVO_MODELO, version=version, **opciones)
    (carpeta / ARCHIVO_HUELLAS).write_text(
        json.dumps({ARCHIVO_MODELO: huella_archivo(modelo)}), encoding="utf-8"
    )
    return raiz


def imagen_gris(nivel=128, tamanio=(320, 240)):
    """Imagen uniforme, en bytes JPEG."""
    import io  # pylint: disable=import-outside-toplevel

    from PIL import Image  # pylint: disable=import-outside-toplevel

    salida = io.BytesIO()
    Image.fromarray(np.full((tamanio[1], tamanio[0], 3), nivel, np.uint8)).save(salida, "JPEG")
    return salida.getvalue()
