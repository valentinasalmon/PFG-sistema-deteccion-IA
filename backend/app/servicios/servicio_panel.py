"""Panel principal: resumen de los casos del usuario y su actividad reciente.

Reúne en una sola consulta lo que la persona necesita ver al entrar: casos
por estado, últimos actualizados, análisis en curso, casos compartidos
recientemente, invitaciones y transferencias pendientes, casos próximos a
destruirse y la actividad reciente, que se arma con la auditoría. Solo incluye
casos a los que el usuario tiene acceso (RNF05).

Realiza: RF48 (CA1 a CA3), CU30; RN31 (casos próximos a destruirse).
"""
from datetime import timedelta

from app.servicios import auditoria
from app.servicios.servicio_casos import vencimiento_de_retencion
from app.utilidades.tiempo import ahora_utc

CANTIDAD_RECIENTES = 5
CANTIDAD_ACTIVIDAD = 10
DIAS_COMPARTIDOS_RECIENTES = 30
DIAS_AVISO_DESTRUCCION = 30  # RN31

# Acciones exitosas sobre casos que se muestran en la actividad, con su texto.
# Las descargas no se muestran porque no cambian el caso.
TEXTOS_DE_ACTIVIDAD = {
    auditoria.CASO_CREACION: "creó el caso {numero}",
    auditoria.CASO_EDICION: "editó los datos del caso {numero}",
    auditoria.CASO_CAMBIO_ESTADO: "cambió el estado del caso {numero}",
    auditoria.CASO_COMPARTIR: "compartió el caso {numero}",
    auditoria.CASO_ACCESO_MODIFICACION: "modificó un acceso al caso {numero}",
    auditoria.CASO_ACCESO_REVOCACION: "quitó un acceso al caso {numero}",
    auditoria.CASO_TRANSFERENCIA: "transfirió el caso {numero}",
    auditoria.IMAGEN_CARGA: "cargó la imagen «{nombre}» en {numero}",
    auditoria.IMAGEN_ELIMINACION: "eliminó la imagen «{nombre}» de {numero}",
    auditoria.ANALISIS_SOLICITUD: "pidió el análisis de {imagenes} imagen(es) de {numero}",
    # Eventos del sistema: se redactan sin sujeto.
    auditoria.ANALISIS_FINALIZACION: "Terminó el análisis de {numero}",
    auditoria.ANALISIS_FALLA: "No se pudo completar el análisis de {numero}",
    auditoria.INFORME_GENERACION: "Se generó el informe PDF de {numero}",
}
ACCIONES_DEL_SISTEMA = (
    auditoria.ANALISIS_FINALIZACION, auditoria.ANALISIS_FALLA, auditoria.INFORME_GENERACION,
)
TEXTOS_ESTADO = {
    "cerrar": "cerró el caso {numero}", "archivar": "archivó el caso {numero}",
    "desarchivar": "desarchivó el caso {numero}", "reabrir": "reabrió el caso {numero}",
}
TEXTOS_TRANSFERENCIA = {
    "solicitud": "pidió transferir el caso {numero}",
    "cancelada": "canceló la transferencia del caso {numero}",
    "aceptada": "aceptó la transferencia del caso {numero}",
    "rechazada": "rechazó la transferencia del caso {numero}",
}


def _plantilla(entrada):
    """Texto que corresponde a la acción, con las variantes según el detalle."""
    detalle = entrada.detalle or {}
    if entrada.accion == auditoria.CASO_CAMBIO_ESTADO:
        return TEXTOS_ESTADO.get(detalle.get("operacion"), TEXTOS_DE_ACTIVIDAD[entrada.accion])
    if entrada.accion == auditoria.CASO_TRANSFERENCIA:
        variante = detalle.get("respuesta") or next(
            (clave for clave in ("solicitud", "cancelada") if detalle.get(clave)), None
        )
        return TEXTOS_TRANSFERENCIA.get(variante, TEXTOS_DE_ACTIVIDAD[entrada.accion])
    return TEXTOS_DE_ACTIVIDAD[entrada.accion]


def redactar_actividad(entrada, usuario):
    """Texto de un evento de la actividad reciente, en lenguaje común (RF48 CA2)."""
    detalle = entrada.detalle or {}
    texto = _plantilla(entrada).format(
        numero=detalle.get("numero", ""), nombre=detalle.get("nombre", "sin nombre"),
        imagenes=detalle.get("imagenes", ""),
    )
    if entrada.accion in ACCIONES_DEL_SISTEMA:
        return texto
    quien = f"{usuario.nombre} {usuario.apellido}" if usuario else "Una cuenta eliminada"
    return f"{quien} {texto}"


class ServicioPanel:
    """Arma el panel principal de un usuario."""

    def __init__(self, repositorios):
        """
        Args:
            repositorios: diccionario con ``casos``, ``analisis``, ``auditoria`` y
                ``organizaciones``.
        """
        self.repositorios = repositorios

    def panel(self, usuario):
        """Todas las secciones del panel (RF48 CA1)."""
        casos = self.repositorios["casos"]
        ids_accesibles = casos.ids_accesibles(usuario.id)
        ahora = ahora_utc()
        return {
            "por_estado": casos.cantidad_por_estado(usuario.id),
            "recientes": casos.recientes(usuario.id, CANTIDAD_RECIENTES),
            "analisis_en_curso": self.repositorios["analisis"].en_curso_de_casos(ids_accesibles),
            "compartidos": casos.compartidos_desde(
                usuario.id, ahora - timedelta(days=DIAS_COMPARTIDOS_RECIENTES), CANTIDAD_RECIENTES
            ),
            "invitaciones": self.repositorios["organizaciones"].invitaciones_pendientes_de_correo(
                usuario.correo, ahora
            ),
            "transferencias": casos.transferencias_para(usuario.id),
            "proximos_a_destruir": self._proximos_a_destruir(usuario, ahora),
            "actividad": self._actividad(ids_accesibles),
        }

    def _proximos_a_destruir(self, usuario, ahora):
        """Casos del Responsable que vencen dentro de 30 días, del más próximo al más lejano."""
        limite = ahora + timedelta(days=DIAS_AVISO_DESTRUCCION)
        proximos = []
        for caso in self.repositorios["casos"].con_retencion_a_cargo(usuario.id):
            vence = vencimiento_de_retencion(caso)
            if vence is not None and vence <= limite:
                proximos.append((caso, vence))
        return sorted(proximos, key=lambda par: par[1])

    def _actividad(self, ids_accesibles):
        """Últimos eventos de los casos accesibles, ya redactados (RF48 CA2)."""
        entradas = self.repositorios["auditoria"].recientes_de_recursos(
            auditoria.TIPO_CASO, ids_accesibles, list(TEXTOS_DE_ACTIVIDAD), auditoria.EXITOSO,
            CANTIDAD_ACTIVIDAD,
        )
        return [
            {
                "fecha": entrada.fecha,
                "id_caso": int(entrada.id_recurso),
                "numero": (entrada.detalle or {}).get("numero"),
                "texto": redactar_actividad(entrada, usuario),
            }
            for entrada, usuario in entradas
        ]
