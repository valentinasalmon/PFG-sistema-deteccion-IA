"""Separación del conjunto propio en evaluación fija y ajuste (decisión del 2026-11-11).

La autora decidió mejorar la red por versiones con datos nuevos. Para que la
mejora se mida sin trampa, el conjunto propio se divide en dos lados que nunca
se mezclan:

- **evaluación**: fija, nunca se usa para entrenar; compara cada versión con
  la anterior (compuerta de las versiones MINOR);
- **ajuste**: puede sumarse al entrenamiento de una versión nueva.

La unidad que se asigna es el **grupo**, no el archivo: todas las herramientas
y las dos variantes (original y captura) de un mismo prompt van del mismo lado.
Si no, el modelo podría entrenar con la versión de ChatGPT de una escena y
evaluarse con la de Gemini de la misma escena (fuga).

Reglas, en orden:

1. Prompts de la lista maestra (números 1 a 199): la tabla fija
   ``configuracion/particion_conjunto_propio.csv``, estratificada por escena
   (y por tono de piel en las lesiones). Se generó una vez con
   ``generar_tabla`` y no se recalcula.
2. Ediciones (200 a 299): van del lado de su foto de origen, que se anota en
   la planilla; sin ella, por la regla 3 con su propio nombre.
3. Fotos reales y cualquier otro ``<escena>-<número>``: huella SHA-256 de
   ``escena-número`` con una semilla fija; la mitad va a cada lado.
4. Archivos sin ese formato (por ejemplo, de CarDD): huella SHA-256 del
   contenido del archivo, con la misma regla.

Todas las reglas dependen solo del nombre o del contenido: una imagen nunca
cambia de lado al sumar otras.

Realiza: CA12 y CA13 de la funcionalidad 010; decisión de la autora del 2026-11-11.
"""

import csv
import hashlib
import math
import re
from collections import defaultdict
from pathlib import Path

LADO_EVALUACION = "evaluacion"
LADO_AJUSTE = "ajuste"
LADOS = (LADO_EVALUACION, LADO_AJUSTE)

SEMILLA = "evidentia-conjunto-propio-v1"
PROPORCION_EVALUACION = 0.5
TABLA_FIJA = Path(__file__).resolve().parents[2] / "configuracion" / "particion_conjunto_propio.csv"

_PATRON = re.compile(r"^(?P<escena>\d{2}-[a-z-]+?)-(?P<numero>\d+)$")


def _fraccion(texto: str) -> float:
    """Número entre 0 y 1 que depende solo del texto (huella con semilla fija)."""
    huella = hashlib.sha256(f"{SEMILLA}:{texto}".encode("utf-8")).hexdigest()
    return int(huella[:12], 16) / 16**12


def _lado_por_fraccion(texto: str) -> str:
    return LADO_EVALUACION if _fraccion(texto) < PROPORCION_EVALUACION else LADO_AJUSTE


def generar_tabla(prompts: list[dict]) -> list[dict]:
    """Asigna un lado a cada prompt de la lista maestra, estratificado.

    ``prompts`` tiene ``numero``, ``archivo``, ``escena`` y ``tono`` (vacío si
    no aplica). Dentro de cada estrato (escena y tono) se ordenan por huella y
    la primera mitad va a evaluación: cada escena y cada tono quedan
    representados en los dos lados. Cuando un estrato tiene un número impar,
    el que sobra va una vez a evaluación y otra a ajuste, alternando, para
    que el total quede parejo.
    """
    estratos: dict[tuple, list[dict]] = defaultdict(list)
    for prompt in prompts:
        estratos[(prompt["escena"], prompt.get("tono", ""))].append(prompt)
    lados = {}
    impares = 0
    for clave in sorted(estratos):
        ordenados = sorted(estratos[clave], key=lambda p: _fraccion(str(int(p["numero"]))))
        exacta = len(ordenados) * PROPORCION_EVALUACION
        if exacta == int(exacta):
            cantidad_evaluacion = int(exacta)
        else:
            cantidad_evaluacion = math.ceil(exacta) if impares % 2 == 0 else math.floor(exacta)
            impares += 1
        for posicion, prompt in enumerate(ordenados):
            lados[int(prompt["numero"])] = (
                LADO_EVALUACION if posicion < cantidad_evaluacion else LADO_AJUSTE
            )
    return [
        {"numero": int(p["numero"]), "archivo": p["archivo"], "escena": p["escena"],
         "lado": lados[int(p["numero"])]}
        for p in sorted(prompts, key=lambda p: int(p["numero"]))
    ]


def leer_tabla(ruta: Path = TABLA_FIJA) -> dict[int, str]:
    """Número de prompt → lado, según la tabla fija versionada."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return {int(fila["numero"]): fila["lado"] for fila in csv.DictReader(archivo)}


def lado_de(nombre_archivo: str, contenido: bytes | None = None,
            foto_de_origen: str | None = None, tabla: dict[int, str] | None = None) -> str:
    """Lado (evaluación o ajuste) de una imagen del conjunto propio.

    Args:
        nombre_archivo: nombre o ruta del archivo, con o sin extensión.
        contenido: bytes de la imagen; solo hacen falta si el nombre no sigue
            el formato ``<escena>-<número>``.
        foto_de_origen: para una edición, el nombre de la foto real de la que
            sale (columna de la planilla).
        tabla: tabla fija ya leída; por defecto, la del repositorio.

    Raises:
        ValueError: si el nombre no sigue el formato y no se pasa el contenido.
    """
    coincidencia = _PATRON.match(Path(nombre_archivo).stem.lower())
    if not coincidencia:
        if contenido is None:
            raise ValueError(
                f"{nombre_archivo}: el nombre no sigue <escena>-<número>; hace falta el contenido"
            )
        return _lado_por_fraccion(hashlib.sha256(contenido).hexdigest())
    numero = int(coincidencia["numero"])
    if numero < 200:
        tabla = leer_tabla() if tabla is None else tabla
        if numero in tabla:
            return tabla[numero]
    if 200 <= numero < 300 and foto_de_origen:
        return lado_de(foto_de_origen, tabla=tabla)
    return _lado_por_fraccion(f"{coincidencia['escena']}-{numero}")
