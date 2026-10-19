"""Proceso trabajador de RQ que ejecuta los análisis (ADR-0004).

Uso (con el entorno virtual activo y ``COLA_ANALISIS=rq``)::

    python trabajador.py

En el desarrollo no hace falta: la cola por defecto ejecuta los análisis en
un hilo del servidor (ADR-0013). En producción lo levanta un servicio de
systemd.

Realiza: RF38, RF46; RNF13.
"""
import redis
from rq import Worker

from app import crear_app


def main():
    """Crea la aplicación y atiende la cola ``analisis`` dentro de su contexto."""
    aplicacion = crear_app()
    conexion = redis.Redis.from_url(aplicacion.config["URL_REDIS"])
    with aplicacion.app_context():
        Worker(["analisis"], connection=conexion).work()


if __name__ == "__main__":
    main()
