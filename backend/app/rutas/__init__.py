"""Capa de rutas: controladores delgados de la API REST (``/api``)."""
from app.rutas.administracion import administracion_bp
from app.rutas.casos import casos_bp
from app.rutas.catalogos import catalogos_bp
from app.rutas.cuentas import cuentas_bp
from app.rutas.errores import registrar_manejadores
from app.rutas.imagenes import imagenes_bp
from app.rutas.invitaciones import invitaciones_bp
from app.rutas.organizaciones import organizaciones_bp
from app.rutas.perfil import perfil_bp
from app.rutas.salud import salud_bp
from app.rutas.sesion import sesion_bp


def registrar_rutas(aplicacion):
    """Registra todos los blueprints de la API y los manejadores de errores."""
    for blueprint in (
        salud_bp, cuentas_bp, sesion_bp, perfil_bp, organizaciones_bp, invitaciones_bp,
        administracion_bp, catalogos_bp, casos_bp, imagenes_bp,
    ):
        aplicacion.register_blueprint(blueprint)
    registrar_manejadores(aplicacion)
