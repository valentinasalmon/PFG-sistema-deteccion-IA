"""Pruebas de seguridad transversales: hash de contraseñas y CSRF.

Criterios de aceptación de la funcionalidad 002: CA20 y CA21.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import pytest

from app.configuracion.entornos import ConfiguracionBase

from pruebas.conftest import CONTRASENIA_VALIDA, contar_usuarios, datos_registro, obtener_usuario


def test_contrasenia_guardada_solo_como_hash_bcrypt(aplicacion, cliente):
    """CA20: se guarda el hash bcrypt, nunca el texto."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    hash_guardado = obtener_usuario(aplicacion).hash_contrasenia
    assert hash_guardado.startswith("$2b$")
    assert CONTRASENIA_VALIDA not in hash_guardado


def test_costo_de_bcrypt_en_produccion_es_doce_o_mas(aplicacion, ):
    """CA20: el costo configurado fuera de las pruebas es 12 o mayor."""
    assert ConfiguracionBase.BCRYPT_COSTO >= 12


@pytest.fixture
def cliente_con_csrf(aplicacion):
    """Cliente de una aplicación con la protección CSRF activada, como en producción."""
    aplicacion.config["WTF_CSRF_ENABLED"] = True
    return aplicacion.test_client()


def test_solicitud_sin_token_csrf_se_rechaza(aplicacion, cliente_con_csrf):
    """CA21: modificar datos sin token CSRF devuelve 400 csrf_invalido."""
    respuesta = cliente_con_csrf.post("/api/cuentas/registro", json=datos_registro())
    assert respuesta.status_code == 400
    assert respuesta.get_json()["codigo"] == "csrf_invalido"
    assert contar_usuarios(aplicacion) == 0


def test_solicitud_con_token_csrf_se_acepta(cliente_con_csrf):
    """CA21: con el token en la cabecera X-CSRFToken la solicitud se procesa."""
    token = cliente_con_csrf.get("/api/sesion/csrf").get_json()["csrf"]
    respuesta = cliente_con_csrf.post(
        "/api/cuentas/registro", json=datos_registro(), headers={"X-CSRFToken": token}
    )
    assert respuesta.status_code == 201


def test_consultas_no_requieren_token_csrf(cliente_con_csrf):
    """Las solicitudes GET no modifican datos y no exigen el token."""
    assert cliente_con_csrf.get("/api/salud").status_code in (200, 503)
