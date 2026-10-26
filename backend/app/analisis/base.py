"""Interfaz común de las capas de análisis y tipos de su resultado.

Realiza: RF43 (nivel de indicio, anomalías y conclusión por capa); RN26,
RN27, RN29; ADR-0006.
"""
import json
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

# --- Nivel de indicio común a las capas basadas en reglas (plan de la 007) ---

BASES = {
    SEVERIDAD_DIRECTO: 90, SEVERIDAD_FUERTE: 70, SEVERIDAD_MODERADO: 45,
    SEVERIDAD_DEBIL: 20, SEVERIDAD_NEUTRO: 0,
}
INCREMENTO_POR_ANOMALIA = 10
# El 100 % se reserva para una declaración de IA con firma C2PA confiable (RN28).
NIVEL_MAXIMO_REGLAS = 90
NIVEL_MAXIMO = 100

# Términos de veredicto que ninguna conclusión puede afirmar (RN27, RF43 CA2).
TERMINOS_DE_VEREDICTO = ("falsa", "falso", "auténtica", "autentica", "adulterada", "fraude")


LARGO_MAXIMO_VALOR = 300


def texto_acotado(valor):
    """Texto de a lo sumo 300 caracteres para mostrar un dato extraído de la imagen.

    Las herramientas pueden devolver números o estructuras (regresión del TIF),
    y un archivo malicioso puede traer textos enormes.
    """
    if isinstance(valor, (dict, list)):
        valor = json.dumps(valor, ensure_ascii=False)
    texto = str(valor).strip()
    return texto if len(texto) <= LARGO_MAXIMO_VALOR else texto[:LARGO_MAXIMO_VALOR] + "…"


def calcular_nivel(anomalias):
    """Nivel de indicio de 0 a 90 a partir de las severidades de las anomalías.

    Toma la base de la anomalía más grave y suma 10 por cada otra anomalía
    moderada o más grave. El método está documentado en el plan de la 007 y lo
    comparten las capas de metadatos y de credenciales de contenido.

    Realiza: RF43 (CA1).
    """
    if not anomalias:
        return 0
    bases = sorted((BASES[a.severidad] for a in anomalias), reverse=True)
    adicionales = sum(1 for base in bases[1:] if base >= BASES[SEVERIDAD_MODERADO])
    return min(NIVEL_MAXIMO_REGLAS, bases[0] + INCREMENTO_POR_ANOMALIA * adicionales)


def describir_intensidad(nivel):
    """Nombre de la intensidad de un nivel mayor que 0, para las conclusiones."""
    if nivel >= BASES[SEVERIDAD_FUERTE]:
        return "indicios fuertes"
    if nivel >= BASES[SEVERIDAD_MODERADO]:
        return "indicios moderados"
    return "indicios débiles"


def anomalias_principales(anomalias, cantidad=2):
    """Las anomalías más graves, que la conclusión cita textualmente."""
    return sorted(anomalias, key=lambda a: BASES[a.severidad], reverse=True)[:cantidad]


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
    # Imagen PNG que acompaña al resultado (el mapa ELA de la 011); el servicio
    # de análisis la guarda en el almacenamiento.
    imagen: bytes | None = None

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
