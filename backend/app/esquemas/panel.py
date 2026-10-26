"""Salida JSON del panel principal (funcionalidad 013).

Realiza: RF48 (CA1 a CA3).
"""
from app.esquemas.casos import NOMBRES_ESTADO, NOMBRES_PERMISO, NOMBRES_TIPO, transferencia_a_dict
from app.esquemas.organizaciones import invitacion_a_dict


def _fecha(valor):
    return valor.isoformat() if valor else None


def _caso_breve(caso):
    """Datos mínimos de un caso para enlazarlo desde el panel (RF48 CA3)."""
    return {
        "id": caso.id,
        "numero": caso.numero,
        "tipo_nombre": NOMBRES_TIPO[caso.tipo],
        "estado": caso.estado,
        "estado_nombre": NOMBRES_ESTADO[caso.estado],
        "actualizado_en": _fecha(caso.actualizado_en),
    }


def panel_a_dict(panel, momento):
    """Todas las secciones del panel, listas para la pantalla de inicio."""
    return {
        "por_estado": panel["por_estado"],
        "recientes": [_caso_breve(caso) for caso in panel["recientes"]],
        "analisis_en_curso": [
            {
                "id": analisis.id,
                "caso": _caso_breve(analisis.caso),
                "estado": analisis.estado,
                "cantidad_imagenes": len(analisis.imagenes),
                "creado_en": _fecha(analisis.creado_en),
            }
            for analisis in panel["analisis_en_curso"]
        ],
        "compartidos": [
            {
                "caso": _caso_breve(acceso.caso),
                "nivel_nombre": NOMBRES_PERMISO[acceso.nivel],
                "responsable": (
                    f"{acceso.caso.responsable.nombre} {acceso.caso.responsable.apellido}"
                ),
                "otorgado_en": _fecha(acceso.otorgado_en),
            }
            for acceso in panel["compartidos"]
        ],
        "invitaciones": [invitacion_a_dict(i, momento) for i in panel["invitaciones"]],
        "transferencias": [transferencia_a_dict(caso) for caso in panel["transferencias"]],
        "proximos_a_destruir": [
            {"caso": _caso_breve(caso), "vence_en": _fecha(vence)}
            for caso, vence in panel["proximos_a_destruir"]
        ],
        "actividad": [
            {**evento, "fecha": _fecha(evento["fecha"])} for evento in panel["actividad"]
        ],
    }
