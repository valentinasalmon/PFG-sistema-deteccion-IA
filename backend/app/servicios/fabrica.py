"""Construcción de los servicios con sus dependencias reales.

Las rutas solo conocen estas funciones: así no importan repositorios ni
integraciones (RNF17) y las pruebas pueden armar los servicios con dobles.
"""
from app.repositorios.repositorio_usuarios import RepositorioUsuarios
from app.servicios.servicio_correos import ServicioCorreos
from app.servicios.servicio_cuentas import ServicioCuentas
from app.servicios.servicio_perfil import ServicioPerfil
from app.servicios.servicio_sesion import ServicioSesion
from app.servicios.tokens import GestorTokens


def _correos(configuracion, enviador):
    return ServicioCorreos(enviador, configuracion["URL_FRONTEND"])


def crear_servicio_cuentas(configuracion, enviador):
    """Servicio de registro, verificación y recuperación."""
    return ServicioCuentas(
        RepositorioUsuarios(), _correos(configuracion, enviador),
        GestorTokens(configuracion["SECRET_KEY"]), configuracion,
    )


def crear_servicio_sesion(configuracion, enviador):
    """Servicio de autenticación."""
    return ServicioSesion(RepositorioUsuarios(), _correos(configuracion, enviador), configuracion)


def crear_servicio_perfil(configuracion, enviador):
    """Servicio del perfil propio."""
    return ServicioPerfil(
        RepositorioUsuarios(), _correos(configuracion, enviador),
        GestorTokens(configuracion["SECRET_KEY"]), configuracion,
    )
