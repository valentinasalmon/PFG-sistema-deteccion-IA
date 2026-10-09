"""Prueba de arquitectura: verifica los contratos de capas (RNF17, CA9).

Ejecuta import-linter con los contratos definidos en pyproject.toml. Si una
ruta importa directamente un repositorio, o un servicio importa Flask, la
prueba falla y el detalle de la violación se muestra en la salida.
"""
import os
from pathlib import Path

from importlinter.cli import EXIT_STATUS_SUCCESS, lint_imports

RAIZ_BACKEND = Path(__file__).resolve().parents[2]


def test_contratos_de_capas_se_cumplen(monkeypatch):
    """Todos los contratos de import-linter deben cumplirse."""
    monkeypatch.chdir(RAIZ_BACKEND)
    resultado = lint_imports(
        config_filename=os.fspath(RAIZ_BACKEND / "pyproject.toml"),
        no_cache=True,
        no_logo=True,
    )
    assert resultado == EXIT_STATUS_SUCCESS, "Se violó la arquitectura en capas (ver salida)"
