"""Construcción de los servicios con sus dependencias reales.

Las rutas solo conocen estas funciones: así no importan repositorios ni
integraciones (RNF17) y las pruebas pueden armar los servicios con dobles.

Cada fábrica recibe el ``origen`` de la solicitud (por ahora, la dirección
IP) para que la auditoría lo registre sin que los servicios conozcan Flask.
"""
from app.repositorios.catalogo_aseguradoras import CatalogoAseguradoras
from app.repositorios.repositorio_auditoria import RepositorioAuditoria
from app.repositorios.repositorio_casos import RepositorioCasos
from app.repositorios.repositorio_organizaciones import RepositorioOrganizaciones
from app.repositorios.repositorio_usuarios import RepositorioUsuarios
from app.servicios.auditoria import ServicioAuditoria
from app.servicios.servicio_casos import ServicioCasos
from app.servicios.servicio_correos import ServicioCorreos
from app.servicios.servicio_cuentas import ServicioCuentas
from app.servicios.servicio_organizaciones import ServicioOrganizaciones
from app.servicios.servicio_perfil import ServicioPerfil
from app.servicios.servicio_sesion import ServicioSesion
from app.servicios.tokens import GestorTokens


def _correos(configuracion, enviador):
    return ServicioCorreos(enviador, configuracion["URL_FRONTEND"])


def crear_servicio_auditoria(origen=None):
    """Servicio del registro de auditoría (RNF06)."""
    return ServicioAuditoria(RepositorioAuditoria(), origen)


def crear_servicio_cuentas(configuracion, enviador, origen=None):
    """Servicio de registro, verificación y recuperación."""
    return ServicioCuentas(
        RepositorioUsuarios(), _correos(configuracion, enviador),
        GestorTokens(configuracion["SECRET_KEY"]), configuracion,
        crear_servicio_auditoria(origen),
        crear_servicio_organizaciones(configuracion, enviador, origen),
        CatalogoAseguradoras(),
    )


def crear_servicio_sesion(configuracion, enviador, origen=None):
    """Servicio de autenticación."""
    return ServicioSesion(
        RepositorioUsuarios(), _correos(configuracion, enviador), configuracion,
        crear_servicio_auditoria(origen),
        crear_servicio_organizaciones(configuracion, enviador, origen),
    )


def crear_catalogo_aseguradoras():
    """Catálogo de aseguradoras de la SSN (CP-18)."""
    return CatalogoAseguradoras()


def crear_servicio_perfil(configuracion, enviador, origen=None):
    """Servicio del perfil propio."""
    return ServicioPerfil(
        RepositorioUsuarios(), _correos(configuracion, enviador),
        GestorTokens(configuracion["SECRET_KEY"]), configuracion,
        crear_servicio_auditoria(origen),
    )


def crear_servicio_organizaciones(configuracion, enviador, origen=None):
    """Servicio de organizaciones, invitaciones y membresías."""
    return ServicioOrganizaciones(
        RepositorioOrganizaciones(), RepositorioUsuarios(), _correos(configuracion, enviador),
        GestorTokens(configuracion["SECRET_KEY"]), configuracion,
        crear_servicio_auditoria(origen), RepositorioCasos(),
    )


def crear_servicio_casos(configuracion, enviador, origen=None):
    """Servicio de casos y accesos (funcionalidad 005)."""
    return ServicioCasos(
        RepositorioCasos(), RepositorioOrganizaciones(), RepositorioUsuarios(),
        _correos(configuracion, enviador), crear_servicio_auditoria(origen),
    )
