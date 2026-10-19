"""Datos de origen de la solicitud que se registran en la auditoría.

Los servicios no conocen Flask (RNF17): las rutas arman este diccionario y
lo pasan a la fábrica de servicios.

Detrás de Nginx (funcionalidad 017), ``crear_app`` aplica ``ProxyFix`` con la
cantidad exacta de proxies (``PROXIES_DE_CONFIANZA``), así ``remote_addr`` es
la dirección real del cliente y no se aceptan cabeceras falsificadas.

Realiza: RNF06 (CA2, dirección IP de origen).
"""
from flask import request


def origen_de_la_solicitud():
    """Devuelve ``{"ip": ...}`` con la dirección IP de la solicitud actual."""
    return {"ip": request.remote_addr}
