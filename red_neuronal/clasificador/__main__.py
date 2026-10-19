"""Línea de comandos del pipeline: ``python -m clasificador <etapa>``.

Cada subcomando ejecuta una etapa del ciclo de vida con una configuración
YAML. Los cuadernos de Kaggle solo llaman a estos comandos (ADR-0012).

Ejemplos::

    python -m clasificador obtener  --configuracion configuracion/prueba_de_concepto.yaml
    python -m clasificador validar  --configuracion ...
    python -m clasificador preparar --configuracion ...
    python -m clasificador entrenar --configuracion ...
    python -m clasificador exportar --configuracion ... --version 0.1.0
    python -m clasificador evaluar  --configuracion ... [--conjunto-propio /ruta]
    python -m clasificador publicar --configuracion ... --version 0.1.0 \\
        --registro local:/kaggle/working/registro

El código de salida es 0 si la etapa terminó bien y 1 ante un error
esperable (configuración, datos, compuerta), con el motivo en español.

Realiza: CA1 y CA19 de la funcionalidad 010.
"""

import argparse
import json
import sys
from pathlib import Path

from clasificador.configuracion import ErrorConfiguracion, cargar_configuracion
from clasificador.datos.fuentes import ErrorFuente
from clasificador.datos.manifiesto import ErrorManifiesto
from clasificador.datos.obtencion import ErrorObtencion
from clasificador.datos.validacion import ErrorValidacionDatos
from clasificador.exportacion.onnx import ErrorExportacion
from clasificador.registro.compuerta import ErrorCompuerta
from clasificador.registro.registro_modelos import (
    ErrorRegistro,
    RegistroHuggingFace,
    RegistroLocal,
    RegistroModelos,
)

ERRORES_ESPERABLES = (
    ErrorConfiguracion,
    ErrorFuente,
    ErrorManifiesto,
    ErrorObtencion,
    ErrorValidacionDatos,
    ErrorExportacion,
    ErrorCompuerta,
    ErrorRegistro,
    FileNotFoundError,
    ValueError,
)

_TRADUCCIONES_ARGPARSE = (
    ("the following arguments are required", "faltan los argumentos obligatorios"),
    ("invalid choice", "opción inválida"),
    ("choose from", "elegir entre"),
    ("unrecognized arguments", "argumentos no reconocidos"),
    ("expected one argument", "se esperaba un valor"),
    ("argument ", "argumento "),
)

ETAPAS = ("obtener", "validar", "preparar", "entrenar", "exportar", "evaluar", "publicar")


def crear_registro(especificacion: str) -> RegistroModelos:
    """Crea el registro a partir de ``local:<ruta>`` o ``hugging_face:<repositorio>``."""
    tipo, _, destino = especificacion.partition(":")
    if not destino:
        raise ValueError("el registro debe indicarse como 'local:<ruta>' o 'hugging_face:<repo>'")
    if tipo == "local":
        return RegistroLocal(Path(destino))
    if tipo == "hugging_face":
        return RegistroHuggingFace(destino)
    raise ValueError(f"tipo de registro desconocido: '{tipo}'")


class _FormatoAyuda(argparse.HelpFormatter):
    """Formato de la ayuda con el encabezado de uso en español."""

    def add_usage(self, usage, actions, groups, prefix=None):
        # argparse pasa prefix="" al armar el nombre de los subcomandos: se respeta.
        super().add_usage(usage, actions, groups, "uso: " if prefix is None else prefix)


class AnalizadorEnEspaniol(argparse.ArgumentParser):
    """``ArgumentParser`` con títulos, ayuda y errores en español.

    ``argparse`` no trae traducción al español: se reemplazan los textos
    visibles para que toda la interfaz del proyecto esté en español.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("formatter_class", _FormatoAyuda)
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self._positionals.title = "argumentos posicionales"
        self._optionals.title = "opciones"
        self.add_argument(
            "-h", "--ayuda", action="help", default=argparse.SUPPRESS,
            help="muestra esta ayuda y termina",
        )

    def error(self, message: str):
        """Informa el error en español y termina con código 2."""
        for original, traduccion in _TRADUCCIONES_ARGPARSE:
            message = message.replace(original, traduccion)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")


def construir_analizador() -> argparse.ArgumentParser:
    """Define los subcomandos y sus argumentos."""
    analizador = AnalizadorEnEspaniol(
        prog="python -m clasificador",
        description="Pipeline del clasificador de imágenes sintéticas (funcionalidad 010).",
    )
    subcomandos = analizador.add_subparsers(
        dest="etapa", required=True, metavar="etapa", parser_class=AnalizadorEnEspaniol
    )
    descripciones = {
        "obtener": "descarga la muestra de cada fuente",
        "validar": "valida el conjunto descargado",
        "preparar": "normaliza y particiona el conjunto",
        "entrenar": "entrena y calibra el modelo",
        "exportar": "exporta el modelo a ONNX y verifica la coincidencia",
        "evaluar": "evalúa el modelo ONNX",
        "publicar": "genera la ficha, aplica la compuerta y publica la versión",
    }
    for etapa in ETAPAS:
        sub = subcomandos.add_parser(etapa, help=descripciones[etapa])
        sub.add_argument("--configuracion", required=True, type=Path, help="archivo YAML")
        if etapa in ("exportar", "publicar"):
            sub.add_argument("--version", required=True, help="versión MAJOR.MINOR.PATCH")
        if etapa == "publicar":
            sub.add_argument(
                "--registro", required=True,
                help="'local:<ruta>' o 'hugging_face:<usuario/repositorio>'",
            )
        if etapa == "evaluar":
            sub.add_argument("--conjunto-propio", type=Path, default=None,
                             help="carpeta del conjunto propio (CA12, CA13)")
    return analizador


def ejecutar(argumentos: argparse.Namespace) -> object:
    """Ejecuta la etapa pedida y devuelve su resultado."""
    # Se importa acá para que '--help' no cargue PyTorch.
    # pylint: disable-next=import-outside-toplevel
    from clasificador import pipeline

    configuracion = cargar_configuracion(argumentos.configuracion)
    etapa = argumentos.etapa
    if etapa == "exportar":
        return pipeline.etapa_exportar(configuracion, argumentos.version)
    if etapa == "evaluar":
        return pipeline.etapa_evaluar(configuracion, argumentos.conjunto_propio)
    if etapa == "publicar":
        resultado = pipeline.etapa_publicar(
            configuracion, argumentos.version, crear_registro(argumentos.registro)
        )
        return {clave: valor for clave, valor in resultado.items() if clave != "ficha"}
    return getattr(pipeline, f"etapa_{etapa}")(configuracion)


def _resumir(resultado: object) -> str:
    """Texto breve del resultado para la consola."""
    if isinstance(resultado, list):
        return f"{len(resultado)} imágenes"
    if hasattr(resultado, "resumen"):
        return "sin errores\n" + json.dumps(resultado.resumen, ensure_ascii=False, indent=2)
    if isinstance(resultado, dict):
        return json.dumps(
            {k: v for k, v in resultado.items() if k != "historial"},
            ensure_ascii=False, default=str, indent=2,
        )
    return str(resultado)


def principal(argv: list[str] | None = None) -> int:
    """Punto de entrada: devuelve el código de salida."""
    argumentos = construir_analizador().parse_args(argv)
    try:
        resultado = ejecutar(argumentos)
    except ERRORES_ESPERABLES as error:
        print(f"Error en la etapa '{argumentos.etapa}': {error}", file=sys.stderr)
        return 1
    print(f"Etapa '{argumentos.etapa}' terminada: {_resumir(resultado)}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
