"""Accesorios (fixtures) compartidos por todas las pruebas de pytest."""
import pytest

from app import crear_app


@pytest.fixture
def aplicacion():
    """Aplicación configurada para el entorno de pruebas."""
    return crear_app("pruebas")


@pytest.fixture
def cliente(aplicacion):  # pylint: disable=redefined-outer-name
    """Cliente HTTP de prueba para invocar la API sin levantar un servidor."""
    return aplicacion.test_client()
