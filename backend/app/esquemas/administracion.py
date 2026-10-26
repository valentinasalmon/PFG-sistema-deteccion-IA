"""Esquemas del tablero, los listados y los planes (funcionalidad 014).

Realiza: RF20, RF21, RF22.
"""
from datetime import date, datetime, timedelta

from app.esquemas.cuentas import EsquemaBase
from app.servicios.errores import ErrorValidacion


class SolicitudCambioPlan(EsquemaBase):
    """Plan elegido en el flujo de pago simulado (RF20 CA2)."""

    plan: str


def rango_de_fechas(desde, hasta):
    """Convierte ``desde`` y ``hasta`` (``AAAA-MM-DD``) en instantes; ``hasta`` incluye el día."""
    try:
        inicio = datetime.combine(date.fromisoformat(desde), datetime.min.time()) if desde else None
        fin = (
            datetime.combine(date.fromisoformat(hasta) + timedelta(days=1), datetime.min.time())
            if hasta else None
        )
    except ValueError as error:
        raise ErrorValidacion("Las fechas tienen que tener el formato AAAA-MM-DD.") from error
    if inicio and fin and inicio >= fin:
        raise ErrorValidacion("La fecha «desde» tiene que ser anterior a «hasta».")
    return inicio, fin


def usuario_de_listado_a_dict(usuario):
    """Fila del listado de cuentas (RF22): sin casos ni datos de análisis."""
    if not usuario.activo:
        estado = "Desactivada"
    elif usuario.correo_verificado_en is None:
        estado = "Sin verificar"
    else:
        estado = "Activa"
    return {
        "id": usuario.id, "nombre": f"{usuario.nombre} {usuario.apellido}",
        "correo": usuario.correo, "perfil": usuario.perfil, "rol": usuario.rol,
        "estado": estado, "creado_en": usuario.creado_en.isoformat(),
    }


def organizacion_de_listado_a_dict(organizacion, miembros, planes):
    """Fila del listado de organizaciones (RF22)."""
    return {
        "id": organizacion.id, "nombre": organizacion.nombre, "tipo": organizacion.tipo,
        "plan": planes[organizacion.plan]["nombre"], "estado": organizacion.estado,
        "miembros": miembros,
    }
