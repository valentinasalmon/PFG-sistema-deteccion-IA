"""Esquemas de entrada y salida de casos y accesos.

Realiza: RNF04 (CA1) para la funcionalidad 005.
"""
from datetime import date
from typing import Literal, Optional

from pydantic import Field, field_validator

from app.esquemas.cuentas import EsquemaBase
from app.modelos.caso import (
    ESTADO_ANALIZADO,
    ESTADO_ARCHIVADO,
    ESTADO_BORRADOR,
    ESTADO_CERRADO,
    ESTADO_EN_ANALISIS,
    TIPO_AUTOMOVILISTICO,
    TIPO_LABORAL,
)
from app.servicios.servicio_casos import PERMISO_RESPONSABLE, vencimiento_de_retencion

TipoCaso = Literal["automovilistico", "laboral"]
EstadoCaso = Literal["borrador", "en_analisis", "analizado", "cerrado", "archivado"]
Nivel = Literal["lectura", "colaboracion"]

NOMBRES_TIPO = {TIPO_AUTOMOVILISTICO: "Automovilístico", TIPO_LABORAL: "Laboral"}
NOMBRES_ESTADO = {
    ESTADO_BORRADOR: "Borrador", ESTADO_EN_ANALISIS: "En análisis",
    ESTADO_ANALIZADO: "Analizado", ESTADO_CERRADO: "Cerrado", ESTADO_ARCHIVADO: "Archivado",
}
NOMBRES_PERMISO = {
    PERMISO_RESPONSABLE: "Responsable", "colaboracion": "Colaboración", "lectura": "Lectura",
}


def _vacio_a_nulo(valor):
    if isinstance(valor, str) and not valor.strip():
        return None
    return valor


def _espacio_valido(valor):
    if valor != "personal" and not str(valor).isdigit():
        raise ValueError("Elegí el espacio de trabajo: personal o una de tus organizaciones.")
    return str(valor)


class SolicitudCaso(EsquemaBase):
    """Datos para crear un caso (RF23)."""

    espacio: str = Field(min_length=1, max_length=20)
    tipo: TipoCaso
    fecha_hecho: date
    lugar: str = Field(min_length=1, max_length=200)
    expediente: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=2000)

    _espacio = field_validator("espacio", mode="before")(_espacio_valido)
    _vacios = field_validator("expediente", "descripcion", mode="before")(_vacio_a_nulo)


class SolicitudEdicionCaso(EsquemaBase):
    """Datos editables del caso (RF25). Todos son opcionales; el número no se edita."""

    tipo: Optional[TipoCaso] = None
    fecha_hecho: Optional[date] = None
    lugar: Optional[str] = Field(default=None, min_length=1, max_length=200)
    expediente: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=2000)

    _vacios = field_validator("expediente", "descripcion", mode="before")(_vacio_a_nulo)


class SolicitudEstado(EsquemaBase):
    """Operación sobre el estado del caso (RF27 a RF29)."""

    operacion: Literal["cerrar", "archivar", "desarchivar", "reabrir"]


class SolicitudCompartir(EsquemaBase):
    """Destinatario y permiso; sin ``id_usuario`` se comparte con toda la organización (RF30)."""

    nivel: Nivel
    id_usuario: Optional[int] = None


class SolicitudNivel(EsquemaBase):
    """Nivel nuevo de un acceso (RF31)."""

    nivel: Nivel


class SolicitudTransferencia(EsquemaBase):
    """Destinatario de la transferencia: id de un miembro o correo de un usuario (RF33)."""

    destino: str = Field(min_length=1, max_length=254)
    conservar_colaboracion: bool = True


