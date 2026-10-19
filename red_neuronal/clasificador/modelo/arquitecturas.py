"""Fábrica de modelos y envoltorio exportable.

Todas las arquitecturas se crean con timm, que ofrece cientos de redes
preentrenadas con la misma interfaz. Cambiar EfficientNet-B0 por
ConvNeXt-Tiny para un experimento es cambiar un nombre en la configuración
(patrón Factory).

El modelo de entrenamiento devuelve un *logit* (un número real sin acotar),
que es lo que necesita la función de pérdida. El ``ModeloExportable``
agrega la temperatura de calibración y la sigmoide, para que el grafo ONNX
devuelva directamente una probabilidad en [0, 1].

Realiza: RF42, RNF24 CA1; CA14 de la funcionalidad 010.
"""

import timm
import torch
from torch import nn

ARQUITECTURAS_ADMITIDAS = ("efficientnet_b0", "convnext_tiny", "resnet50")


class ErrorArquitectura(Exception):
    """Se pidió una arquitectura que el proyecto no admite."""


def crear_modelo(nombre: str, preentrenado: bool = True) -> nn.Module:
    """Crea una red con una única salida (el *logit* de la clase sintética).

    ``preentrenado=True`` descarga los pesos de ImageNet (transferencia de
    aprendizaje); las pruebas usan ``False`` para no acceder a la red.
    """
    if nombre not in ARQUITECTURAS_ADMITIDAS:
        raise ErrorArquitectura(
            f"arquitectura '{nombre}' no admitida; opciones: {', '.join(ARQUITECTURAS_ADMITIDAS)}"
        )
    return timm.create_model(nombre, pretrained=preentrenado, num_classes=1)


class ModeloExportable(nn.Module):
    """Modelo calibrado que devuelve probabilidades: ``sigmoide(logit / T)``.

    La temperatura ``T`` se ajusta después del entrenamiento sobre la
    partición de validación (T13). Con ``T > 1`` las probabilidades se
    vuelven menos extremas, lo que corrige el exceso de confianza típico de
    las redes profundas.
    """

    def __init__(self, modelo: nn.Module, temperatura: float = 1.0) -> None:
        super().__init__()
        if temperatura <= 0:
            raise ValueError("la temperatura debe ser positiva")
        self.modelo = modelo
        self.register_buffer("temperatura", torch.tensor(float(temperatura)))

    def forward(self, entrada: torch.Tensor) -> torch.Tensor:  # nombre impuesto por PyTorch
        """Devuelve la probabilidad calibrada de cada imagen, forma ``[N, 1]``."""
        return torch.sigmoid(self.modelo(entrada) / self.temperatura)
