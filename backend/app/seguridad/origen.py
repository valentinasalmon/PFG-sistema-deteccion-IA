"""Datos de origen de la solicitud que se registran en la auditoría.

Los servicios no conocen Flask (RNF17): las rutas arman este diccionario y
lo pasan a la fábrica de servicios.

Detrás de Nginx (funcionalidad 017), ``remote_addr`` es la dirección del
proxy; allí se configurará ``ProxyFix`` con la cantidad exacta de proxies
para obtener la dirección real sin aceptar cabeceras falsificadas.

Realiza: RNF06 (CA2, dirección IP de origen).
"""
from flask import request


def origen_de_la_solicitud():
    """Devuelve ``{"ip": ...}`` con la dirección IP de la solicitud actual."""
    return {"ip": request.remote_addr}
