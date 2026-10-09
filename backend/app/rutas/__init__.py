"""Capa de rutas: controladores delgados de la API REST (``/api``)."""
from app.rutas.salud import salud_bp


def registrar_rutas(aplicacion):
    """Registra todos los blueprints de la API en la aplicación."""
    aplicacion.register_blueprint(salud_bp)
