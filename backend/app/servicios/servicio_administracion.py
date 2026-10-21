"""Tablero y listados del Administrador de la plataforma (funcionalidad 014).

Todo es de solo lectura y agregado: ningún indicador permite identificar ni
abrir un caso, una imagen o un informe (RF21 CA2, RF22 CA2).

Realiza: RF21 (CA1 a CA3), RF22 (CA1, CA2); RN35.
"""
from app.modelos.caso import Caso
from app.modelos.organizacion import Organizacion
from app.modelos.usuario import ROL_ADMINISTRADOR
from app.servicios.errores import AccesoDenegado

POR_PAGINA = 20


class ServicioAdministracion:
    """Indicadores y listados globales, solo para el Administrador."""

    def __init__(self, estadisticas, configuracion):
        """
        Args:
            estadisticas: ``RepositorioEstadisticas``.
        """
        self.estadisticas = estadisticas
        self.configuracion = configuracion

    @staticmethod
    def _exigir_administrador(usuario):
        if usuario.rol != ROL_ADMINISTRADOR:
            raise AccesoDenegado(
                "Solo el Administrador de la plataforma puede ver esta información."
            )

    def tablero(self, usuario, desde=None, hasta=None):
        """Indicadores agregados; las series por mes respetan el rango (RF21 CA1)."""
        self._exigir_administrador(usuario)
        e = self.estadisticas
        return {
            "usuarios_por_perfil": e.usuarios_por_perfil(),
            "organizaciones_por_tipo": e.organizaciones_por(Organizacion.tipo),
            "organizaciones_por_plan": e.organizaciones_por(Organizacion.plan),
            "casos_por_estado": e.casos_por(Caso.estado),
            "casos_por_tipo": e.casos_por(Caso.tipo),
            "analisis_por_mes": e.analisis_por_mes(desde, hasta),
            "altas_por_mes": e.altas_por_mes(desde, hasta),
        }

    def usuarios(self, usuario, busqueda=None, perfil=None, pagina=1):
        """Listado de cuentas, de solo lectura (RF22)."""
        self._exigir_administrador(usuario)
        filas, total = self.estadisticas.usuarios(busqueda, perfil, pagina, POR_PAGINA)
        return filas, total, POR_PAGINA

    def organizaciones(self, usuario, busqueda=None, tipo=None, pagina=1):
        """Listado de organizaciones con su cantidad de miembros (RF22)."""
        self._exigir_administrador(usuario)
        filas, total = self.estadisticas.organizaciones(busqueda, tipo, pagina, POR_PAGINA)
        return filas, total, POR_PAGINA
