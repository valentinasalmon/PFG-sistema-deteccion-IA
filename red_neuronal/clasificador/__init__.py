"""Clasificador de imágenes sintéticas para la capa 4 del análisis.

Paquete que implementa el ciclo de vida completo del modelo: obtención,
validación y preparación de datos, entrenamiento, calibración, evaluación,
exportación a ONNX, compuerta de promoción, registro e inferencia.

El subpaquete ``clasificador.inferencia`` no depende de PyTorch y es el
que reutiliza el backend; el resto requiere el extra ``[entrenamiento]``.

Realiza: RNF24, RF42 (preparación). Ver ADR-0010 y ADR-0011.
"""

# Versión del código del paquete. No confundir con la versión de un modelo
# publicado, que se numera aparte (MAJOR.MINOR.PATCH, ver plan técnico).
__version__ = "0.1.0"
