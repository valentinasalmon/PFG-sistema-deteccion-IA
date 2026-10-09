"""Servicio que informa el estado de la API y de sus dependencias.

Es el primer ejemplo del recorrido completo de capas:
ruta -> servicio -> repositorio / integración.

Realiza: CA2 y CA3 de la funcionalidad 001; RNF15.
"""
from dataclasses import dataclass, field

from app.integraciones.cliente_redis import ClienteRedis
from app.repositorios.repositorio_salud import RepositorioSalud

ESTADO_OK = "ok"
ESTADO_ERROR = "error"


@dataclass
class EstadoSalud:
    """Resultado de una verificación de salud."""

    componentes: dict = field(default_factory=dict)

    @property
    def saludable(self):
        """True si todos los componentes respondieron correctamente."""
        return all(estado == ESTADO_OK for estado in self.componentes.values())


class ServicioSalud:
    """Ejecuta un conjunto de verificaciones independientes.

    Recibe las verificaciones como funciones (inyección de dependencias),
    lo que permite probar el servicio sin una base de datos ni un Redis reales.
    """

    def __init__(self, verificaciones):
        """Args:
            verificaciones: diccionario nombre -> función sin argumentos que
                devuelve True si el componente está disponible.
        """
        self.verificaciones = verificaciones

    def obtener_estado(self):
        """Ejecuta todas las verificaciones; una falla no impide las demás.

        Returns:
            EstadoSalud con "ok" o "error" por componente.
        """
        componentes = {"api": ESTADO_OK}
        for nombre, verificar in self.verificaciones.items():
            try:
                componentes[nombre] = ESTADO_OK if verificar() else ESTADO_ERROR
            except Exception:  # pylint: disable=broad-exception-caught
                # Una verificación nunca debe interrumpir el informe de salud.
                componentes[nombre] = ESTADO_ERROR
        return EstadoSalud(componentes=componentes)


def crear_servicio_salud(url_redis):
    """Arma el servicio con sus dependencias reales.

    La construcción vive en la capa de servicios para que las rutas no
    importen repositorios ni integraciones (RNF17).
    """
    return ServicioSalud(
        {
            "base_de_datos": RepositorioSalud().verificar_conexion,
            "redis": ClienteRedis(url_redis).verificar_conexion,
        }
    )