class FiltrosCasos(EsquemaBase):
    """Búsqueda y filtros del listado (RF26)."""

    numero: Optional[str] = Field(default=None, max_length=20)
    expediente: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[EstadoCaso] = None
    tipo: Optional[TipoCaso] = None
    espacio: Optional[str] = Field(default=None, max_length=20)
    desde: Optional[date] = None
    hasta: Optional[date] = None
    pagina: int = Field(default=1, ge=1)

    _vacios = field_validator(
        "numero", "expediente", "estado", "tipo", "espacio", "desde", "hasta", mode="before"
    )(_vacio_a_nulo)

    @field_validator("espacio")
    @classmethod
    def _espacio(cls, valor):
        return None if valor is None else _espacio_valido(valor)


def _fecha(valor):
    return valor.isoformat() if valor else None


def _persona(usuario):
    if usuario is None:
        return None
    return {
        "id": usuario.id, "nombre": f"{usuario.nombre} {usuario.apellido}",
        "correo": usuario.correo,
    }


def acciones_permitidas(caso, permiso):
    """Qué puede hacer el usuario en el estado actual (RF24 CA1, RN19, RN20)."""
    es_responsable = permiso == PERMISO_RESPONSABLE
    editable = caso.estado in (ESTADO_BORRADOR, ESTADO_ANALIZADO)
    return {
        "editar": permiso in (PERMISO_RESPONSABLE, "colaboracion") and editable,
        "cerrar": es_responsable and editable,
        "archivar": es_responsable and caso.estado == ESTADO_CERRADO,
        "desarchivar": es_responsable and caso.estado == ESTADO_ARCHIVADO,
        "reabrir": es_responsable and caso.estado in (ESTADO_CERRADO, ESTADO_ARCHIVADO),
        "compartir": es_responsable and not caso.es_personal,
        "transferir": es_responsable and caso.estado != ESTADO_EN_ANALISIS,
        "eliminar": es_responsable and caso.estado != ESTADO_EN_ANALISIS,
    }


def caso_a_dict(caso, permiso):
    """Caso con el permiso del usuario y las acciones que habilita."""
    vence = vencimiento_de_retencion(caso)
    datos = {
        "id": caso.id,
        "numero": caso.numero,
        "tipo": caso.tipo,
        "tipo_nombre": NOMBRES_TIPO[caso.tipo],
        "fecha_hecho": caso.fecha_hecho.isoformat(),
        "lugar": caso.lugar,
        "expediente": caso.expediente,
        "descripcion": caso.descripcion,
        "estado": caso.estado,
        "estado_nombre": NOMBRES_ESTADO[caso.estado],
        "espacio": (
            {"tipo": "personal", "id": None, "nombre": "Personal"} if caso.es_personal
            else {"tipo": "organizacion", "id": caso.id_organizacion,
                  "nombre": caso.organizacion.nombre}
        ),
        "responsable": _persona(caso.responsable),
        "mi_permiso": permiso,
        "mi_permiso_nombre": NOMBRES_PERMISO[permiso],
        "creado_en": _fecha(caso.creado_en),
        "actualizado_en": _fecha(caso.actualizado_en),
        "retencion_desde": _fecha(caso.retencion_desde),
        "retencion_vence": _fecha(vence),
        "acciones": acciones_permitidas(caso, permiso),
    }
    if permiso == PERMISO_RESPONSABLE:
        datos["transferencia_pendiente"] = _persona(caso.destinatario_transferencia)
    return datos


def acceso_a_dict(acceso):
    """Acceso compartido de un caso."""
    return {
        "id": acceso.id,
        "toda_organizacion": acceso.toda_organizacion,
        "usuario": _persona(acceso.usuario),
        "nivel": acceso.nivel,
        "nivel_nombre": NOMBRES_PERMISO[acceso.nivel],
        "otorgado_en": _fecha(acceso.otorgado_en),
    }


def transferencia_a_dict(caso):
    """Transferencia de un caso personal que espera la respuesta del usuario."""
    return {
        "id": caso.id,
        "numero": caso.numero,
        "tipo_nombre": NOMBRES_TIPO[caso.tipo],
        "solicitante": _persona(caso.responsable),
        "solicitada_en": _fecha(caso.transferencia_en),
    }
