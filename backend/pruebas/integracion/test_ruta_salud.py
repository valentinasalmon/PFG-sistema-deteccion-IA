"""Pruebas de la ruta GET /api/salud (CA2 y CA3 de la funcionalidad 001)."""
from app.integraciones.cliente_redis import ClienteRedis


def test_salud_responde_200_si_todo_funciona(cliente, monkeypatch):
    """CA2: con base de datos y Redis disponibles, la respuesta es 200."""
    monkeypatch.setattr(ClienteRedis, "verificar_conexion", lambda self: True)
    respuesta = cliente.get("/api/salud")
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["estado"] == "ok"
    assert datos["componentes"] == {"api": "ok", "base_de_datos": "ok", "redis": "ok"}
    assert datos["entorno"] == "pruebas"
    assert "version" in datos


def test_salud_responde_503_si_redis_no_responde(cliente, monkeypatch):
    """CA3: si un componente no responde, la respuesta es 503 e indica cuál."""
    monkeypatch.setattr(ClienteRedis, "verificar_conexion", lambda self: False)
    respuesta = cliente.get("/api/salud")
    assert respuesta.status_code == 503
    datos = respuesta.get_json()
    assert datos["estado"] == "degradado"
    assert datos["componentes"]["redis"] == "error"