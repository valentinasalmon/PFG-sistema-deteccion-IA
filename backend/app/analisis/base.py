"""Interfaz común de las capas de análisis y tipos de su resultado.

Realiza: RF43 (nivel de indicio, anomalías y conclusión por capa); RN26,
RN27, RN29; ADR-0006.
"""
from dataclasses import asdict, dataclass, field
from datetime import datetime

SEVERIDAD_DIRECTO = "directo"
SEVERIDAD_FUERTE = "fuerte"
SEVERIDAD_MODERADO = "moderado"
SEVERIDAD_DEBIL = "debil"
SEVERIDAD_NEUTRO = "neutro"
SEVERIDADES = (
    SEVERIDAD_DIRECTO, SEVERIDAD_FUERTE, SEVERIDAD_MODERADO, SEVERIDAD_DEBIL, SEVERIDAD_NEUTRO,
)

RECOMENDACION = (
    "Este resultado es un indicio y no constituye una conclusión definitiva. "
    "Se recomienda consultar a un perito especializado en informática forense."
)

# Términos de veredicto que ninguna conclusión puede afirmar (RN27, RF43 CA2).
TERMINOS_DE_VEREDICTO = ("falsa", "falso", "auténtica", "autentica", "adulterada", "fraude")


class CapaNoDisponible(Exception):
    """La capa no pudo ejecutarse (por ejemplo, falta una herramienta); RN26."""


@dataclass
class Anomalia:
    """Hallazgo de una capa, con la severidad que aporta al nivel de indicio."""

    campo: str
    valor: str
    descripcion: str
    severidad: str


@dataclass
class ResultadoCapa:
    """Resultado de una capa sobre una imagen (RF43)."""

    nivel: int
    anomalias: list
    conclusion: str
    detalle: dict = field(default_factory=dict)

    def como_dict(self):
        """Representación serializable (para pruebas y registros)."""
        return asdict(self)


@dataclass
class ContextoImagen:
    """Datos de la imagen que las capas necesitan además del contenido."""

    formato: str
    ancho: int
    alto: int
    cargada_en: datetime


class CapaAnalisis:
    """Interfaz de una capa: un nombre, una versión y ``analizar``.

    Una capa nueva hereda de esta clase y se registra en ``registro.py``,
    sin modificar las existentes (ADR-0006).
    """

    nombre = ""
    titulo = ""

    def version(self):
        """Versión de la capa y de sus herramientas, para la reproducibilidad (RN29)."""
        raise NotImplementedError

    def analizar(self, contenido, contexto):
        """Analiza los bytes de la imagen y devuelve un ``ResultadoCapa``.

        Raises:
            CapaNoDisponible: si la capa no puede ejecutarse; el servicio la
                informa como "No disponible" y sigue con las demás (RN26).
        """
        raise NotImplementedError
