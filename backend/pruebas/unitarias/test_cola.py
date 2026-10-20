"""Pruebas de las implementaciones de la cola de trabajos (ADR-0013)."""
import threading

import pytest

from app.integraciones import cola as modulo_cola
from app.integraciones.cola import ColaEnHilo, ColaRQ, ColaSincronica, crear_cola, resolver

EJECUCIONES = []
LISTO = threading.Event()


def trabajo_de_prueba(valor):
    """Trabajo que registra su ejecución (se encola por su ruta de importación)."""
    EJECUCIONES.append(valor)
    LISTO.set()


RUTA = f"{__name__}.trabajo_de_prueba"


@pytest.fixture(autouse=True)
def limpiar():
    """Cada prueba empieza sin ejecuciones registradas."""
    EJECUCIONES.clear()
    LISTO.clear()


def test_resolver_busca_la_funcion_por_su_ruta():
    """El trabajo se indica por su ruta de importación, como en RQ."""
    assert resolver(RUTA) is trabajo_de_prueba


def test_la_cola_sincronica_ejecuta_en_el_momento():
    """Pruebas: el trabajo ya terminó al volver de ``encolar``."""
    assert ColaSincronica().encolar(RUTA, 7) == "sincronico"
    assert EJECUCIONES == [7]


def test_la_cola_en_hilo_ejecuta_en_segundo_plano_con_contexto(aplicacion):
    """Desarrollo: el trabajo corre en otro hilo, dentro de un contexto de aplicación."""
    nombre = ColaEnHilo(aplicacion).encolar(RUTA, 3)
    assert nombre.startswith("trabajo-")
    assert LISTO.wait(5)
    assert EJECUCIONES == [3]


def test_la_cola_en_hilo_registra_las_fallas(aplicacion, caplog, monkeypatch):
    """Una excepción del trabajo queda en el log y no se propaga."""
    monkeypatch.setattr(modulo_cola.registro, "disabled", False)

    def fallar(_valor):
        LISTO.set()
        raise RuntimeError("falla")

    monkeypatch.setattr(f"{__name__}.trabajo_de_prueba", fallar)
    ColaEnHilo(aplicacion).encolar(RUTA, 1)
    assert LISTO.wait(5)
    for hilo in threading.enumerate():
        if hilo.name.startswith("trabajo-"):
            hilo.join(5)
    assert "Falló el trabajo en segundo plano" in caplog.text


def test_la_cola_rq_encola_por_nombre(monkeypatch):
    """Producción: RQ recibe la ruta del trabajo y sus argumentos."""
    encolados = []

    class ColaFalsa:  # pylint: disable=too-few-public-methods
        """Reemplazo de ``rq.Queue`` que no necesita Redis."""

        def __init__(self, nombre, connection, default_timeout):
            self.nombre, self.conexion, self.tiempo = nombre, connection, default_timeout

        def enqueue(self, trabajo, *argumentos):
            """Registra el trabajo encolado."""
            encolados.append((self.nombre, trabajo, argumentos))
            return type("Trabajo", (), {"id": "abc"})()

    monkeypatch.setattr("rq.Queue", ColaFalsa)
    assert ColaRQ("conexion").encolar(RUTA, 5) == "abc"
    assert encolados == [("analisis", RUTA, (5,))]


def test_crear_cola_segun_la_configuracion(aplicacion, monkeypatch):
    """``COLA_ANALISIS`` elige la implementación."""
    monkeypatch.setattr("rq.Queue", lambda *a, **k: None)
    aplicacion.config["COLA_ANALISIS"] = "sincronica"
    assert isinstance(crear_cola(aplicacion), ColaSincronica)
    aplicacion.config["COLA_ANALISIS"] = "hilo"
    assert isinstance(crear_cola(aplicacion), ColaEnHilo)
    aplicacion.config["COLA_ANALISIS"] = "rq"
    assert isinstance(crear_cola(aplicacion), ColaRQ)
