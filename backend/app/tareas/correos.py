"""Trabajo de la cola que entrega un correo (funcionalidad 013).

Lo ejecuta el proceso trabajador (cola ``correos``) dentro de un contexto de
aplicación. Si el servidor de correo falla, la excepción se propaga para que
la cola lo reintente (RF47 CA3).

Realiza: RF47 (CA1, CA3).
"""
from flask import current_app

from app.integraciones.correo import Correo


def entregar_correo(datos):
    """Entrega el correo descrito por ``datos`` (destinatario, asunto, texto y html)."""
    current_app.extensions["enviador_directo"].entregar(Correo(**datos))
