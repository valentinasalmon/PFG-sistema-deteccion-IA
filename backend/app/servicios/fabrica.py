"""Construcción de los servicios con sus dependencias reales.

Las rutas solo conocen estas funciones: así no importan repositorios ni
integraciones (RNF17) y las pruebas pueden armar los servicios con dobles.

Cada fábrica recibe el ``origen`` de la solicitud (por ahora, la dirección
IP) para que la auditoría lo registre sin que los servicios conozcan Flask.
"""
from app.repositorios.catalogo_aseguradoras import CatalogoAseguradoras
from app.analisis.registro import crear_capas
from app.integraciones.google import crear_cliente_google
from app.integraciones.pagos import crear_proveedor_pagos
from app.integraciones.sello_tiempo import crear_sellador, crear_tema_hedera
from app.repositorios.repositorio_analisis import RepositorioAnalisis
from app.repositorios.repositorio_auditoria import RepositorioAuditoria
from app.repositorios.repositorio_casos import RepositorioCasos
from app.repositorios.repositorio_cobros import RepositorioCobros
from app.repositorios.repositorio_enlaces_carga import RepositorioEnlacesCarga
from app.repositorios.repositorio_estadisticas import RepositorioEstadisticas
from app.repositorios.repositorio_imagenes import RepositorioImagenes
from app.repositorios.repositorio_informes import RepositorioInformes
from app.repositorios.repositorio_organizaciones import RepositorioOrganizaciones
from app.repositorios.repositorio_usuarios import RepositorioUsuarios
from app.repositorios.repositorio_versiones import RepositorioVersiones
from app.servicios.auditoria import ServicioAuditoria
from app.servicios.servicio_administracion import ServicioAdministracion
from app.servicios.servicio_analisis import ServicioAnalisis
from app.servicios.servicio_casos import ServicioCasos, TareasDeRetencion
from app.servicios.servicio_correos import ServicioCorreos
from app.servicios.servicio_cuentas import ServicioCuentas
from app.servicios.servicio_datos_personales import ServicioDatosPersonales
from app.servicios.servicio_imagenes import ArchivosDeCasos, ServicioImagenes
from app.servicios.servicio_informes import ServicioInformes
from app.servicios.servicio_organizaciones import ServicioOrganizaciones
from app.servicios.servicio_pagos import ServicioPagos
from app.servicios.servicio_panel import ServicioPanel
from app.servicios.servicio_perfil import ServicioPerfil
from app.servicios.servicio_planes import ServicioPlanes
from app.servicios.servicio_sellos import ServicioSellos
from app.servicios.servicio_versiones import ServicioVersiones
from app.servicios.servicio_enlaces_carga import ServicioEnlacesCarga
from app.servicios.servicio_google import ServicioGoogle
from app.servicios.servicio_sesion import ServicioSesion
from app.servicios.tokens import GestorTokens


# Trabajo de la cola que procesa un análisis, por su ruta de importación (ADR-0013).
TRABAJO_ANALISIS = "app.tareas.analisis.ejecutar_analisis"


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


