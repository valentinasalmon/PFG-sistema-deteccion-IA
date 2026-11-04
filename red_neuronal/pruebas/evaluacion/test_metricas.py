"""Pruebas de las métricas (tarea T16)."""

import pytest

from clasificador.evaluacion.metricas import (
    calcular_metricas,
    metricas_por_generador,
    metricas_por_grupo,
)


def test_separacion_perfecta():
    """Con predicciones perfectas, todas las métricas valen 1."""
    metricas = calcular_metricas([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    assert metricas["auc"] == 1.0
    assert metricas["exactitud"] == metricas["f1"] == 1.0
    assert metricas["matriz_confusion"] == {
        "negativos_verdaderos": 2, "falsos_positivos": 0,
        "falsos_negativos": 0, "positivos_verdaderos": 2,
    }


def test_prediccion_constante_tiene_auc_de_azar():
    """Si el modelo da siempre lo mismo, el AUC es 0,5."""
    assert calcular_metricas([0, 1, 0, 1], [0.7] * 4)["auc"] == 0.5


def test_un_caso_construido_a_mano():
    """Precisión 1/2, exhaustividad 1/2 y exactitud 1/2."""
    metricas = calcular_metricas([0, 0, 1, 1], [0.2, 0.6, 0.4, 0.9])
    assert metricas["precision"] == pytest.approx(0.5)
    assert metricas["exhaustividad"] == pytest.approx(0.5)
    assert metricas["exactitud"] == pytest.approx(0.5)
    assert metricas["auc"] == pytest.approx(0.75)


def test_auc_no_calculable_con_una_sola_clase():
    """El AUC se informa como None, sin fallar."""
    metricas = calcular_metricas([1, 1], [0.3, 0.9])
    assert metricas["auc"] is None
    assert metricas["exhaustividad"] == 0.5


def test_por_generador_compara_contra_todas_las_reales():
    """Cada generador se evalúa con sus imágenes más todas las reales."""
    etiquetas = [0, 0, 1, 1, 1, 1]
    probabilidades = [0.1, 0.2, 0.9, 0.8, 0.15, 0.05]
    generadores = ["real", "real", "gemini", "gemini", "chatgpt", "chatgpt"]
    resultado = metricas_por_generador(etiquetas, probabilidades, generadores)
    assert set(resultado) == {"gemini", "chatgpt"}
    assert resultado["gemini"]["auc"] == 1.0
    assert resultado["gemini"]["cantidad"] == 4
    assert resultado["chatgpt"]["auc"] == pytest.approx(0.25)


def test_por_grupo_separa_cada_variante():
    """Las métricas se calculan por separado para cada variante."""
    resultado = metricas_por_grupo(
        [0, 1, 0, 1], [0.1, 0.9, 0.6, 0.4], ["original", "original", "whatsapp", "whatsapp"]
    )
    assert resultado["original"]["auc"] == 1.0
    assert resultado["whatsapp"]["auc"] == 0.0
