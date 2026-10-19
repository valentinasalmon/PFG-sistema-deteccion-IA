"""Pruebas del entrenador (tarea T12).

Usan EfficientNet-B0 sin pesos preentrenados, recortes de 64 px y las 40
imágenes generadas en memoria: corren en CPU en pocos segundos.
"""

import math

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader

from clasificador.configuracion import ConfiguracionEntrenamiento
from clasificador.datos.aumentacion import TransformacionEvaluacion
from clasificador.datos.conjunto import ConjuntoImagenes
from clasificador.datos.manifiesto import RegistroImagen
from clasificador.entrenamiento.entrenador import (
    NOMBRE_MEJOR,
    NOMBRE_ULTIMO,
    Entrenador,
    OpcionesEjecucion,
    auc_seguro,
    fijar_semillas,
)
from clasificador.modelo.arquitecturas import crear_modelo
from clasificador.seguimiento.experimentos import RegistradorNulo


@pytest.fixture
def cargadores(directorio_imagenes, tmp_path):
    """Cargadores de entrenamiento y validación con recortes de 64 px."""
    registros = [
        RegistroImagen("0" * 64, str(i.ruta.relative_to(tmp_path)), i.clase, "p", i.generador)
        for i in directorio_imagenes
    ]
    conjunto = ConjuntoImagenes(registros, tmp_path, TransformacionEvaluacion(64))
    return (
        DataLoader(conjunto, batch_size=8, shuffle=True),
        DataLoader(conjunto, batch_size=20),
    )


def _entrenador(directorio, epocas=3, paciencia=5):
    fijar_semillas(0)
    configuracion = ConfiguracionEntrenamiento(
        epocas=epocas, tasa_aprendizaje=1e-3, paciencia=paciencia, precision_mixta=True
    )
    modelo = crear_modelo("efficientnet_b0", preentrenado=False)
    opciones = OpcionesEjecucion(dispositivo=torch.device("cpu"))
    return Entrenador(modelo, configuracion, directorio, RegistradorNulo(), opciones)


def test_el_entrenamiento_reduce_la_perdida_y_guarda_el_mejor(cargadores, tmp_path):
    """La pérdida baja, se registran métricas y se guardan los puntos de control."""
    entrenador = _entrenador(tmp_path / "salida")
    resultado = entrenador.entrenar(*cargadores)
    perdidas = [fila["perdida_entrenamiento"] for fila in resultado.historial]
    assert perdidas[-1] < perdidas[0]
    assert resultado.ruta_mejor.is_file()
    assert (tmp_path / "salida" / NOMBRE_ULTIMO).is_file()
    assert 0.0 <= resultado.mejor_auc <= 1.0
    assert len(entrenador.registrador.metricas) == len(resultado.historial)


def test_el_entrenamiento_se_reanuda_desde_el_ultimo_punto(cargadores, tmp_path):
    """Si se corta la sesión, se continúa desde la época siguiente."""
    directorio = tmp_path / "salida"
    _entrenador(directorio, epocas=1).entrenar(*cargadores)
    reanudado = _entrenador(directorio, epocas=2)
    assert reanudado.reanudar()
    assert reanudado.estado.epoca_inicial == 1
    resultado = reanudado.entrenar(*cargadores)
    assert [fila["epoca"] for fila in resultado.historial] == [0, 1]


def test_reanudar_sin_punto_de_control_no_hace_nada(tmp_path):
    """La primera ejecución empieza de cero."""
    assert not _entrenador(tmp_path / "vacio").reanudar()


def test_la_parada_temprana_corta_sin_mejora(cargadores, tmp_path):
    """Con paciencia 1, se detiene cuando el AUC deja de mejorar."""
    entrenador = _entrenador(tmp_path / "salida", epocas=8, paciencia=1)
    entrenador.opciones.maximos_pasos_por_epoca = 0  # sin pasos: el AUC no mejora
    resultado = entrenador.entrenar(*cargadores)
    assert len(resultado.historial) == 2


def test_sin_auc_valido_se_conserva_el_ultimo_modelo(directorio_imagenes, tmp_path):
    """Si la validación tiene una sola clase, igual queda un modelo guardado."""
    reales = [
        RegistroImagen("0" * 64, str(i.ruta.relative_to(tmp_path)), 0, "p", "real")
        for i in directorio_imagenes if i.clase == 0
    ]
    conjunto = ConjuntoImagenes(reales, tmp_path, TransformacionEvaluacion(64))
    cargador = DataLoader(conjunto, batch_size=10)
    resultado = _entrenador(tmp_path / "salida", epocas=1).entrenar(cargador, cargador)
    assert math.isnan(resultado.historial[0]["auc_validacion"])
    assert (tmp_path / "salida" / NOMBRE_MEJOR).is_file()


def test_auc_seguro():
    """AUC 1 con separación perfecta y NaN con una sola clase."""
    assert auc_seguro(np.array([0, 1]), np.array([0.1, 0.9])) == 1.0
    assert math.isnan(auc_seguro(np.array([1, 1]), np.array([0.1, 0.9])))
