"""Ficha del modelo (*model card*).

Cada versión publicada tiene una ficha que permite entender y reproducir el
modelo: datos y licencias, partición, hiperparámetros, entorno, métricas,
exportación y limitaciones. Se genera automáticamente a partir de las
salidas del pipeline para que no dependa de completarla a mano.

Realiza: RN27, RN29, RNF24 CA2; CA11 y CA17 de la funcionalidad 010.
"""

from dataclasses import dataclass, fields
from importlib import resources

from jinja2 import Environment, StrictUndefined

from clasificador.configuracion import Configuracion

LEYENDA = (
    "Este modelo estima una probabilidad. Su resultado es un indicio y no constituye "
    "un dictamen pericial. Consulte a un profesional especializado."
)

SECCIONES_OBLIGATORIAS = (
    "## 1. Identificación",
    "## 2. Uso previsto y limitaciones",
    "## 3. Datos",
    "## 4. Entrenamiento",
    "## 5. Entorno",
    "## 6. Métricas",
    "## 7. Exportación",
    "## 8. Reproducción",
)

_COLUMNAS_TABLA = ("cantidad", "auc", "exactitud", "precision", "exhaustividad", "f1", "ece")


class ErrorFicha(Exception):
    """Faltan datos obligatorios para generar la ficha."""


@dataclass(frozen=True)
class DatosFicha:  # pylint: disable=too-many-instance-attributes
    """Todo lo que la ficha necesita, reunido por la etapa ``publicar``.

    Es un registro de datos: tiene tantos campos como secciones la ficha.
    """

    version: str
    fecha: str
    configuracion: Configuracion
    huella_manifiesto: str
    huella_modelo: str
    resumen_datos: dict
    entrenamiento: dict
    temperatura: float
    entorno: dict
    metricas_prueba: dict
    exportacion: dict
    commit: str
    id_ejecucion: str
    metricas_no_visto: dict | None = None
    metricas_condiciones_reales: dict | None = None


def _formatear(valor) -> str:
    """Texto legible en español para un valor de la ficha."""
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if valor is None:
        return "no calculable"
    if isinstance(valor, float):
        return f"{valor:.4f}"
    return str(valor)


def _tabla(metricas: dict) -> str:
    """Tabla Markdown de una sola fila de métricas."""
    encabezado = "| " + " | ".join(_COLUMNAS_TABLA) + " |"
    separador = "|" + "---|" * len(_COLUMNAS_TABLA)
    fila = "| " + " | ".join(_formatear(metricas.get(c)) for c in _COLUMNAS_TABLA) + " |"
    return "\n".join([encabezado, separador, fila])


def _tabla_grupos(grupos: dict[str, dict]) -> str:
    """Tabla Markdown con una fila por grupo."""
    if not grupos:
        return "_Sin datos._"
    encabezado = "| grupo | " + " | ".join(_COLUMNAS_TABLA) + " |"
    separador = "|---|" + "---|" * len(_COLUMNAS_TABLA)
    filas = [
        f"| {grupo} | " + " | ".join(_formatear(m.get(c)) for c in _COLUMNAS_TABLA) + " |"
        for grupo, m in grupos.items()
    ]
    return "\n".join([encabezado, separador, *filas])


def generar_ficha(datos: DatosFicha) -> str:
    """Genera el texto Markdown de la ficha del modelo."""
    if not datos.metricas_prueba or "total" not in datos.metricas_prueba:
        raise ErrorFicha("faltan las métricas del conjunto de prueba")
    if datos.metricas_prueba["total"].get("auc") is None:
        raise ErrorFicha("el AUC de prueba no es calculable: la prueba debe tener ambas clases")
    entorno_jinja = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    entorno_jinja.globals.update(tabla=_tabla, tabla_grupos=_tabla_grupos)
    entorno_jinja.filters["legible"] = _formatear
    plantilla = entorno_jinja.from_string(
        resources.files("clasificador.plantillas")
        .joinpath("ficha_modelo.md.j2")
        .read_text(encoding="utf-8")
    )
    return plantilla.render(
        **{campo.name: getattr(datos, campo.name) for campo in fields(DatosFicha)},
        leyenda=LEYENDA,
        tamanio_recorte=datos.configuracion.entrenamiento.tamanio_recorte,
    )


def secciones_faltantes(texto: str) -> list[str]:
    """Secciones obligatorias (CA17) que no aparecen en una ficha."""
    faltantes = [seccion for seccion in SECCIONES_OBLIGATORIAS if seccion not in texto]
    if LEYENDA not in texto:
        faltantes.append("leyenda de indicio (RN27)")
    return faltantes
