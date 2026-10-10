"""Pruebas de los tokens firmados (RNF01 CA5)."""
from datetime import timedelta

import pytest

from app.servicios.errores import TokenInvalido
from app.servicios.tokens import GestorTokens


def test_token_valido_devuelve_los_datos():
    """Un token recién generado se lee correctamente."""
    gestor = GestorTokens("clave")
    token = gestor.generar("proposito", {"id": 7})
    assert gestor.leer("proposito", token, timedelta(hours=1)) == {"id": 7}


def test_token_alterado_se_rechaza():
    """Modificar un token invalida la firma."""
    gestor = GestorTokens("clave")
    token = gestor.generar("proposito", {"id": 7})
    with pytest.raises(TokenInvalido, match="no es válido"):
        gestor.leer("proposito", token[:-2] + "xx", timedelta(hours=1))


def test_token_de_otro_proposito_se_rechaza():
    """Un token de verificación no sirve como token de recuperación."""
    gestor = GestorTokens("clave")
    token = gestor.generar("verificacion", {"id": 7})
    with pytest.raises(TokenInvalido):
        gestor.leer("recuperacion", token, timedelta(hours=1))


def test_token_vencido_se_rechaza():
    """Un token más antiguo que la vigencia se rechaza."""
    gestor = GestorTokens("clave")
    token = gestor.generar("proposito", {"id": 7})
    with pytest.raises(TokenInvalido, match="venció"):
        gestor.leer("proposito", token, timedelta(seconds=-1))
