"""Servicio que informa el estado de la API y de sus dependencias.

Es el primer ejemplo del recorrido completo de capas:
ruta -> servicio -> repositorio / integración.

Realiza: CA2 y CA3 de la funcionalidad 001; RNF15.
"""
from dataclasses import dataclass, field
from datetime import timedelta

from app.integraciones.cliente_redis import ClienteRedis
from app.repositorios.repositorio_salud import RepositorioSalud
from app.utilidades.tiempo import ahora_utc

ESTADO_OK = "ok"
ESTADO_ERROR = "error"

# Un sello que no se confirma en este tiempo se informa como demorado: el
# trabajo periódico lo reintenta cada pocos minutos (funcionalidad 023).
DEMORA_DEL_SELLO = timedelta(minutes=30)


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


def resumen_del_sello(modo, red, repositorio=None, ahora=None):
    """Resume si el sello en Hedera está funcionando, para la página pública de estado.

    No afecta a ``saludable``: si Hedera no responde, la plataforma sigue
    analizando y reintenta el sello después (RF37 CA3). Nunca expone la
    cuenta, el tema ni las huellas: solo el modo, la red y si hay fallas.

    Args:
        modo: valor de ``SELLO_TIEMPO`` (hedera, simulado o desactivado).
        red: red de Hedera configurada (testnet o mainnet).
        repositorio: repositorio con ``resumen_sellos``; por defecto, el real.
        ahora: fecha de referencia (para las pruebas).

    Returns:
        Diccionario con ``modo``, ``red`` (solo con Hedera), ``estado``
        (ok, con_demoras, con_fallas o desactivado) y ``ultimo`` (ISO o None).

    Realiza: RF37, RNF15; tarea pendiente de comprobación de la 023.
    """
    if modo not in ("hedera", "simulado"):
        return {"modo": "desactivado", "estado": "desactivado", "ultimo": None}
    repositorio = repositorio or RepositorioSalud()
    try:
        datos = repositorio.resumen_sellos((ahora or ahora_utc()) - DEMORA_DEL_SELLO)
    except Exception:  # pylint: disable=broad-exception-caught
        # El resumen nunca debe tirar abajo la ruta de salud.
        return {"modo": modo, "estado": ESTADO_ERROR, "ultimo": None}
    if datos["fallidos"]:
        estado = "con_fallas"
    elif datos["demorados"]:
        estado = "con_demoras"
    else:
        estado = ESTADO_OK
    resumen = {
        "modo": modo,
        "estado": estado,
        "ultimo": datos["ultimo"].isoformat() if datos["ultimo"] else None,
    }
    if modo == "hedera":
        resumen["red"] = red
    return resumen