def crear_servicio_google(configuracion, enviador, origen=None):
    """Servicio de inicio de sesión y registro con Google (027)."""
    return ServicioGoogle(
        crear_cliente_google(configuracion), RepositorioUsuarios(),
        crear_servicio_cuentas(configuracion, enviador, origen),
        crear_servicio_sesion(configuracion, enviador, origen), configuracion,
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


def _archivos(almacenamiento):
    if not almacenamiento:
        return None
    return ArchivosDeCasos(
        RepositorioImagenes(), almacenamiento, RepositorioInformes(), RepositorioAnalisis()
    )


def crear_servicio_pagos(configuracion, origen=None):
    """Cobro del plan por transferencia, hoy simulado con la forma de Cresium (032)."""
    return ServicioPagos(
        RepositorioCobros(), crear_proveedor_pagos(configuracion), configuracion,
        crear_servicio_auditoria(origen),
    )


def crear_servicio_organizaciones(configuracion, enviador, origen=None, almacenamiento=None):
    """Servicio de organizaciones, invitaciones y membresías."""
    return ServicioOrganizaciones(
        RepositorioOrganizaciones(), RepositorioUsuarios(), _correos(configuracion, enviador),
        GestorTokens(configuracion["SECRET_KEY"]), configuracion,
        crear_servicio_auditoria(origen), RepositorioCasos(), _archivos(almacenamiento),
        crear_servicio_pagos(configuracion, origen),
    )


def crear_servicio_casos(configuracion, enviador, origen=None, almacenamiento=None):
    """Servicio de casos y accesos (funcionalidad 005)."""
    return ServicioCasos(
        RepositorioCasos(), RepositorioOrganizaciones(), RepositorioUsuarios(),
        _correos(configuracion, enviador), crear_servicio_auditoria(origen),
        _archivos(almacenamiento),
    )


def crear_servicio_imagenes(configuracion, enviador, almacenamiento, origen=None):
    """Servicio de imágenes de los casos (funcionalidad 006)."""
    return ServicioImagenes(
        RepositorioImagenes(), crear_servicio_casos(configuracion, enviador, origen),
        almacenamiento, configuracion, crear_servicio_auditoria(origen),
        crear_servicio_sellos(configuracion, origen),
    )


def crear_servicio_enlaces_carga(configuracion, enviador, almacenamiento, origen=None):
    """Enlaces de carga desde el celular (funcionalidad 024)."""
    return ServicioEnlacesCarga(
        RepositorioEnlacesCarga(),
        crear_servicio_imagenes(configuracion, enviador, almacenamiento, origen),
        crear_servicio_auditoria(origen),
    )


def crear_servicio_datos_personales(configuracion, enviador, origen=None, almacenamiento=None):
    """Servicio de copia de datos y eliminación de la cuenta (funcionalidad 019)."""
    return ServicioDatosPersonales(
        {
            "usuarios": RepositorioUsuarios(),
            "organizaciones": RepositorioOrganizaciones(),
            "casos": RepositorioCasos(),
            "auditoria": RepositorioAuditoria(),
        },
        crear_servicio_organizaciones(configuracion, enviador, origen, almacenamiento),
        _correos(configuracion, enviador), GestorTokens(configuracion["SECRET_KEY"]),
        configuracion, crear_servicio_auditoria(origen),
    )


def crear_servicio_analisis(configuracion, enviador, almacenamiento, cola, origen=None):
    """Servicio de análisis de imágenes (funcionalidad 007)."""
    return ServicioAnalisis(
        RepositorioAnalisis(), crear_servicio_casos(configuracion, enviador, origen),
        RepositorioImagenes(),
        {
            "capas": crear_capas(configuracion), "cola": cola, "trabajo": TRABAJO_ANALISIS,
            "almacenamiento": almacenamiento,
            "informes": crear_servicio_informes(configuracion, enviador, almacenamiento, origen),
            "planes": crear_servicio_planes(configuracion, enviador, origen),
        },
        _correos(configuracion, enviador), configuracion, crear_servicio_auditoria(origen),
    )


def crear_servicio_informes(configuracion, enviador, almacenamiento, origen=None):
    """Servicio de informes PDF (funcionalidad 008)."""
    return ServicioInformes(
        RepositorioInformes(), crear_servicio_casos(configuracion, enviador, origen),
        almacenamiento, configuracion, crear_servicio_auditoria(origen),
        crear_servicio_sellos(configuracion, origen),
    )


def crear_servicio_panel():
    """Servicio del panel principal (funcionalidad 013)."""
    return ServicioPanel({
        "casos": RepositorioCasos(), "analisis": RepositorioAnalisis(),
        "auditoria": RepositorioAuditoria(), "organizaciones": RepositorioOrganizaciones(),
    })


def crear_servicio_planes(configuracion, enviador, origen=None):
    """Planes, consumo y pago simulado (funcionalidad 014)."""
    return ServicioPlanes(
        crear_servicio_organizaciones(configuracion, enviador, origen), RepositorioEstadisticas(),
        configuracion, crear_servicio_auditoria(origen),
    )


def crear_servicio_administracion(configuracion):
    """Tablero y listados del Administrador (funcionalidad 014)."""
    return ServicioAdministracion(RepositorioEstadisticas(), configuracion)


def crear_tareas_de_retencion(configuracion, enviador, almacenamiento=None, origen=None):
    """Prórroga y tarea diaria de retención de los casos (funcionalidad 015)."""
    return TareasDeRetencion(crear_servicio_casos(configuracion, enviador, origen, almacenamiento))


def crear_tema_de_sellos(red, cuenta, clave):
    """Crea en Hedera el tema donde la plataforma publica las huellas (funcionalidad 023)."""
    return crear_tema_hedera(red, cuenta, clave)


def crear_servicio_sellos(configuracion, origen=None):
    """Sello de tiempo de las imágenes en Hedera (funcionalidades 016 y 023)."""
    return ServicioSellos(
        RepositorioImagenes(), crear_sellador(configuracion), crear_servicio_auditoria(origen),
        RepositorioInformes(), RepositorioVersiones(),
    )


def crear_servicio_versiones(configuracion, origen=None):
    """Registro de las versiones desplegadas en Hedera (funcionalidad 029)."""
    return ServicioVersiones(
        RepositorioVersiones(), crear_servicio_sellos(configuracion, origen),
        crear_servicio_auditoria(origen), configuracion["VERSION_APLICACION"],
    )
