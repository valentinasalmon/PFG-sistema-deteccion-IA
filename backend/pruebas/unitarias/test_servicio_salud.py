"""Pruebas del servicio de salud con verificaciones simuladas."""
from app.servicios.servicio_salud import ESTADO_ERROR, ESTADO_OK, ServicioSalud


def test_todos_los_componentes_disponibles():
    """Si todas las verificaciones responden, el estado es saludable."""
    servicio = ServicioSalud({"base_de_datos": lambda: True, "redis": lambda: True})
    estado = servicio.obtener_estado()
    assert estado.saludable
    assert estado.componentes == {"api": ESTADO_OK, "base_de_datos": ESTADO_OK, "redis": ESTADO_OK}


def test_componente_caido_marca_error():
    """CA3: un componente que no responde se informa como error."""
    servicio = ServicioSalud({"base_de_datos": lambda: False, "redis": lambda: True})
    estado = servicio.obtener_estado()
    assert not estado.saludable
    assert estado.componentes["base_de_datos"] == ESTADO_ERROR
    assert estado.componentes["redis"] == ESTADO_OK


def test_excepcion_en_una_verificacion_no_interrumpe_las_demas():
    """Una verificación que lanza una excepción no impide evaluar el resto."""

    def verificacion_que_falla():
        raise RuntimeError("falla inesperada")

    servicio = ServicioSalud({"base_de_datos": verificacion_que_falla, "redis": lambda: True})
    estado = servicio.obtener_estado()
    assert estado.componentes["base_de_datos"] == ESTADO_ERROR
    assert estado.componentes["redis"] == ESTADO_OK