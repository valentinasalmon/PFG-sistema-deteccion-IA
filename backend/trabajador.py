"""Proceso trabajador de RQ que ejecuta los análisis y envía los correos (ADR-0004).

Uso (con el entorno virtual activo y ``COLA_ANALISIS=rq``)::

    python trabajador.py

En el desarrollo no hace falta: la cola por defecto ejecuta los análisis en
un hilo del servidor (ADR-0013). En producción lo levanta un servicio de
systemd.

Atiende primero la cola ``correos`` (así un correo no espera detrás de un
análisis largo) y después la de ``analisis``. El planificador de RQ ejecuta los
reintentos de los correos (RF47 CA3).

Realiza: RF38, RF46, RF47 (CA1, CA3); RNF13.
"""
import redis
from rq import Worker

from app import crear_app


def main():
    """Crea la aplicación y atiende las colas ``correos`` y ``analisis`` en su contexto."""
    aplicacion = crear_app()
    conexion = redis.Redis.from_url(aplicacion.config["URL_REDIS"])
    with aplicacion.app_context():
        Worker(["correos", "analisis"], connection=conexion).work(with_scheduler=True)


if __name__ == "__main__":
    main()
