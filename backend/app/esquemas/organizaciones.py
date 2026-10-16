"""Esquemas de entrada y salida de organizaciones, miembros e invitaciones.

Realiza: RNF04 (CA1) para la funcionalidad 004.
"""
from typing import Literal, Optional

from pydantic import EmailStr, Field, field_validator

from app.esquemas.cuentas import EsquemaBase
from app.modelos.organizacion import TIPO_ASEGURADORA, TIPO_ESTUDIO_JURIDICO

TipoOrganizacion = Literal["estudio_juridico", "aseguradora"]
NOMBRES_TIPO = {TIPO_ESTUDIO_JURIDICO: "Estudio Jurídico", TIPO_ASEGURADORA: "Aseguradora"}


def _vacio_a_nulo(valor):
    """Un texto vacío en un dato opcional significa "sin dato"."""
    if isinstance(valor, str) and not valor.strip():
        return None
    return valor


class SolicitudOrganizacion(EsquemaBase):
    """Datos para crear una organización (RF10)."""

    nombre: str = Field(min_length=1, max_length=150)
    tipo: TipoOrganizacion
    correo_contacto: Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, max_length=30)

    _vacios = field_validator("correo_contacto", "telefono", mode="before")(_vacio_a_nulo)


class SolicitudEdicionOrganizacion(EsquemaBase):
    """Datos editables de la organización (RF11). Todos son opcionales."""

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    tipo: Optional[TipoOrganizacion] = None
    correo_contacto: Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, max_length=30)

    _vacios = field_validator("correo_contacto", "telefono", mode="before")(_vacio_a_nulo)


class SolicitudEliminacion(EsquemaBase):
    """Confirmación de la eliminación: el nombre de la organización (RF18 CA1)."""

    confirmacion: str = Field(min_length=1, max_length=150)


class SolicitudInvitacion(EsquemaBase):
    """Correo y cargo opcional de la persona invitada (RF12)."""

    correo: EmailStr
    cargo: Optional[str] = Field(default=None, max_length=100)


class SolicitudCargo(EsquemaBase):
    """Cargo o área del miembro dentro de la organización (RF15 CA1)."""

    cargo: Optional[str] = Field(default=None, max_length=100)


class SolicitudReferente(EsquemaBase):
    """Miembro que pasa a ser Referente (RF15 CA2)."""

    id_usuario: int


class SolicitudAbandono(EsquemaBase):
    """Confirmación de que el único miembro acepta que la organización se elimine (RN08)."""

    confirmar_eliminacion: bool = False


def _fecha(valor):
    return valor.isoformat() if valor else None


def organizacion_a_dict(organizacion, membresia, servicio=None):
    """Organización con el rol del usuario que la consulta.

    Args:
        servicio: ``ServicioOrganizaciones``; si se indica, agrega el plan y su límite.
    """
    datos = {
        "id": organizacion.id,
        "nombre": organizacion.nombre,
        "tipo": organizacion.tipo,
        "tipo_nombre": NOMBRES_TIPO[organizacion.tipo],
        "correo_contacto": organizacion.correo_contacto,
        "telefono": organizacion.telefono,
        "mi_rol": membresia.rol,
        "creada_en": _fecha(organizacion.creada_en),
    }
    if servicio is not None:
        datos["plan"] = {
            "codigo": organizacion.plan,
            "nombre": servicio.nombre_del_plan(organizacion),
            "limite_miembros": servicio.limite_de_miembros(organizacion),
        }
    return datos


def miembro_a_dict(membresia):
    """Miembro tal como lo ven los demás miembros (RF16 CA1)."""
    usuario = membresia.usuario
    return {
        "id_usuario": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "correo": usuario.correo,
        "perfil": usuario.perfil,
        "cargo": membresia.cargo,
        "rol": membresia.rol,
        "incorporado_en": _fecha(membresia.incorporado_en),
    }


def invitacion_a_dict(invitacion, momento):
    """Invitación con su vigencia calculada en ``momento``."""
    invitante = invitacion.invitante
    return {
        "id": invitacion.id,
        "correo": invitacion.correo,
        "cargo": invitacion.cargo,
        "estado": invitacion.estado,
        "vigente": invitacion.vigente(momento),
        "vence_en": _fecha(invitacion.vence_en),
        "creada_en": _fecha(invitacion.creada_en),
        "organizacion": {
            "id": invitacion.organizacion.id,
            "nombre": invitacion.organizacion.nombre,
            "tipo_nombre": NOMBRES_TIPO[invitacion.organizacion.tipo],
        },
        "invitante": f"{invitante.nombre} {invitante.apellido}" if invitante else None,
    }
