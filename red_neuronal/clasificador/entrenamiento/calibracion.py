"""Calibración de probabilidades por *temperature scaling*.

Una red profunda suele estar sobreconfiada: dice 0,99 cuando acierta el 90 %
de las veces. Como el sistema informa una **probabilidad** (RF42 CA1) y no
un veredicto (RN27), esa probabilidad debe ser honesta. La calibración por
temperatura divide el *logit* por un único número ``T`` ajustado sobre la
partición de validación: no cambia qué imagen tiene más puntaje que otra
(el AUC queda igual), solo cuán extremas son las probabilidades.

El error de calibración esperado (ECE) mide cuánto se aleja la confianza
del modelo de su tasa real de aciertos; se informa antes y después.

Realiza: RF42 CA1, RN27; CA11 de la funcionalidad 010. Ver ADR-0013.
"""

import numpy as np
import torch


def sigmoide(valores: np.ndarray) -> np.ndarray:
    """Función logística, numéricamente estable."""
    return 1.0 / (1.0 + np.exp(-np.clip(valores, -60, 60)))


def ajustar_temperatura(logits: np.ndarray, etiquetas: np.ndarray, iteraciones: int = 100) -> float:
    """Encuentra la temperatura que minimiza la log-verosimilitud negativa.

    Se optimiza el logaritmo de ``T`` para que la temperatura sea siempre
    positiva.
    """
    logits_t = torch.as_tensor(np.asarray(logits, dtype=np.float64))
    etiquetas_t = torch.as_tensor(np.asarray(etiquetas, dtype=np.float64))
    log_temperatura = torch.zeros(1, dtype=torch.float64, requires_grad=True)
    optimizador = torch.optim.LBFGS([log_temperatura], lr=0.1, max_iter=iteraciones)

    def cierre() -> torch.Tensor:
        optimizador.zero_grad()
        perdida = torch.nn.functional.binary_cross_entropy_with_logits(
            logits_t / log_temperatura.exp(), etiquetas_t
        )
        perdida.backward()
        return perdida

    optimizador.step(cierre)
    return float(log_temperatura.exp().item())


def error_calibracion_esperado(
    probabilidades: np.ndarray, etiquetas: np.ndarray, cantidad_intervalos: int = 15
) -> float:
    """ECE para clasificación binaria.

    Las predicciones se agrupan por confianza (la probabilidad de la clase
    elegida) en intervalos iguales; en cada intervalo se compara la
    confianza media con la exactitud real, ponderando por la cantidad de
    imágenes del intervalo.
    """
    probabilidades = np.asarray(probabilidades, dtype=np.float64)
    etiquetas = np.asarray(etiquetas)
    predicciones = (probabilidades >= 0.5).astype(int)
    confianzas = np.where(predicciones == 1, probabilidades, 1.0 - probabilidades)
    aciertos = (predicciones == etiquetas).astype(np.float64)
    bordes = np.linspace(0.5, 1.0, cantidad_intervalos + 1)
    error = 0.0
    for inferior, superior in zip(bordes[:-1], bordes[1:]):
        en_intervalo = (confianzas > inferior) & (confianzas <= superior)
        if inferior == 0.5:
            en_intervalo |= confianzas == 0.5
        if en_intervalo.any():
            diferencia = abs(confianzas[en_intervalo].mean() - aciertos[en_intervalo].mean())
            error += en_intervalo.mean() * diferencia
    return float(error)
