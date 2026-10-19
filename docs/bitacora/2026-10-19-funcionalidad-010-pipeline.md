# 2026-10-19 — Funcionalidad 010: pipeline del clasificador implementado

## Qué se hizo

1. Se integró `desarrollo` en la rama de la funcionalidad 010. Los ADR de la red neuronal se renumeraron a 0012 y 0013 porque 0010 y 0011 ya existían; se unieron los `.gitignore`.
2. Se implementaron las tareas T01 a T22: el paquete `red_neuronal/clasificador/` con todas las etapas del ciclo de vida (obtener, validar, preparar, entrenar, exportar, evaluar, publicar), su línea de comandos y la integración continua propia (`.github/workflows/red_neuronal.yml`).
3. Se escribió el cuaderno de la prueba de concepto (T23) para ejecutar en Kaggle.
4. Calidad: 176 pruebas, cobertura del 99 %, flake8 sin errores y pylint 10/10. La integración continua corre en Python 3.12 (backend) y 3.13 (versión de Kaggle, detectada al ejecutar el cuaderno).

## Decisiones tomadas

- **MLflow con SQLite local** en lugar del almacén de archivos planos: la versión actual de MLflow dejó este último en modo de mantenimiento y rechaza usarlo por defecto. Sigue siendo un único directorio portable, sin servidor (ADR-0012 actualizado antes de integrarse).
- **Exportador de `torch.export`** (`dynamo=True`), el predeterminado desde PyTorch 2.9; el anterior está obsoleto. Requiere `onnxscript`. Como guarda los pesos en un archivo aparte, el modelo se vuelve a guardar como **un único archivo** para que tenga una sola huella en el registro.
- **Preprocesamiento único**: la conversión a RGB, los recortes y la normalización están en `clasificador.inferencia.preprocesamiento` y los usan la preparación, las aumentaciones, la evaluación y el backend. Una prueba de contrato verifica que ONNX y PyTorch den la misma probabilidad. Por eso la tarea T14 se adelantó a la T10.
- **Desempeño por generador**: cada generador se evalúa con sus imágenes frente a **todas las reales**, porque el AUC necesita las dos clases.
- **Conjunto propio sin normalizar**: se evalúa tal como llega (original, WhatsApp, captura), para medir las condiciones reales.
- **Estructura del conjunto propio**: `<real|sintetica>/<generador>/<variante>/archivo`, con variante `original`, `whatsapp`, `captura` o `editada`.
- **Interfaz en español**: la ayuda y los errores de la línea de comandos se tradujeron (argparse no trae traducción) y la ficha muestra "sí/no" en lugar de valores en inglés.
- **Repositorio privado**: el cuaderno de Kaggle clona el repositorio con un *token* de GitHub de solo lectura guardado como secreto (nueva tarea externa E05).

## Tecnologías, bibliotecas o técnicas incorporadas

| Biblioteca | Para qué |
|---|---|
| PyTorch, torchvision, timm | Entrenamiento por transferencia de aprendizaje (EfficientNet-B0) |
| onnx, onnxscript, onnxruntime | Exportación a ONNX e inferencia en CPU |
| scikit-learn | Métricas, curva ROC y matriz de confusión |
| MLflow | Seguimiento de experimentos |
| datasets, huggingface_hub | Lectura en *streaming* de conjuntos públicos y registro de modelos |
| pydantic, PyYAML | Configuración validada |
| Jinja2 | Ficha del modelo |

Técnicas: *temperature scaling* para calibrar la probabilidad, error de calibración esperado (ECE), cinco recortes sin reescalar, aumentaciones de recompresión JPEG y reducción de tamaño, partición estratificada por generador, parada temprana y puntos de control reanudables.

## Problemas encontrados y cómo se resolvieron

- Desde el entorno del asistente no se puede acceder a Hugging Face: los nombres de columnas de cada conjunto se dejan en la configuración y se confirman en Kaggle (sección 4 del cuaderno y tarea T25).
- En la prueba de integración, con grupos chicos, el redondeo de la partición desbalancea las clases y el modelo diminuto no siempre alcanza AUC 0,90: la prueba usa tolerancias propias, porque verifica que las etapas se conecten y no la calidad del modelo, que se mide en Kaggle.

- **Token expuesto en la primera ejecución en Kaggle**: el cuaderno ponía el *token* de GitHub dentro de la URL de `git clone`; al fallar el clon (el *token* no tenía acceso al repositorio), Python imprimió el comando completo con el *token*. Se revocó el *token* y se corrigió el cuaderno: ahora el *token* viaja en una variable de entorno de configuración de git (cabecera de autorización), nunca en la URL, y los errores se muestran sin él. Lección: ninguna credencial va en argumentos de comandos.
- En Kaggle, la primera ejecución falló por tener internet desactivado (error de resolución de nombres al leer los secretos).

## Pendientes

- E03, E04 y E05 (autora): repositorio privado de modelos en Hugging Face, conjunto propio y *token* de GitHub en Kaggle.
- T24: ejecutar la prueba de concepto en Kaggle y registrar tiempos y métricas.
- T25 en adelante: exploración de datos, receta v1, entrenamiento completo, evaluación en condiciones reales y publicación de la versión 1.0.0.
