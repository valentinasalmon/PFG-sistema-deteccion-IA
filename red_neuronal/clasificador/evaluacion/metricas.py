"""Métricas de clasificación, en total y por grupo.

Se reportan exactitud, precisión, exhaustividad, F1, AUC ROC, matriz de
confusión y error de calibración (RNF24 CA3). Las cuatro primeras necesitan
un umbral: se usa 0,5 **solo para reportar**; el sistema no fija un umbral
de decisión porque no emite veredictos (RN27, ADR-0013).

Desempeño por generador: el AUC necesita las dos clases, así que para cada
generador se comparan sus imágenes contra **todas las reales** del mismo
conjunto. Responde a la pregunta "¿qué tan bien separa el modelo las
imágenes de este generador de las fotografías reales?".

Realiza: RNF24 CA3; CA5, CA11 a CA13 de la funcionalidad 010.
"""

import math
from collections.abc import Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from clasificador.entrenamiento.calibracion import error_calibracion_esperado
from clasificador.entrenamiento.entrenador import auc_seguro

UMBRAL_REPORTE = 0.5


def calcular_metricas(
    etiquetas: Sequence[int], probabilidades: Sequence[float], umbral: float = UMBRAL_REPORTE
) -> dict:
    """Todas las métricas de un conjunto de predicciones.

    El AUC es ``None`` cuando no es calculable (una sola clase presente).
    """
    etiquetas = np.asarray(etiquetas, dtype=int)
    probabilidades = np.asarray(probabilidades, dtype=float)
    predicciones = (probabilidades >= umbral).astype(int)
    auc = auc_seguro(etiquetas, probabilidades)
    negativos_verdaderos, falsos_positivos, falsos_negativos, positivos_verdaderos = (
        confusion_matrix(etiquetas, predicciones, labels=[0, 1]).ravel().tolist()
    )
    return {
        "cantidad": int(len(etiquetas)),
        "reales": int((etiquetas == 0).sum()),
        "sinteticas": int((etiquetas == 1).sum()),
        "exactitud": float(accuracy_score(etiquetas, predicciones)),
        "precision": float(precision_score(etiquetas, predicciones, zero_division=0)),
        "exhaustividad": float(recall_score(etiquetas, predicciones, zero_division=0)),
        "f1": float(f1_score(etiquetas, predicciones, zero_division=0)),
        "auc": None if math.isnan(auc) else auc,
        "ece": error_calibracion_esperado(probabilidades, etiquetas),
        "matriz_confusion": {
            "negativos_verdaderos": negativos_verdaderos,
            "falsos_positivos": falsos_positivos,
            "falsos_negativos": falsos_negativos,
            "positivos_verdaderos": positivos_verdaderos,
        },
    }


def metricas_por_generador(
    etiquetas: Sequence[int], probabilidades: Sequence[float], generadores: Sequence[str]
) -> dict[str, dict]:
    """Métricas de cada generador frente a todas las imágenes reales."""
    etiquetas = np.asarray(etiquetas, dtype=int)
    probabilidades = np.asarray(probabilidades, dtype=float)
    generadores = np.asarray(generadores)
    reales = etiquetas == 0
    resultado = {}
    for generador in sorted(set(generadores[etiquetas == 1].tolist())):
        seleccion = reales | ((etiquetas == 1) & (generadores == generador))
        resultado[generador] = calcular_metricas(etiquetas[seleccion], probabilidades[seleccion])
    return resultado


def metricas_por_grupo(
    etiquetas: Sequence[int], probabilidades: Sequence[float], grupos: Sequence[str]
) -> dict[str, dict]:
    """Métricas de cada grupo por separado (por ejemplo, por variante)."""
    etiquetas = np.asarray(etiquetas, dtype=int)
    probabilidades = np.asarray(probabilidades, dtype=float)
    grupos = np.asarray(grupos)
    return {
        grupo: calcular_metricas(etiquetas[grupos == grupo], probabilidades[grupos == grupo])
        for grupo in sorted(set(grupos.tolist()))
    }
