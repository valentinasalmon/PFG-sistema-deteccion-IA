"""Capa 4: probabilidad de imagen sintética según la red neuronal (funcionalidad 012).

Ejecuta el clasificador de la funcionalidad 010 con ONNX Runtime en CPU. No
reimplementa nada del modelo: usa ``PredictorOnnx`` de ``clasificador``,
el mismo código que la evaluación del modelo, así el preprocesamiento es
idéntico y la probabilidad coincide con la de su ficha (ADR-0015).

Cómo se lee el resultado (umbrales publicados, ADR-0017):

- la probabilidad está calibrada: 0,8 significa que, en promedio, 8 de cada
  10 imágenes con ese valor eran sintéticas en la validación;
- por debajo de 50 % la capa no aporta indicios (nivel 0), lo que **no**
  significa que la foto sea real;
- desde 50 %, el nivel es la probabilidad en porcentaje, con un máximo de 90
  (el 100 se reserva para una declaración de IA con firma C2PA, RN28), y se
  lee con la escala común: moderados desde 45 %, fuertes desde 70 %.

La conclusión siempre aclara las limitaciones del modelo (RF42 CA2).

Realiza: RF42, RF43 (CA1 a CA3), RNF23 (CA1, CA3, CA5), RNF24 (CA1, CA4);
RN26, RN27, RN29.
"""
import io

import onnxruntime
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

from app.analisis.base import (
    NIVEL_MAXIMO_REGLAS,
    RECOMENDACION,
    SEVERIDAD_FUERTE,
    SEVERIDAD_MODERADO,
    Anomalia,
    CapaAnalisis,
    CapaNoDisponible,
    ResultadoCapa,
    describir_intensidad,
)
from app.integraciones.modelo_red_neuronal import ModeloNoDisponible, obtener_modelo

register_heif_opener()

VERSION_CAPA = "1.0"
# Por debajo de esta probabilidad la capa no aporta indicios (nivel 0).
UMBRAL_CONSIDERACION = 0.5
# Desde esta probabilidad la anomalía es fuerte (coincide con la escala común).
UMBRAL_FUERTE = 0.7

# Desempeño publicado de cada versión (ficha del modelo y capítulo 11 de
# docs/red-neuronal/): se muestra como referencia en la tabla de criterios.
DESEMPENIO_PUBLICADO = {
    "1.0.0": {
        "conocidos": "AUC 0,961 con generadores conocidos",
        "no_vistos": "AUC 0,938 con la familia de Google, que no vio al entrenar",
    },
}

LIMITACIONES = (
    "El modelo mira la imagen completa: no detecta ediciones parciales, como una "
    "abolladura agregada a una foto real; para eso están las otras capas. Su desempeño "
    "puede bajar con generadores que no vio durante el entrenamiento, como las versiones "
    "más nuevas de las herramientas comerciales."
)
ACLARACION_PROBABILIDAD_BAJA = (
    "Una probabilidad baja no indica que la foto sea real: solo que el modelo no "
    "encontró los patrones que dejan los generadores que conoce."
)


def porcentaje(probabilidad):
    """Probabilidad de 0 a 1 como porcentaje entero, para mostrar."""
    return round(100 * probabilidad)


def calcular_nivel_red(probabilidad):
    """Nivel de indicio de la capa 4 a partir de la probabilidad calibrada.

    0 por debajo de 50 %; desde ahí, la probabilidad en porcentaje con un
    máximo de 90 (RF43 CA1; el 100 queda para C2PA, RN28).
    """
    if probabilidad < UMBRAL_CONSIDERACION:
        return 0
    return min(NIVEL_MAXIMO_REGLAS, porcentaje(probabilidad))


def redactar_conclusion(probabilidad, nivel):
    """Conclusión como indicio, con las limitaciones del modelo y la recomendación (RN27)."""
    valor = porcentaje(probabilidad)
    if nivel == 0:
        texto = (
            f"La red neuronal estima una probabilidad de {valor} % de que la imagen haya sido "
            f"generada íntegramente con inteligencia artificial, por debajo del umbral de "
            f"{porcentaje(UMBRAL_CONSIDERACION)} % a partir del cual esta capa aporta indicios. "
            f"{ACLARACION_PROBABILIDAD_BAJA}"
        )
    else:
        texto = (
            f"La red neuronal estima una probabilidad de {valor} % de que la imagen haya sido "
            f"generada íntegramente con inteligencia artificial, lo que constituye "
            f"{describir_intensidad(nivel)} en esta capa."
        )
    return f"{texto} {LIMITACIONES} {RECOMENDACION}"


