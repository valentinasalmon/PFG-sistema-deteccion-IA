"""Exploración de conjuntos candidatos antes de armar una receta (tarea T25).

Para cada conjunto candidato de Hugging Face responde, **sin bajar el
conjunto entero**:

1. si está disponible y en qué revisión exacta (el *commit* del conjunto);
2. qué licencia declara su ficha en esa revisión (CA2): si no declara una
   licencia verificable, el conjunto queda **excluido** y anotado;
3. qué columnas tiene y si existen las que espera la receta;
4. cuántas imágenes hay por clase y por generador en una muestra de archivos;
5. qué formato, tamaño y calidad JPEG tienen unas imágenes de muestra, para
   ver si hay sesgos de formato entre las clases («Fake or JPEG?»).

Con eso propone el bloque de la receta de cada fuente: revisión fija,
archivos elegidos al azar con semilla, generadores con más imágenes y una
cuota por generador (lecciones de la prueba de concepto).

El acceso a Hugging Face está detrás de ``InspectorConjuntos`` (Strategy):
las pruebas usan un inspector simulado y nunca acceden a la red.

Realiza: CA2 de la funcionalidad 010 y tareas T25 y T27.
"""

import io
import json
import math
import os
import random
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

import yaml
from PIL import Image, UnidentifiedImageError
from pydantic import Field, ValidationError, model_validator

from clasificador.configuracion import ErrorConfiguracion, _Esquema

# Licencias que la ficha puede declarar y que no permiten saber qué se puede
# hacer con los datos: el conjunto se excluye salvo verificación manual.
LICENCIAS_NO_VERIFICABLES = {"", "other", "unknown", "none", "cc"}

# Tabla de cuantización de luminancia del estándar JPEG (anexo K), en la que
# se basan casi todos los codificadores. Solo importa su suma.
_SUMA_TABLA_ESTANDAR = sum((
    16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99,
))

MARGEN_ARCHIVOS = 1.3  # se eligen archivos con un 30 % más de lo pedido


class Candidato(_Esquema):
    """Un conjunto candidato y las columnas que se esperan de él."""

    nombre: str = Field(min_length=1)
    conjunto: str = Field(min_length=3, description="Identificador en Hugging Face.")
    revision: str = "main"
    columna_imagen: str = "image"
    columna_clase: str | None = None
    valores_sinteticos: list[str] = Field(default_factory=list)
    clase_fija: Literal["real", "sintetica"] | None = None
    columna_generador: str | None = None
    uso: str = Field(min_length=1, description="Para qué se usaría: entrenamiento, no_visto...")
    licencia_verificada_a_mano: str | None = Field(
        default=None,
        description="Licencia leída a mano en el artículo o el sitio, con su fuente.",
    )

    @model_validator(mode="after")
    def _validar_clase(self) -> "Candidato":
        if self.clase_fija is None and not (self.columna_clase and self.valores_sinteticos):
            raise ValueError(
                f"'{self.nombre}': indicar 'columna_clase' y 'valores_sinteticos', o 'clase_fija'"
            )
        return self


class ListaCandidatos(_Esquema):
    """Archivo YAML con los candidatos y los parámetros de la exploración."""

    semilla: int = Field(default=42, ge=0)
    archivos_por_conjunto: int = Field(default=12, ge=1)
    imagenes_por_conjunto: int = Field(default=24, ge=1)
    candidatos: list[Candidato] = Field(min_length=1)


