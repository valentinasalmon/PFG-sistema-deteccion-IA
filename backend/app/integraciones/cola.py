"""Cola de trabajos en segundo plano (patrón Strategy, ADR-0004 y ADR-0013).

Tres implementaciones con la misma interfaz ``encolar(trabajo, *argumentos)``:

- ``ColaRQ``: producción. Encola en Redis y lo ejecuta el proceso trabajador
  (``backend/trabajador.py``).
- ``ColaEnHilo``: desarrollo. Ejecuta el trabajo en un hilo aparte con su
  propio contexto de aplicación, así no hace falta levantar un trabajador.
- ``ColaSincronica``: pruebas. Ejecuta el trabajo en el momento.

El trabajo se indica por su ruta de importación (``"app.tareas.analisis.
ejecutar_analisis"``), como lo acepta RQ: así quien encola no necesita importar
el trabajo y no se forman importaciones circulares.

Realiza: RF38 (CA1), RF46; RNF13, RNF18 (CA2).
"""
import importlib
import logging
import threading

registro = logging.getLogger(__name__)


def resolver(trabajo):
    """Función a partir de su ruta de importación (``"paquete.modulo.funcion"``)."""
    modulo, _, nombre = trabajo.rpartition(".")
    return getattr(importlib.import_module(modulo), nombre)


class ColaSincronica:
    """Ejecuta cada trabajo en el momento (pruebas)."""

    def encolar(self, trabajo, *argumentos):
        """Ejecuta el trabajo en el momento y devuelve un identificador."""
        resolver(trabajo)(*argumentos)
        return "sincronico"


class ColaEnHilo:
    """Ejecuta cada trabajo en un hilo con su propio contexto de aplicación (desarrollo)."""

    def __init__(self, aplicacion):
        self.aplicacion = aplicacion

    def encolar(self, trabajo, *argumentos):
        """Lanza el trabajo en un hilo y devuelve su nombre."""
        funcion = resolver(trabajo)

        def ejecutar():
            with self.aplicacion.app_context():
                try:
                    funcion(*argumentos)
                except Exception:  # pylint: disable=broad-exception-caught
                    registro.exception("Falló el trabajo en segundo plano %s", trabajo)

        hilo = threading.Thread(target=ejecutar, daemon=True, name=f"trabajo-{funcion.__name__}")
        hilo.start()
        return hilo.name


class ColaRQ:
    """Encola en Redis para el proceso trabajador de RQ (producción)."""

    def __init__(self, conexion, nombre="analisis", tiempo_maximo=1800):
        # Se importa aquí: RQ solo hace falta con esta implementación.
        from rq import Queue  # pylint: disable=import-outside-toplevel

        self.cola = Queue(nombre, connection=conexion, default_timeout=tiempo_maximo)

    def encolar(self, trabajo, *argumentos):
        """Encola el trabajo y devuelve el identificador que le asigna RQ."""
        return self.cola.enqueue(trabajo, *argumentos).id


def crear_cola(aplicacion):
    """Elige la implementación según ``COLA_ANALISIS`` (``rq``, ``hilo`` o ``sincronica``)."""
    tipo = aplicacion.config["COLA_ANALISIS"]
    if tipo == "rq":
        import redis  # pylint: disable=import-outside-toplevel

        return ColaRQ(redis.Redis.from_url(aplicacion.config["URL_REDIS"]))
    if tipo == "hilo":
        return ColaEnHilo(aplicacion)
    return ColaSincronica()
