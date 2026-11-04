"""Preparación de datos: normalización anti-atajos y partición con semilla.

Normalización (CA5): las imágenes reales y las sintéticas llegan con
formatos y tamaños distintos (por ejemplo, PNG generados frente a JPEG de
cámara). Si se dejaran así, el modelo podría aprender a distinguir el
formato en lugar de las huellas de la generación. Por eso todas pasan por el
mismo proceso: RGB, lado menor llevado a un valor aleatorio dentro de un
rango y JPEG con calidad aleatoria dentro de otro. Ambas clases quedan con
la misma distribución de formato, tamaño y compresión.

Partición (CA6): estratificada por clase y generador, con semilla fija, y
con los generadores reservados apartados en la partición ``no_visto``.

Los valores aleatorios de cada imagen dependen de la semilla y de la huella
de la imagen, no del orden de procesamiento: el resultado es el mismo
aunque se procese en paralelo o en otro orden (CA7).

Realiza: CA5, CA6 y CA7 de la funcionalidad 010.
"""

from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image

from clasificador.configuracion import ConfiguracionDatos, ConfiguracionProporciones
from clasificador.datos.manifiesto import RegistroImagen, huella_archivo
from clasificador.inferencia.preprocesamiento import convertir_a_rgb


def _generador_aleatorio(semilla: int, clave: str) -> np.random.Generator:
    """Generador reproducible propio de cada imagen (semilla + huella)."""
    return np.random.default_rng([semilla, int(clave[:15], 16)])


def normalizar_imagen(
    origen: Path,
    destino: Path,
    lado_menor: int,
    calidad_jpeg: int,
) -> None:
    """Convierte una imagen a RGB, la redimensiona y la guarda como JPEG.

    La conversión a RGB es la misma que usa la inferencia (ADR-0015): la
    transparencia se compone sobre fondo blanco.
    """
    with Image.open(origen) as abierta:
        imagen = convertir_a_rgb(abierta)
        ancho, alto = imagen.size
        escala = lado_menor / min(ancho, alto)
        nuevo_tamanio = (max(1, round(ancho * escala)), max(1, round(alto * escala)))
        imagen = imagen.resize(nuevo_tamanio, Image.Resampling.LANCZOS)
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagen.save(destino, format="JPEG", quality=calidad_jpeg)


def normalizar_conjunto(
    registros: list[RegistroImagen],
    raiz_origen: Path,
    raiz_destino: Path,
    configuracion: ConfiguracionDatos,
    semilla: int,
) -> list[RegistroImagen]:
    """Normaliza todas las imágenes y devuelve los registros actualizados.

    Las imágenes normalizadas se guardan en ``raiz_destino`` con un nombre
    derivado de su huella original; la huella del registro pasa a ser la de
    la imagen normalizada, que es la que se usa para entrenar.
    """
    normalizados = []
    for registro in registros:
        aleatorio = _generador_aleatorio(semilla, registro.huella_sha256)
        lado = int(aleatorio.integers(configuracion.lado_menor[0], configuracion.lado_menor[1] + 1))
        calidad = int(
            aleatorio.integers(configuracion.calidad_jpeg[0], configuracion.calidad_jpeg[1] + 1)
        )
        nombre_clase = "sintetica" if registro.clase else "real"
        ruta_relativa = (
            f"{nombre_clase}/{registro.generador}/{registro.huella_sha256[:20]}"
            f"_{registro.variante}.jpg"
        )
        destino = Path(raiz_destino) / ruta_relativa
        normalizar_imagen(Path(raiz_origen) / registro.ruta_relativa, destino, lado, calidad)
        normalizados.append(
            replace(registro, ruta_relativa=ruta_relativa, huella_sha256=huella_archivo(destino))
        )
    return normalizados


def _repartir_grupo(
    grupo: list[RegistroImagen],
    proporciones: ConfiguracionProporciones,
    aleatorio: np.random.Generator,
) -> list[RegistroImagen]:
    """Reparte un grupo (clase, generador) entre las tres particiones."""
    # Orden por huella antes de mezclar: no depende del orden de llegada.
    grupo = sorted(grupo, key=lambda registro: registro.huella_sha256)
    corte_entrenamiento = round(len(grupo) * proporciones.entrenamiento)
    corte_validacion = corte_entrenamiento + round(len(grupo) * proporciones.validacion)
    repartidos = []
    for posicion, indice in enumerate(aleatorio.permutation(len(grupo))):
        if posicion < corte_entrenamiento:
            particion = "entrenamiento"
        elif posicion < corte_validacion:
            particion = "validacion"
        else:
            particion = "prueba"
        repartidos.append(replace(grupo[indice], particion=particion))
    return repartidos


def particionar(
    registros: list[RegistroImagen],
    proporciones: ConfiguracionProporciones,
    generadores_reservados: list[str],
    semilla: int,
) -> list[RegistroImagen]:
    """Asigna cada imagen a una partición de forma estratificada y reproducible.

    Cada grupo (clase, generador) se reparte con las mismas proporciones,
    para que todos los generadores estén representados en validación y
    prueba. Los generadores reservados van completos a ``no_visto``.
    """
    reservados = set(generadores_reservados)
    grupos: dict[tuple[int, str], list[RegistroImagen]] = defaultdict(list)
    resultado = []
    for registro in registros:
        if registro.generador in reservados:
            resultado.append(replace(registro, particion="no_visto"))
        else:
            grupos[(registro.clase, registro.generador)].append(registro)

    aleatorio = np.random.default_rng(semilla)
    for clave in sorted(grupos):
        resultado += _repartir_grupo(grupos[clave], proporciones, aleatorio)
    return resultado


def preparar(
    registros: list[RegistroImagen],
    raiz_origen: Path,
    raiz_destino: Path,
    configuracion: ConfiguracionDatos,
    semilla: int,
) -> list[RegistroImagen]:
    """Etapa ``preparar``: normaliza y particiona el conjunto completo."""
    normalizados = normalizar_conjunto(registros, raiz_origen, raiz_destino, configuracion, semilla)
    return particionar(
        normalizados, configuracion.proporciones, configuracion.generadores_reservados, semilla
    )
