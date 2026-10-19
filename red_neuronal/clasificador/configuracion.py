"""Configuración validada de una ejecución del pipeline.

Cada ejecución se describe con un archivo YAML versionado en
``red_neuronal/configuracion/``. Este módulo define su esquema con pydantic
para que un error (un campo faltante, una proporción imposible) se detecte
al inicio y no después de una hora de entrenamiento en Kaggle.

Realiza: RNF24 CA2 (reproducibilidad), CA8 de la funcionalidad 010
(hiperparámetros fuera del código).
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class ErrorConfiguracion(Exception):
    """El archivo de configuración no existe o no cumple el esquema."""


class _Esquema(BaseModel):
    """Base de todas las secciones: rechaza campos desconocidos.

    Un campo mal escrito (``epoca`` en lugar de ``epocas``) se informa como
    error en vez de ignorarse en silencio y usar el valor por defecto.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)


class ConfiguracionFuente(_Esquema):
    """Una fuente de imágenes: un conjunto público o una carpeta local.

    Los nombres de columnas dependen de cada conjunto de Hugging Face y se
    confirman con el cuaderno de exploración (tarea T25).
    """

    nombre: str = Field(min_length=1, description="Identificador corto, p. ej. 'openfake'.")
    tipo: Literal["hugging_face", "carpeta_local"]
    # Hugging Face
    conjunto: str | None = None
    revision: str = "main"
    division: str = "train"
    columna_imagen: str = "image"
    columna_clase: str | None = None
    valores_sinteticos: list[str] = Field(default_factory=list)
    columna_generador: str | None = None
    excluir: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Filas a descartar por columna, p. ej. {'nsfw_flag': ['True']}.",
    )
    # Carpeta local
    ruta: Path | None = None
    # Cantidades
    cantidad_reales: int = Field(default=0, ge=0)
    cantidad_sinteticas: int = Field(default=0, ge=0)
    licencia: str = Field(min_length=1, description="Licencia verificada del conjunto (CA2).")

    @model_validator(mode="after")
    def _validar_segun_tipo(self) -> "ConfiguracionFuente":
        if self.tipo == "hugging_face":
            if not self.conjunto or not self.columna_clase:
                raise ValueError("una fuente de Hugging Face requiere 'conjunto' y 'columna_clase'")
            if not self.valores_sinteticos:
                raise ValueError("indicar en 'valores_sinteticos' qué valores son sintéticos")
        if self.tipo == "carpeta_local" and self.ruta is None:
            raise ValueError("una fuente 'carpeta_local' requiere 'ruta'")
        if self.cantidad_reales + self.cantidad_sinteticas == 0:
            raise ValueError(f"la fuente '{self.nombre}' no pide ninguna imagen")
        return self


class ConfiguracionProporciones(_Esquema):
    """Proporción de cada partición. Deben sumar 1."""

    entrenamiento: float = Field(gt=0, lt=1)
    validacion: float = Field(gt=0, lt=1)
    prueba: float = Field(gt=0, lt=1)

    @model_validator(mode="after")
    def _validar_suma(self) -> "ConfiguracionProporciones":
        total = self.entrenamiento + self.validacion + self.prueba
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"las proporciones deben sumar 1 (suman {total:.3f})")
        return self


class ConfiguracionDatos(_Esquema):
    """Receta del conjunto de datos y normalización anti-atajos (CA5)."""

    fuentes: list[ConfiguracionFuente] = Field(min_length=1)
    generadores_reservados: list[str] = Field(
        default_factory=list,
        description="Generadores que no se usan para entrenar: solo prueba 'no vista' (CA6).",
    )
    proporciones: ConfiguracionProporciones = ConfiguracionProporciones(
        entrenamiento=0.8, validacion=0.1, prueba=0.1
    )
    calidad_jpeg: tuple[int, int] = (75, 95)
    lado_menor: tuple[int, int] = (256, 512)
    desbalance_tolerado: float = Field(default=0.05, ge=0, lt=1)

    @model_validator(mode="after")
    def _validar_rangos(self) -> "ConfiguracionDatos":
        minimo, maximo = self.calidad_jpeg
        if not 1 <= minimo <= maximo <= 100:
            raise ValueError("'calidad_jpeg' debe ser un rango [min, max] dentro de 1..100")
        minimo, maximo = self.lado_menor
        if not 224 <= minimo <= maximo:
            raise ValueError("'lado_menor' debe ser un rango [min, max] con min >= 224")
        nombres = [fuente.nombre for fuente in self.fuentes]
        if len(nombres) != len(set(nombres)):
            raise ValueError("hay fuentes con el mismo nombre")
        return self


class ConfiguracionEntrenamiento(_Esquema):
    """Hiperparámetros del entrenamiento (ADR-0013)."""

    arquitectura: str = "efficientnet_b0"
    preentrenado: bool = True
    epocas: int = Field(default=10, ge=1)
    tamanio_lote: int = Field(default=64, ge=1)
    tasa_aprendizaje: float = Field(default=3e-4, gt=0)
    decaimiento_pesos: float = Field(default=1e-4, ge=0)
    paciencia: int = Field(default=3, ge=1, description="Épocas sin mejorar antes de parar.")
    tamanio_recorte: int = Field(default=224, ge=32)
    trabajadores_carga: int = Field(default=2, ge=0)
    precision_mixta: bool = True


class ConfiguracionExportacion(_Esquema):
    """Parámetros de la exportación a ONNX (CA14)."""

    opset: int = Field(default=18, ge=18, description="Mínimo del exportador de torch.export.")
    tolerancia: float = Field(default=1e-3, gt=0)


class ConfiguracionCompuerta(_Esquema):
    """Criterios de la compuerta de promoción (CA10, CA15)."""

    auc_minimo: float = Field(default=0.90, gt=0.5, le=1)


class Configuracion(_Esquema):
    """Configuración completa de una ejecución del pipeline."""

    nombre: str = Field(min_length=1)
    semilla: int = Field(default=42, ge=0)
    directorio_trabajo: Path = Path("trabajo")
    datos: ConfiguracionDatos
    entrenamiento: ConfiguracionEntrenamiento = ConfiguracionEntrenamiento()
    exportacion: ConfiguracionExportacion = ConfiguracionExportacion()
    compuerta: ConfiguracionCompuerta = ConfiguracionCompuerta()


def cargar_configuracion(ruta: Path | str) -> Configuracion:
    """Lee y valida un archivo YAML de configuración.

    Lanza ``ErrorConfiguracion`` con un mensaje en español que indica qué
    campo falla, en lugar del error genérico de pydantic o de YAML.
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorConfiguracion(f"no existe el archivo de configuración: {ruta}")
    try:
        contenido = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ErrorConfiguracion(f"el archivo {ruta} no es YAML válido: {error}") from error
    if not isinstance(contenido, dict):
        raise ErrorConfiguracion(f"el archivo {ruta} debe contener un mapa de claves")
    try:
        return Configuracion.model_validate(contenido)
    except ValidationError as error:
        detalles = "; ".join(
            f"{'.'.join(str(parte) for parte in problema['loc'])}: {problema['msg']}"
            for problema in error.errors()
        )
        raise ErrorConfiguracion(f"configuración inválida en {ruta}: {detalles}") from error
