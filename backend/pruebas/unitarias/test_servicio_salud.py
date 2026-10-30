"""Pruebas del servicio de salud con verificaciones simuladas."""
from datetime import datetime

from app.servicios.servicio_salud import ESTADO_ERROR, ESTADO_OK, ServicioSalud, resumen_del_sello


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


class _RepositorioSellos:
    """Doble del repositorio de salud con un resumen fijo de sellos."""

    def __init__(self, fallidos=0, demorados=0, ultimo=None, falla=False):
        self.datos = {"fallidos": fallidos, "demorados": demorados, "ultimo": ultimo}
        self.falla = falla

    def resumen_sellos(self, demorado_desde):
        """Devuelve el resumen fijo o simula un error de la base."""
        if self.falla:
            raise RuntimeError("base caída")
        return self.datos


def test_sello_desactivado_no_consulta_la_base():
    """Sin sello configurado, se informa desactivado y sin red."""
    assert resumen_del_sello("desactivado", "testnet", _RepositorioSellos(falla=True)) == {
        "modo": "desactivado", "estado": "desactivado", "ultimo": None,
    }


def test_sello_en_hedera_al_dia_informa_red_y_ultimo():
    """Con Hedera y sin pendientes viejos ni fallas, el estado es ok."""
    ultimo = datetime(2026, 10, 30, 12, 0)
    resumen = resumen_del_sello("hedera", "testnet", _RepositorioSellos(ultimo=ultimo))
    assert resumen == {"modo": "hedera", "red": "testnet", "estado": "ok",
                       "ultimo": "2026-10-30T12:00:00"}


def test_sello_con_fallas_y_demoras():
    """Las fallas pesan más que las demoras; un error de la base no rompe la salud."""
    assert resumen_del_sello("hedera", "mainnet", _RepositorioSellos(fallidos=1, demorados=2))[
        "estado"] == "con_fallas"
    assert resumen_del_sello("simulado", "testnet", _RepositorioSellos(demorados=1))[
        "estado"] == "con_demoras"
    assert resumen_del_sello("hedera", "testnet", _RepositorioSellos(falla=True))[
        "estado"] == "error"
