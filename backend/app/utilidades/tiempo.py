"""Manejo uniforme de fechas y horas.

Todas las fechas se guardan en UTC y sin zona horaria (naive), para que se
comporten igual en PostgreSQL y en SQLite (pruebas). La conversión a la hora
de Argentina se hace solo al mostrarlas.
"""
from datetime import datetime, timezone


def ahora_utc():
    """Devuelve la fecha y hora actual en UTC, sin información de zona horaria."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
