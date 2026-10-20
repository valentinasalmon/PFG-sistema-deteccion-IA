"""Entorno de plantillas Jinja2 de los documentos PDF y conversión con WeasyPrint.

Lo comparten la copia de datos personales (019) y el informe de análisis
(008), para que tengan los mismos filtros de fecha y el mismo motor.

Realiza: RF09, RF44.
"""
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape

DIRECTORIO_PLANTILLAS = Path(__file__).resolve().parents[1] / "plantillas" / "informes"
ZONA_HORARIA = ZoneInfo("America/Argentina/Buenos_Aires")


def formatear_iso(valor):
    """Fecha ISO como ``dd/mm/aaaa hh:mm`` (tal cual, en UTC); sin hora, ``dd/mm/aaaa``."""
    if not valor:
        return "—"
    fecha, _, hora = valor.partition("T")
    anio, mes, dia = fecha.split("-")
    return f"{dia}/{mes}/{anio} {hora[:5]}".strip()


def formatear_hora_argentina(valor):
    """Fecha y hora UTC (``datetime`` sin zona) en la hora de Argentina, ``dd/mm/aaaa hh:mm``."""
    if not valor:
        return "—"
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor)
    local = valor.replace(tzinfo=timezone.utc).astimezone(ZONA_HORARIA)
    return local.strftime("%d/%m/%Y %H:%M")


def formatear_dia(valor):
    """Fecha calendario (``date``) como ``dd/mm/aaaa``."""
    return valor.strftime("%d/%m/%Y") if valor else "—"


entorno = Environment(
    loader=FileSystemLoader(DIRECTORIO_PLANTILLAS),
    autoescape=select_autoescape(["html"]),
)
entorno.filters["fecha"] = formatear_iso
entorno.filters["hora_argentina"] = formatear_hora_argentina
entorno.filters["dia"] = formatear_dia


def html_a_pdf(plantilla, **datos):
    """Renderiza la plantilla y la convierte a PDF con WeasyPrint."""
    # Se importa aquí: WeasyPrint tarda en cargar y solo hace falta al generar un PDF.
    from weasyprint import HTML  # pylint: disable=import-outside-toplevel

    return HTML(string=entorno.get_template(plantilla).render(**datos)).write_pdf()


def version_weasyprint():
    """Versión de WeasyPrint, para registrarla en el informe (RN29)."""
    from weasyprint import __version__  # pylint: disable=import-outside-toplevel

    return __version__
