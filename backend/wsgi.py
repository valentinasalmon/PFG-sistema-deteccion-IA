"""Punto de entrada WSGI.

Lo usan el servidor de desarrollo (``flask --app wsgi run``) y Gunicorn en
producción (``gunicorn wsgi:aplicacion``). En desarrollo carga el archivo
``.env`` con las variables de entorno.
"""
from dotenv import load_dotenv

load_dotenv()

from app import crear_app  # noqa: E402  pylint: disable=wrong-import-position

aplicacion = crear_app()