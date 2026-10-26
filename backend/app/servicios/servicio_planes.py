"""Planes, consumo y cambio de plan con pago simulado (funcionalidad 014).

Los límites de cada plan son datos de configuración (RF19 CA3). El cambio de
plan recorre un pago **simulado**: no pide ni guarda datos de pago, aplica el
plan de inmediato y queda en la auditoría como pago simulado (RF20 CA2, CP-01).

Realiza: RF19 (CA2, CA3), RF20 (CA1, CA2).
"""
from datetime import datetime

from app.servicios import auditoria
from app.servicios.errores import AccesoDenegado, ConflictoDatos, ErrorValidacion
from app.utilidades.tiempo import ahora_utc


def inicio_del_mes(momento):
    """Primer instante del mes de ``momento``."""
    return datetime(momento.year, momento.month, 1)


def inicio_del_mes_siguiente(momento):
    """Primer instante del mes siguiente: la fecha de renovación de los límites."""
    if momento.month == 12:
        return datetime(momento.year + 1, 1, 1)
    return datetime(momento.year, momento.month + 1, 1)


class ServicioPlanes:
    """Consulta y cambio de planes, y control del límite mensual de análisis."""

    def __init__(self, organizaciones, estadisticas, configuracion, registro):
        """
        Args:
            organizaciones: ``ServicioOrganizaciones``, que resuelve la membresía.
            estadisticas: ``RepositorioEstadisticas``, que cuenta los análisis.
            registro: ``ServicioAuditoria``.
        """
        self.organizaciones = organizaciones
        self.estadisticas = estadisticas
        self.configuracion = configuracion
        self.registro = registro

    def limites_del_caso(self, caso):
        """Límites del plan del espacio de trabajo del caso."""
        if caso.id_organizacion is None:
            return self.configuracion["PLAN_PERSONAL"]
        return self.configuracion["PLANES"][caso.organizacion.plan]

    def analisis_del_mes(self, id_organizacion, id_responsable, momento=None):
        """Análisis pedidos en el mes en curso por un espacio de trabajo."""
        desde = inicio_del_mes(momento or ahora_utc())
        return self.estadisticas.analisis_del_espacio_desde(id_organizacion, id_responsable, desde)

    def verificar_analisis_disponible(self, caso):
        """Rechaza el pedido si el espacio alcanzó su límite mensual (RF19 CA2).

        Raises:
            ConflictoDatos: con el límite y la fecha de renovación.
        """
        limite = self.limites_del_caso(caso)["analisis_mes"]
        ahora = ahora_utc()
        usados = self.analisis_del_mes(caso.id_organizacion, caso.id_responsable, ahora)
        if usados >= limite:
            renovacion = inicio_del_mes_siguiente(ahora).strftime("%d/%m/%Y")
            raise ConflictoDatos(
                f"Este espacio usó los {limite} análisis de su plan para este mes. "
                f"El límite se renueva el {renovacion}.",
                codigo="limite_de_analisis",
            )

    def plan_personal(self, usuario):
        """Plan y consumo del espacio personal de un abogado (RF20)."""
        plan = self.configuracion["PLAN_PERSONAL"]
        return {
            "codigo": "personal", "nombre": plan["nombre"], "limites": plan,
            "consumo": {"analisis_mes": self.analisis_del_mes(None, usuario.id)},
            "renovacion": inicio_del_mes_siguiente(ahora_utc()).date().isoformat(),
        }

    def plan_de_organizacion(self, id_organizacion, usuario):
        """Plan, límites, consumo y planes disponibles de una organización (RF20 CA1)."""
        organizacion, membresia = self.organizaciones.obtener(id_organizacion, usuario)
        planes = self.configuracion["PLANES"]
        return {
            "codigo": organizacion.plan,
            "nombre": planes[organizacion.plan]["nombre"],
            "limites": planes[organizacion.plan],
            "consumo": {
                "miembros": len(organizacion.membresias),
                "analisis_mes": self.analisis_del_mes(organizacion.id, None),
            },
            "renovacion": inicio_del_mes_siguiente(ahora_utc()).date().isoformat(),
            "puede_cambiar": membresia.es_referente,
            "disponibles": [{"codigo": codigo, **datos} for codigo, datos in planes.items()],
        }

    def cambiar_plan(self, id_organizacion, usuario, codigo):
        """Aplica otro plan después de un pago simulado (RF20 CA2). Solo el Referente.

        Raises:
            AccesoDenegado: si no es Referente.
            ErrorValidacion: si el plan no existe o los miembros superan su límite.
        """
        organizacion, membresia = self.organizaciones.obtener(id_organizacion, usuario)
        if not membresia.es_referente:
            raise AccesoDenegado("Solo el Referente puede cambiar el plan.")
        planes = self.configuracion["PLANES"]
        if codigo not in planes:
            raise ErrorValidacion("Elegí un plan válido.", {"plan": "Elegí un plan válido."})
        if len(organizacion.membresias) > planes[codigo]["miembros"]:
            mensaje = (
                f"El plan {planes[codigo]['nombre']} admite hasta {planes[codigo]['miembros']} "
                "miembros. Desvinculá a algunos antes de cambiarlo."
            )
            raise ErrorValidacion(mensaje, {"plan": mensaje})
        anterior = organizacion.plan
        organizacion.plan = codigo
        self.registro.registrar(
            auditoria.ORGANIZACION_CAMBIO_PLAN, auditoria.EXITOSO, usuario=usuario,
            recurso=(auditoria.TIPO_ORGANIZACION, organizacion.id),
            detalle={"anterior": anterior, "nuevo": codigo, "pago": "simulado"},
            confirmar=True,
        )
        return organizacion
