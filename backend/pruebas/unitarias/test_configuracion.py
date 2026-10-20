"""Pruebas de la fábrica de configuración (RNF22, CA6 de la funcionalidad 001)."""
import pytest
from flask import request

from app import crear_app
from app.configuracion import (
    ConfiguracionDesarrollo,
    ConfiguracionProduccion,
    ErrorConfiguracion,
    obtener_configuracion,
)
from app.seguridad.origen import origen_de_la_solicitud


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
    monkeypatch.setenv("URL_FRONTEND", "https://plataforma.ejemplo.com")
    monkeypatch.setenv("SERVIDOR_CORREO", "email-smtp.eu-west-1.amazonaws.com")
    monkeypatch.setenv("REMITENTE_CORREO", "no-responder@ejemplo.com")
    monkeypatch.setenv("S3_BUCKET", "imagenes-plataforma")
    monkeypatch.setenv("ALMACENAMIENTO", "local")
    configuracion = obtener_configuracion("produccion")
    assert isinstance(configuracion, ConfiguracionProduccion)
    # En producción las imágenes siempre van a S3 cifrado (RNF03).
    assert (configuracion.ALMACENAMIENTO, configuracion.S3_CIFRADO) == ("s3", "AES256")
    assert configuracion.DEBUG is False
    assert configuracion.SECRET_KEY == "una-clave-segura"
    assert configuracion.SESSION_COOKIE_SECURE is True
    # Detrás de Nginx se confía en un único proxy (017) y la región es Irlanda.
    assert (configuracion.PROXIES_DE_CONFIANZA, configuracion.S3_REGION) == (1, "eu-west-1")


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


def test_detras_de_nginx_se_usa_la_ip_real_del_cliente(monkeypatch):
    """017: con un proxy de confianza, la auditoría registra la IP que informa Nginx."""
    monkeypatch.setenv("PROXIES_DE_CONFIANZA", "1")
    aplicacion = crear_app("pruebas")

    @aplicacion.get("/ip-de-prueba")
    def ip_de_prueba():
        return {"ip": origen_de_la_solicitud()["ip"], "esquema": request.scheme}

    respuesta = aplicacion.test_client().get(
        "/ip-de-prueba",
        headers={"X-Forwarded-For": "1.1.1.1, 203.0.113.7", "X-Forwarded-Proto": "https"},
    )

    # Solo se toma la última dirección agregada por el proxy de confianza.
    assert respuesta.get_json() == {"ip": "203.0.113.7", "esquema": "https"}
