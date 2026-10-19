"""Pruebas de la calibración por temperatura (tarea T13)."""

import numpy as np
import pytest

from clasificador.entrenamiento.calibracion import (
    ajustar_temperatura,
    error_calibracion_esperado,
    sigmoide,
)


def _datos_sobreconfiados(cantidad=2000, semilla=0):
    """Logits bien calibrados multiplicados por 4: el modelo exagera su confianza."""
    aleatorio = np.random.default_rng(semilla)
    logits_reales = aleatorio.normal(0, 1.5, cantidad)
    etiquetas = (aleatorio.random(cantidad) < sigmoide(logits_reales)).astype(int)
    return logits_reales * 4.0, etiquetas


def test_la_temperatura_corrige_la_sobreconfianza():
    """La temperatura ajustada es cercana a 4 y el ECE baja."""
    logits, etiquetas = _datos_sobreconfiados()
    temperatura = ajustar_temperatura(logits, etiquetas)
    antes = error_calibracion_esperado(sigmoide(logits), etiquetas)
    despues = error_calibracion_esperado(sigmoide(logits / temperatura), etiquetas)
    assert temperatura == pytest.approx(4.0, rel=0.2)
    assert despues < antes / 2


def test_la_temperatura_no_cambia_el_orden():
    """Dividir por una constante positiva mantiene el ranking (el AUC no cambia)."""
    logits, etiquetas = _datos_sobreconfiados()
    temperatura = ajustar_temperatura(logits, etiquetas)
    assert np.array_equal(np.argsort(logits), np.argsort(logits / temperatura))


def test_el_ece_de_un_modelo_perfectamente_calibrado_es_bajo():
    """Si la probabilidad es la tasa real, el ECE es casi cero."""
    aleatorio = np.random.default_rng(1)
    probabilidades = aleatorio.random(20000)
    etiquetas = (aleatorio.random(20000) < probabilidades).astype(int)
    assert error_calibracion_esperado(probabilidades, etiquetas) < 0.02


def test_el_ece_de_un_caso_construido_a_mano():
    """Confianza 0,9 y 50 % de aciertos: ECE = 0,4."""
    probabilidades = np.array([0.9, 0.9, 0.1, 0.1])
    etiquetas = np.array([1, 0, 0, 1])
    assert error_calibracion_esperado(probabilidades, etiquetas) == pytest.approx(0.4)


def test_el_ece_incluye_las_predicciones_de_confianza_minima():
    """Una probabilidad exacta de 0,5 cae en el primer intervalo."""
    assert error_calibracion_esperado(np.array([0.5]), np.array([1])) == pytest.approx(0.5)
