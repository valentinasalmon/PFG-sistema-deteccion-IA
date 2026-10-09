"""Pruebas del adaptador de Redis."""
from app.integraciones.cliente_redis import ClienteRedis


def test_redis_inaccesible_devuelve_false():
    """Si Redis no está disponible, la verificación devuelve False sin lanzar errores."""
    assert ClienteRedis("redis://localhost:1/0").verificar_conexion() is False