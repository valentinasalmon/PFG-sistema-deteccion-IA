"""Entrada y salida JSON de los análisis.

Realiza: RF38, RF43, RF45, RF46; RNF04 (CA1).
"""
from typing import List

from pydantic import Field

from app.esquemas.cuentas import EsquemaBase

NOMBRES_ESTADO = {
    "en_cola": "En cola",
    "en_proceso": "En proceso",
    "finalizado": "Finalizado",
    "fallido": "Fallido",
}


class SolicitudAnalisis(EsquemaBase):
    """Imágenes elegidas para analizar (RF38)."""

    imagenes: List[int] = Field(default_factory=list, max_length=200)


def _fecha(valor):
    return valor.isoformat() if valor else None


def _solicitante(analisis):
    usuario = analisis.solicitante
    return f"{usuario.nombre} {usuario.apellido}" if usuario else "Cuenta eliminada"


def analisis_resumen_a_dict(analisis):
    """Análisis para el historial y para seguir su progreso (RF46)."""
    return {
        "id": analisis.id,
        "estado": analisis.estado,
        "estado_nombre": NOMBRES_ESTADO[analisis.estado],
        "en_curso": analisis.en_curso,
        "solicitante": _solicitante(analisis),
        "creado_en": _fecha(analisis.creado_en),
        "finalizado_en": _fecha(analisis.finalizado_en),
        "cantidad_imagenes": len(analisis.imagenes),
        "progreso": {
            "imagen_actual": analisis.imagen_actual,
            "capa_actual": analisis.capa_actual,
        },
        "motivo_falla": analisis.motivo_falla,
    }


def _resultado_a_dict(resultado, enlaces):
    return {
        "capa": resultado.capa,
        "estado": resultado.estado,
        "nivel": resultado.nivel,
        "conclusion": resultado.conclusion,
        "motivo": resultado.motivo,
        "version": resultado.version,
        "detalle": resultado.detalle,
        # Enlace firmado de la imagen del resultado (mapa ELA), si tiene (011).
        "imagen": enlaces.get(resultado.id),
        "anomalias": [
            {
                "campo": a.campo, "valor": a.valor, "descripcion": a.descripcion,
                "severidad": a.severidad,
            }
            for a in resultado.anomalias
        ],
    }


def informe_a_dict(informe):
    """Informe PDF para el historial (RF45 CA1)."""
    analisis = informe.analisis
    return {
        "id": informe.id,
        "id_analisis": informe.id_analisis,
        "generado_en": _fecha(informe.generado_en),
        "solicitante": _solicitante(analisis),
        "imagenes": [incluida.nombre for incluida in analisis.imagenes],
        "huella": informe.huella,
        "tamanio": informe.tamanio,
        # Verificación pública y sello del PDF en Hedera (funcionalidad 026).
        "codigo_verificacion": informe.codigo_verificacion,
        "sello": {
            "estado": informe.sello_estado,
            "referencia": informe.sello_referencia,
            "simulado": informe.sello_simulado,
        },
    }


def analisis_a_dict(analisis, enlaces=None):
    """Análisis completo, con los resultados de cada capa por imagen (RF43) y su informe.

    Args:
        enlaces: diccionario ``id de resultado -> enlace firmado`` de sus imágenes.
    """
    enlaces = enlaces or {}
    datos = analisis_resumen_a_dict(analisis)
    datos["versiones"] = analisis.versiones
    datos["informe"] = informe_a_dict(analisis.informe) if analisis.informe else None
    datos["imagenes"] = [
        {
            "id_imagen": incluida.id_imagen,
            "nombre": incluida.nombre,
            "huella": incluida.huella,
            "integridad": incluida.integridad,
            "resultados": [_resultado_a_dict(r, enlaces) for r in incluida.resultados],
        }
        for incluida in analisis.imagenes
    ]
    return datos
