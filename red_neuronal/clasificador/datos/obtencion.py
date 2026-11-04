"""Etapa ``obtener``: descarga la muestra pedida de cada fuente.

Toma de cada fuente la cantidad configurada de imágenes reales y sintéticas,
las guarda sin modificar (con su formato original) y escribe el manifiesto
crudo. La normalización se hace después, en la etapa ``preparar``, para
poder auditar qué se descargó exactamente.

Realiza: CA2 y CA3 de la funcionalidad 010.
"""

from collections import Counter
from pathlib import Path

from clasificador.configuracion import ConfiguracionDatos
from clasificador.datos.fuentes import FuenteDatos, crear_fuente
from clasificador.datos.manifiesto import (
    CLASE_REAL,
    CLASE_SINTETICA,
    RegistroImagen,
    huella_archivo,
)


class ErrorObtencion(Exception):
    """Una fuente no tiene suficientes imágenes para lo que se pidió."""


def obtener_de_fuente(  # pylint: disable=too-many-locals
    fuente: FuenteDatos,
    raiz_destino: Path,
    cantidades: dict[int, int] | None = None,
    cuota_por_generador: int | None = None,
) -> list[RegistroImagen]:
    """Guarda imágenes de una fuente hasta completar la cantidad por clase.

    Con ``cantidades=None`` se toman todas las imágenes de la fuente (se usa
    para el conjunto propio, que se evalúa completo). Las imágenes repetidas
    dentro de la fuente (misma huella) se saltean, para que el conjunto no
    tenga duplicados desde el origen. Con ``cuota_por_generador`` ningún
    generador aporta más de esa cantidad de sintéticas: así las métricas por
    generador tienen sentido y ninguno domina el entrenamiento (lección de la
    prueba de concepto, receta v1).
    """
    todas = cantidades is None
    pendientes = Counter(cantidades or {})
    por_generador: Counter = Counter()
    vistas: set[str] = set()
    registros = []
    for ejemplo in fuente.iterar():
        if not todas and sum(pendientes.values()) == 0:
            break
        if not todas and pendientes[ejemplo.clase] <= 0:
            continue
        if (
            cuota_por_generador is not None
            and ejemplo.clase == CLASE_SINTETICA
            and por_generador[ejemplo.generador] >= cuota_por_generador
        ):
            continue
        # Las carpetas locales conservan su ruta: el nombre del archivo indica
        # la escena del conjunto propio y permite ubicar cada foto en la planilla.
        ruta_relativa = Path("crudo") / fuente.nombre / (
            ejemplo.nombre or f"{len(registros):07d}{ejemplo.extension}"
        )
        destino = Path(raiz_destino) / ruta_relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(ejemplo.contenido)
        huella = huella_archivo(destino)
        if huella in vistas:
            destino.unlink()
            continue
        vistas.add(huella)
        pendientes[ejemplo.clase] -= 1
        if ejemplo.clase == CLASE_SINTETICA:
            por_generador[ejemplo.generador] += 1
        registros.append(
            RegistroImagen(
                huella_sha256=huella,
                ruta_relativa=ruta_relativa.as_posix(),
                clase=ejemplo.clase,
                fuente=fuente.nombre,
                generador=ejemplo.generador,
                variante=ejemplo.variante,
            )
        )
    faltantes = {clase: cantidad for clase, cantidad in pendientes.items() if cantidad > 0}
    if faltantes:
        nombres = {CLASE_REAL: "reales", CLASE_SINTETICA: "sintéticas"}
        detalle = ", ".join(f"{cantidad} {nombres[clase]}" for clase, cantidad in faltantes.items())
        raise ErrorObtencion(f"la fuente '{fuente.nombre}' se agotó y faltan {detalle}")
    return registros


def obtener(
    configuracion: ConfiguracionDatos, raiz_destino: Path, semilla: int
) -> list[RegistroImagen]:
    """Etapa ``obtener``: recorre todas las fuentes configuradas."""
    registros = []
    for config_fuente in configuracion.fuentes:
        fuente = crear_fuente(config_fuente, semilla)
        cantidades = {
            CLASE_REAL: config_fuente.cantidad_reales,
            CLASE_SINTETICA: config_fuente.cantidad_sinteticas,
        }
        registros += obtener_de_fuente(
            fuente, raiz_destino, cantidades, config_fuente.cuota_por_generador
        )
    return registros