def armar_tabla(probabilidad, modelo):
    """Criterios con sus umbrales y el valor obtenido, sin describir la red (RNF23 CA5)."""
    tabla = [
        {"campo": "Probabilidad estimada de imagen generada con IA",
         "valor": f"{porcentaje(probabilidad)} %"},
        {"campo": "Umbral a partir del cual la capa aporta indicios",
         "valor": f"{porcentaje(UMBRAL_CONSIDERACION)} %"},
        {"campo": "Escala de lectura",
         "valor": "indicios moderados desde 45 %, fuertes desde 70 %"},
        {"campo": "Versión del modelo", "valor": modelo.version},
    ]
    desempenio = DESEMPENIO_PUBLICADO.get(modelo.version)
    if desempenio:
        tabla.append({"campo": "Desempeño publicado del modelo",
                      "valor": f"{desempenio['conocidos']}; {desempenio['no_vistos']}"})
    return tabla


class CapaRedNeuronal(CapaAnalisis):
    """Estima la probabilidad de que la imagen haya sido generada íntegramente con IA."""

    nombre = "red_neuronal"
    titulo = "Red neuronal"
    que_significa = (
        "Un modelo entrenado con miles de fotos reales y generadas estima la probabilidad de "
        "que la imagen completa haya sido creada con inteligencia artificial. No detecta "
        "ediciones parciales y puede fallar con generadores que no conoce; una probabilidad "
        "baja no significa que la foto sea real."
    )
    tipo_de_resultado = "probabilistico"

    def __init__(self, configuracion):
        self.configuracion = configuracion

    def version(self):
        """Versión de la capa, del modelo configurado y de ONNX Runtime (RN29).

        No carga el modelo: el proceso web también la consulta al crear el análisis.
        """
        version_modelo = self.configuracion.get("MODELO_RED_NEURONAL_VERSION") or "sin configurar"
        return (
            f"{VERSION_CAPA} (modelo {version_modelo}, ONNX Runtime {onnxruntime.__version__})"
        )

    def analizar(self, contenido, contexto):
        """Probabilidad del clasificador, nivel, anomalía y conclusión (RF42, RF43).

        Raises:
            CapaNoDisponible: si el modelo no está disponible o la imagen no se puede leer.
        """
        try:
            modelo = obtener_modelo(self.configuracion)
        except ModeloNoDisponible as error:
            raise CapaNoDisponible(str(error)) from error
        try:
            with Image.open(io.BytesIO(contenido)) as imagen:
                probabilidad = modelo.predictor.predecir(imagen).probabilidad_sintetica
        except (UnidentifiedImageError, OSError, ValueError) as error:
            raise CapaNoDisponible(
                "No se pudo leer la imagen para la red neuronal."
            ) from error
        nivel = calcular_nivel_red(probabilidad)
        anomalias = []
        if nivel:
            anomalias.append(Anomalia(
                "Probabilidad de imagen generada con IA", f"{porcentaje(probabilidad)} %",
                f"La red neuronal estima una probabilidad de {porcentaje(probabilidad)} % de "
                "que la imagen haya sido generada íntegramente con inteligencia artificial.",
                SEVERIDAD_FUERTE if probabilidad >= UMBRAL_FUERTE else SEVERIDAD_MODERADO,
            ))
        metadatos = modelo.metadatos
        return ResultadoCapa(
            nivel=nivel,
            anomalias=anomalias,
            conclusion=redactar_conclusion(probabilidad, nivel),
            detalle={
                "tabla": armar_tabla(probabilidad, modelo),
                "probabilidad": round(probabilidad, 4),
                "modelo": {
                    "version": modelo.version,
                    "huella": modelo.huella,
                    "huella_manifiesto": metadatos.huella_manifiesto,
                    "commit": metadatos.commit,
                    "onnxruntime": onnxruntime.__version__,
                },
            },
        )
