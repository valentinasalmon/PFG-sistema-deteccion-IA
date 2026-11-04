"""Pruebas de la fábrica de modelos (tarea T11)."""

import pytest
import torch

from clasificador.modelo.arquitecturas import ErrorArquitectura, ModeloExportable, crear_modelo


@pytest.fixture(scope="module")
def modelo():
    """EfficientNet-B0 sin pesos preentrenados (sin acceso a la red)."""
    return crear_modelo("efficientnet_b0", preentrenado=False).eval()


def test_el_modelo_devuelve_un_logit_por_imagen(modelo):
    """La salida tiene forma [N, 1]."""
    with torch.no_grad():
        salida = modelo(torch.randn(2, 3, 64, 64))
    assert salida.shape == (2, 1)


def test_el_modelo_exportable_devuelve_probabilidades(modelo):
    """Los valores quedan en [0, 1]."""
    exportable = ModeloExportable(modelo, temperatura=1.5).eval()
    with torch.no_grad():
        salida = exportable(torch.randn(3, 3, 64, 64) * 10)
    assert salida.shape == (3, 1)
    assert torch.all((salida >= 0) & (salida <= 1))


def test_la_temperatura_suaviza_las_probabilidades(modelo):
    """Con mayor temperatura, la probabilidad se acerca a 0,5."""
    entrada = torch.randn(4, 3, 64, 64)
    with torch.no_grad():
        frio = ModeloExportable(modelo, 1.0).eval()(entrada)
        calido = ModeloExportable(modelo, 10.0).eval()(entrada)
    assert torch.all((calido - 0.5).abs() <= (frio - 0.5).abs() + 1e-6)


def test_una_temperatura_no_positiva_se_rechaza(modelo):
    """La temperatura debe ser mayor que cero."""
    with pytest.raises(ValueError, match="positiva"):
        ModeloExportable(modelo, 0.0)


def test_una_arquitectura_desconocida_lanza_error_claro():
    """El error lista las arquitecturas admitidas."""
    with pytest.raises(ErrorArquitectura, match="efficientnet_b0"):
        crear_modelo("red_inventada", preentrenado=False)
