"""Trabajo de la cola que procesa un análisis.

Es una función de módulo porque RQ la busca por su nombre. Se ejecuta
dentro de un contexto de aplicación: el del trabajador de RQ
(``backend/trabajador.py``), el del hilo de desarrollo o el de la solicitud
en las pruebas.

Realiza: RF38 (CA1), RF46; RNF13.
"""
from flask import current_app


def ejecutar_analisis(id_analisis):
    """Procesa el análisis indicado con el servicio de análisis."""
    # Se importa aquí para evitar una importación circular con la fábrica,
    # que referencia esta función.
    # pylint: disable-next=import-outside-toplevel
    from app.servicios.fabrica import crear_servicio_analisis

    servicio = crear_servicio_analisis(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions["almacenamiento"], current_app.extensions["cola_analisis"],
    )
    servicio.procesar(id_analisis)
