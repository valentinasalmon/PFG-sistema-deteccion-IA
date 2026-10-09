"""Pruebas de la fábrica de configuración (RNF22, CA6 de la funcionalidad 001)."""
import pytest

from app.configuracion import (
    ConfiguracionDesarrollo,
    ConfiguracionProduccion,
    ErrorConfiguracion,
    obtener_configuracion,
)


def test_entorno_por_defecto_es_desarrollo(monkeypatch):
    """Sin la variable ENTORNO se usa la configuración de desarrollo."""
    monkeypatch.delenv("ENTORNO", raising=False)
    monkeypatch.setenv("URL_BASE_DATOS", "postgresql+psycopg://u:c@localhost/bd")
    assert isinstance(obtener_configuracion(), ConfiguracionDesarrollo)


def test_entorno_desconocido_lanza_error():
    """Un nombre de entorno inexistente se rechaza con un mensaje claro."""
    with pytest.raises(ErrorConfiguracion, match="Entorno desconocido"):
        obtener_configuracion("inexistente")


def test_produccion_sin_clave_secreta_no_arranca(monkeypatch):
    """CA6: en producción, la falta de la clave secreta impide arrancar."""
    monkeypatch.delenv("CLAVE_SECRETA", raising=False)
    monkeypatch.setenv("URL_BASE_DATOS", "postgresql+psycopg://u:c@servidor/bd")
    monkeypatch.setenv("URL_REDIS", "redis://servidor:6379/0")
    with pytest.raises(ErrorConfiguracion, match="CLAVE_SECRETA"):
        obtener_configuracion("produccion")


def test_produccion_con_todas_las_variables(monkeypatch):
    """Con todas las variables obligatorias, la configuración es válida."""
    monkeypatch.setenv("CLAVE_SECRETA", "una-clave-segura")
    monkeypatch.setenv("URL_BASE_DATOS", "postgresql+psycopg://u:c@servidor/bd")
    monkeypatch.setenv("URL_REDIS", "redis://servidor:6379/0")
    configuracion = obtener_configuracion("produccion")
    assert isinstance(configuracion, ConfiguracionProduccion)
    assert configuracion.DEBUG is False
    assert configuracion.SECRET_KEY == "una-clave-segura"


def test_desarrollo_usa_clave_por_defecto(monkeypatch):
    """En desarrollo, si no hay clave secreta se usa una de desarrollo."""
    monkeypatch.delenv("CLAVE_SECRETA", raising=False)
    monkeypatch.setenv("URL_BASE_DATOS", "postgresql+psycopg://u:c@localhost/bd")
    assert obtener_configuracion("desarrollo").SECRET_KEY == "clave-solo-para-desarrollo"


def test_pruebas_usa_base_en_memoria():
    """Las pruebas nunca usan una base de datos real."""
    configuracion = obtener_configuracion("pruebas")
    assert configuracion.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"
    assert configuracion.TESTING is True