def cargar_candidatos(ruta: Path | str) -> ListaCandidatos:
    """Lee y valida el archivo YAML de candidatos."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorConfiguracion(f"no existe el archivo de candidatos: {ruta}")
    try:
        return ListaCandidatos.model_validate(yaml.safe_load(ruta.read_text(encoding="utf-8")))
    except (yaml.YAMLError, ValidationError) as error:
        raise ErrorConfiguracion(f"archivo de candidatos inválido {ruta}: {error}") from error


@dataclass(frozen=True)
class InformacionConjunto:
    """Lo que el registro de conjuntos dice de un conjunto en una revisión."""

    revision_exacta: str
    licencia: str
    requiere_aceptar_condiciones: bool
    archivos: list[str]


class ErrorInspeccion(Exception):
    """El conjunto no existe, es privado o no se puede leer."""


class InspectorConjuntos(ABC):
    """Interfaz de acceso a un registro de conjuntos de datos."""

    @abstractmethod
    def informacion(self, conjunto: str, revision: str) -> InformacionConjunto:
        """Revisión exacta, licencia de la ficha y lista de archivos."""

    @abstractmethod
    def columnas(self, conjunto: str, revision: str, archivo: str) -> list[str]:
        """Nombres de las columnas de un archivo Parquet."""

    @abstractmethod
    def leer_filas(
        self, conjunto: str, revision: str, archivo: str, columnas: list[str]
    ) -> list[dict]:
        """Lee solo las columnas pedidas de todas las filas del archivo.

        Sin columnas, devuelve una fila vacía por cada fila del archivo.
        """

    @abstractmethod
    def leer_imagenes(
        self, conjunto: str, revision: str, archivo: str, columnas: list[str], cantidad: int
    ) -> list[dict]:
        """Lee las primeras ``cantidad`` filas con la imagen y las columnas pedidas."""


class InspectorHuggingFace(InspectorConjuntos):
    """Inspector real: API de Hugging Face y lectura parcial de Parquet.

    Lee el esquema y las columnas livianas sin descargar imágenes; para las
    imágenes de muestra baja un solo grupo de filas de cada archivo.
    """

    def __init__(self, token: str | None = None) -> None:
        # pylint: disable=import-outside-toplevel
        from huggingface_hub import HfApi, HfFileSystem

        token = token or os.environ.get("HF_TOKEN")
        self._api = HfApi(token=token)
        self._sistema = HfFileSystem(token=token)

    def informacion(self, conjunto: str, revision: str) -> InformacionConjunto:
        """Consulta la ficha del conjunto en la revisión pedida."""
        try:
            datos = self._api.dataset_info(conjunto, revision=revision)
        except Exception as error:  # pylint: disable=broad-exception-caught
            raise ErrorInspeccion(f"{type(error).__name__}: {error}") from error
        ficha = datos.card_data.to_dict() if datos.card_data else {}
        licencia = ficha.get("license") or ""
        if isinstance(licencia, list):
            licencia = ", ".join(str(valor) for valor in licencia)
        return InformacionConjunto(
            revision_exacta=datos.sha,
            licencia=str(licencia),
            requiere_aceptar_condiciones=bool(datos.gated),
            archivos=sorted(archivo.rfilename for archivo in datos.siblings or []),
        )

    def _abrir(self, conjunto: str, revision: str, archivo: str):
        # pylint: disable-next=import-outside-toplevel
        import pyarrow.parquet as pq

        abierto = self._sistema.open(f"datasets/{conjunto}@{revision}/{archivo}", "rb")
        return abierto, pq.ParquetFile(abierto)

    def columnas(self, conjunto: str, revision: str, archivo: str) -> list[str]:
        """Lee solo el esquema, que está al final del archivo."""
        abierto, parquet = self._abrir(conjunto, revision, archivo)
        with abierto:
            return list(parquet.schema_arrow.names)

    def leer_filas(
        self, conjunto: str, revision: str, archivo: str, columnas: list[str]
    ) -> list[dict]:
        """Lee las columnas livianas de todo el archivo."""
        abierto, parquet = self._abrir(conjunto, revision, archivo)
        with abierto:
            if not columnas:
                return [{} for _ in range(parquet.metadata.num_rows)]
            return parquet.read(columns=columnas).to_pylist()

    def leer_imagenes(
        self, conjunto: str, revision: str, archivo: str, columnas: list[str], cantidad: int
    ) -> list[dict]:
        """Lee el primer grupo de filas: baja imágenes de un solo bloque."""
        abierto, parquet = self._abrir(conjunto, revision, archivo)
        with abierto:
            return parquet.read_row_group(0, columns=columnas).slice(0, cantidad).to_pylist()


def estimar_calidad_jpeg(imagen: Image.Image) -> int | None:
    """Estima la calidad JPEG (1 a 100) a partir de la tabla de luminancia.

    Invierte la fórmula de escala de libjpeg comparando la suma de la tabla
    del archivo con la del estándar. Devuelve ``None`` si no es un JPEG.
    """
    tablas = getattr(imagen, "quantization", None)
    if not tablas:
        return None
    escala = 100 * sum(tablas[0]) / _SUMA_TABLA_ESTANDAR
    calidad = (200 - escala) / 2 if escala <= 100 else 5000 / escala
    return max(1, min(100, round(calidad)))


def describir_imagen(contenido: bytes) -> dict:
    """Formato, tamaño, modo de color y calidad JPEG de una imagen."""
    try:
        with Image.open(io.BytesIO(contenido)) as imagen:
            return {
                "formato": (imagen.format or "desconocido").lower(),
                "ancho": imagen.width,
                "alto": imagen.height,
                "modo": imagen.mode,
                "calidad_jpeg": estimar_calidad_jpeg(imagen),
            }
    except (UnidentifiedImageError, OSError):
        return {"formato": "ilegible", "ancho": 0, "alto": 0, "modo": "", "calidad_jpeg": None}


def licencia_verificable(licencia: str) -> bool:
    """Indica si la licencia declarada permite saber qué se puede hacer."""
    return licencia.strip().lower() not in LICENCIAS_NO_VERIFICABLES


@dataclass
class InformeConjunto:  # pylint: disable=too-many-instance-attributes
    """Resultado de explorar un candidato."""

    nombre: str
    conjunto: str
    uso: str
    disponible: bool = False
    incluido: bool = False
    motivos_exclusion: list[str] = field(default_factory=list)
    revision_exacta: str = ""
    licencia: str = ""
    requiere_aceptar_condiciones: bool = False
    cantidad_archivos: int = 0
    columnas: list[str] = field(default_factory=list)
    columnas_faltantes: list[str] = field(default_factory=list)
    archivos_explorados: dict[str, dict[str, int]] = field(default_factory=dict)
    por_clase: dict[str, int] = field(default_factory=dict)
    por_generador: dict[str, int] = field(default_factory=dict)
    muestra_imagenes: dict[str, list[dict]] = field(default_factory=dict)

    def resumen_formatos(self) -> dict[str, dict]:
        """Formatos, tamaño mediano y calidad JPEG mediana por clase."""
        resumen = {}
        for clase, imagenes in self.muestra_imagenes.items():
            lados = sorted(min(imagen["ancho"], imagen["alto"]) for imagen in imagenes)
            calidades = sorted(i["calidad_jpeg"] for i in imagenes if i["calidad_jpeg"])
            resumen[clase] = {
                "formatos": dict(Counter(imagen["formato"] for imagen in imagenes)),
                "lado_menor_mediano": lados[len(lados) // 2] if lados else None,
                "calidad_jpeg_mediana": calidades[len(calidades) // 2] if calidades else None,
            }
        return resumen


def _clase_de(fila: dict, candidato: Candidato) -> str:
    if candidato.clase_fija:
        return candidato.clase_fija
    valor = str(fila.get(candidato.columna_clase))
    return "sintetica" if valor in candidato.valores_sinteticos else "real"


def _explorar_archivos(  # pylint: disable=too-many-locals
    inspector: InspectorConjuntos, candidato: Candidato, informe: InformeConjunto,
    archivos: list[str], cantidad_imagenes: int,
) -> None:
    """Cuenta clases y generadores y describe imágenes de muestra."""
    # Con una sola clase y sin generador no se lee ninguna columna: solo se
    # cuentan las filas.
    livianas = [c for c in (candidato.columna_clase, candidato.columna_generador) if c]
    por_clase: Counter = Counter()
    por_generador: Counter = Counter()
    for archivo in archivos:
        filas = inspector.leer_filas(
            candidato.conjunto, informe.revision_exacta, archivo, livianas
        )
        clases = Counter(_clase_de(fila, candidato) for fila in filas)
        informe.archivos_explorados[archivo] = dict(clases)
        por_clase.update(clases)
        if candidato.columna_generador:
            por_generador.update(
                str(fila.get(candidato.columna_generador))
                for fila in filas if _clase_de(fila, candidato) == "sintetica"
            )
    informe.por_clase = dict(por_clase)
    informe.por_generador = dict(por_generador.most_common())

    muestra: dict[str, list[dict]] = {"real": [], "sintetica": []}
    # Las clases suelen estar en archivos separados: se lee hasta la cantidad
    # pedida de cada archivo (un solo grupo de filas) hasta completar las dos.
    for archivo in archivos:
        if all(len(lista) >= cantidad_imagenes for lista in muestra.values()):
            break
        filas = inspector.leer_imagenes(
            candidato.conjunto, informe.revision_exacta, archivo,
            [c for c in (candidato.columna_imagen, candidato.columna_clase) if c],
            cantidad_imagenes,
        )
        for fila in filas:
            valor = fila.get(candidato.columna_imagen)
            contenido = valor.get("bytes") if isinstance(valor, dict) else valor
            lista = muestra[_clase_de(fila, candidato)]
            if isinstance(contenido, bytes) and len(lista) < cantidad_imagenes:
                lista.append(describir_imagen(contenido))
    informe.muestra_imagenes = {clase: lista for clase, lista in muestra.items() if lista}


def explorar_candidato(
    inspector: InspectorConjuntos, candidato: Candidato, cantidad_archivos: int,
    cantidad_imagenes: int, semilla: int,
) -> InformeConjunto:
    """Explora un candidato y decide si queda incluido o excluido (CA2)."""
    informe = InformeConjunto(candidato.nombre, candidato.conjunto, candidato.uso)
    try:
        info = inspector.informacion(candidato.conjunto, candidato.revision)
    except ErrorInspeccion as error:
        informe.motivos_exclusion.append(f"no disponible: {error}")
        return informe
    informe.disponible = True
    informe.revision_exacta = info.revision_exacta
    informe.licencia = candidato.licencia_verificada_a_mano or info.licencia
    informe.requiere_aceptar_condiciones = info.requiere_aceptar_condiciones
    if not licencia_verificable(info.licencia) and not candidato.licencia_verificada_a_mano:
        informe.motivos_exclusion.append(
            f"la ficha no declara una licencia verificable ('{info.licencia or 'vacía'}')"
        )
    parquets = [archivo for archivo in info.archivos if archivo.endswith(".parquet")]
    informe.cantidad_archivos = len(parquets)
    if not parquets:
        extensiones = Counter(
            Path(archivo).suffix or "(sin extensión)" for archivo in info.archivos
        )
        informe.motivos_exclusion.append(
            f"no tiene archivos Parquet (tiene {dict(extensiones)}): revisar a mano"
        )
        return informe
    try:
        informe.columnas = inspector.columnas(
            candidato.conjunto, informe.revision_exacta, parquets[0]
        )
        esperadas = [
            c for c in (candidato.columna_imagen, candidato.columna_clase,
                        candidato.columna_generador) if c
        ]
        informe.columnas_faltantes = [c for c in esperadas if c not in informe.columnas]
        if informe.columnas_faltantes:
            informe.motivos_exclusion.append(
                f"faltan las columnas {informe.columnas_faltantes}: corregir el candidato"
            )
            return informe
        elegidos = sorted(
            random.Random(semilla).sample(parquets, min(cantidad_archivos, len(parquets)))
        )
        _explorar_archivos(inspector, candidato, informe, elegidos, cantidad_imagenes)
    except Exception as error:  # pylint: disable=broad-exception-caught
        informe.motivos_exclusion.append(f"no se pudo leer: {type(error).__name__}: {error}")
    informe.incluido = not informe.motivos_exclusion
    return informe


def proponer_fuente(  # pylint: disable=too-many-arguments
    informe: InformeConjunto, candidato: Candidato, *, cantidad_reales: int,
    cantidad_sinteticas: int, cantidad_generadores: int, semilla: int,
) -> dict:
    """Propone el bloque de la receta para una fuente explorada (T27).

    Toma los ``cantidad_generadores`` generadores con más imágenes, fija una
    cuota por generador y elige, entre los archivos explorados (cuyo
    contenido ya se conoce), los necesarios para cubrir lo pedido con margen.
    """
    generadores = list(informe.por_generador)[:cantidad_generadores]
    cuota = math.ceil(cantidad_sinteticas / max(1, len(generadores))) if generadores else None
    archivos = list(informe.archivos_explorados)
    random.Random(semilla).shuffle(archivos)
    elegidos: list[str] = []
    reales = sinteticas = 0
    for archivo in archivos:
        if (reales >= MARGEN_ARCHIVOS * cantidad_reales
                and sinteticas >= MARGEN_ARCHIVOS * cantidad_sinteticas):
            break
        conteo = informe.archivos_explorados[archivo]
        if conteo.get("real", 0) or conteo.get("sintetica", 0):
            elegidos.append(archivo)
            reales += conteo.get("real", 0)
            sinteticas += conteo.get("sintetica", 0)
    propuesta = {
        "nombre": candidato.nombre,
        "tipo": "hugging_face",
        "conjunto": candidato.conjunto,
        "revision": informe.revision_exacta,
        "columna_imagen": candidato.columna_imagen,
        "archivos": sorted(elegidos),
        "cantidad_reales": cantidad_reales,
        "cantidad_sinteticas": cantidad_sinteticas,
        "licencia": informe.licencia,
    }
    if candidato.clase_fija:
        propuesta["clase_fija"] = candidato.clase_fija
    else:
        propuesta["columna_clase"] = candidato.columna_clase
        propuesta["valores_sinteticos"] = list(candidato.valores_sinteticos)
    if candidato.columna_generador:
        propuesta["columna_generador"] = candidato.columna_generador
    if generadores:
        propuesta["generadores_incluidos"] = generadores
        propuesta["cuota_por_generador"] = cuota
    return propuesta


def tabla_markdown(informes: list[InformeConjunto]) -> str:
    """Tabla de fuentes con su licencia y decisión, para la bitácora."""
    lineas = [
        "| Conjunto | Uso | Revisión | Licencia | Condiciones | Reales / sintéticas "
        "(muestra) | Generadores | Formatos real → sintética | Decisión |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for informe in informes:
        formatos = informe.resumen_formatos()
        texto_formatos = " → ".join(
            ", ".join(f"{k} {v}" for k, v in formatos.get(clase, {}).get("formatos", {}).items())
            or "—"
            for clase in ("real", "sintetica")
        )
        decision = "incluido" if informe.incluido else "excluido: " + "; ".join(
            informe.motivos_exclusion
        )
        condiciones = "sí" if informe.requiere_aceptar_condiciones else "no"
        lineas.append(
            f"| {informe.conjunto} | {informe.uso} | `{informe.revision_exacta[:10] or '—'}` "
            f"| {informe.licencia or '—'} | {condiciones} "
            f"| {informe.por_clase.get('real', 0)} / {informe.por_clase.get('sintetica', 0)} "
            f"| {len(informe.por_generador)} | {texto_formatos} | {decision} |"
        )
    return "\n".join(lineas) + "\n"


def explorar(
    lista: ListaCandidatos, salida: Path, inspector: InspectorConjuntos | None = None
) -> list[InformeConjunto]:
    """Explora todos los candidatos y escribe ``exploracion.json`` y ``.md``."""
    inspector = inspector or InspectorHuggingFace()
    informes = []
    for candidato in lista.candidatos:
        print(f"Explorando {candidato.conjunto}...", flush=True)
        informes.append(
            explorar_candidato(
                inspector, candidato, lista.archivos_por_conjunto,
                lista.imagenes_por_conjunto, lista.semilla,
            )
        )
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "exploracion.json").write_text(
        json.dumps(
            [{**asdict(i), "resumen_formatos": i.resumen_formatos()} for i in informes],
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )
    (salida / "exploracion.md").write_text(tabla_markdown(informes), encoding="utf-8")
    return informes
