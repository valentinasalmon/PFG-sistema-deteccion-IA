# 9. MLOps: CI, CT y CD

## Por qué un modelo necesita MLOps

En el software común, el comportamiento depende solo del **código**. En un modelo depende de tres cosas, y si cambia cualquiera, cambia el modelo:

| Elemento | Qué es | Cómo se versiona en evidentIA |
|---|---|---|
| **Código** | Preparación, arquitectura, entrenamiento, evaluación | Git, con el commit registrado en cada modelo |
| **Datos** | Las imágenes con que aprende y se evalúa | Receta YAML en Git + manifiesto con la huella de cada imagen |
| **Modelo** | Los pesos resultantes | Registro de modelos con versión inmutable, huella y ficha |

MLOps es aplicar ingeniería de software a esos tres elementos para poder **reproducir cualquier resultado**. En evidentIA no es opcional: un informe pericial debe poder explicar con qué modelo, datos y código se obtuvo cada indicio (RN29).

## CI, CT y CD

| Práctica | Qué automatiza | Cuándo | En evidentIA |
|---|---|---|---|
| **CI** · Integración continua | Análisis estático y pruebas del código del pipeline, sin GPU ni datos reales | En cada cambio de `red_neuronal/` que se sube a GitHub | Flujo `.github/workflows/red_neuronal.yml` |
| **CT** · Entrenamiento continuo | Volver a entrenar cuando cambian los datos o el código | A pedido, cuando la vigilancia lo indica | El cuaderno de Colab |
| **CD** · Entrega continua del modelo | Exportar, verificar la compuerta y publicar la versión | Al terminar un entrenamiento | Etapas `exportar`, `evaluar` y `publicar` |

### CI: qué se prueba sin GPU

El flujo de GitHub Actions corre en **Python 3.12** (la versión del backend) y **3.13** (la de Colab), con PyTorch para CPU:

1. `flake8` sobre el código y las pruebas;
2. `pylint` sobre el código;
3. `pytest` con **cobertura mínima del 80 %**.

Las 177 pruebas verifican que **el código hace lo que debe**, con imágenes generadas en memoria:

| Tipo | Qué verifica |
|---|---|
| Datos | El manifiesto se escribe y se lee sin pérdida y su huella es estable; la validación detecta una imagen corrupta, un duplicado, una fuga entre particiones y un desbalance; la preparación con la misma semilla da el mismo manifiesto |
| Entrenamiento | Unos pasos sobre un lote diminuto bajan la pérdida; los puntos de control permiten reanudar; la calibración baja el ECE |
| Inferencia | Recortes en imágenes chicas, grandes, verticales, con transparencia y en escala de grises; la normalización da valores conocidos; el promedio es correcto |
| Métricas | Con casos armados a mano, AUC = 1 con separación perfecta y 0,5 con predicciones constantes; la agrupación por generador es correcta |
| Exportación | El ONNX coincide con PyTorch y lleva sus metadatos |
| Compuerta | Rechaza cada incumplimiento e informa todos los motivos juntos |
| Integración | Pipeline mínimo completo (`preparar → entrenar → exportar → evaluar → publicar`) con 40 imágenes; la misma imagen da la misma probabilidad con PyTorch y con ONNX |

Así un error en el pipeline se detecta **en minutos, en GitHub**, y no después de horas de entrenamiento.

### CT y CD: el cuaderno

El entrenamiento real ocurre en Colab, porque necesita GPU. El cuaderno **no tiene lógica propia**: clona el repositorio en una rama o commit concreto, instala el paquete y llama a las siete etapas. Lo que se ejecuta es siempre código probado por la CI. El detalle de cómo correrlo está en el capítulo 10.

## Seguimiento de experimentos (MLflow)

Cada ejecución de `entrenar` queda registrada en **MLflow**, con una base SQLite local (sin servidor):

- **parámetros:** toda la configuración, la huella del manifiesto, el commit y el entorno (versiones de Python, PyTorch y la GPU);
- **métricas por época:** pérdida de entrenamiento y AUC de validación;
- **métricas finales:** ECE antes y después de calibrar;
- **artefactos:** `resultado.json`.

Se empaqueta con cada versión publicada (`mlruns.zip`). Para comparar ejecuciones en una computadora: `mlflow ui --backend-store-uri sqlite:///<carpeta>/mlflow.db`. El identificador de la ejecución queda en la ficha (sección 8).

## Las herramientas y por qué (ADR-0014)

| Necesidad | Herramienta | Por qué |
|---|---|---|
| Entrenar con GPU | Google Colab (Pro) | La autora ya lo tiene; GPU T4, L4 o A100; respaldo en Drive |
| Datos públicos | Hugging Face Datasets en *streaming* | Sin bajar conjuntos enteros de cientos de GB |
| Versionar datos | Receta YAML en Git + manifiesto con huellas | Liviano y suficiente para este volumen; sin herramientas extra |
| Experimentos | MLflow con SQLite | Estándar de la industria, sin servidor que mantener |
| Registro de modelos | Hugging Face Hub privado | Etiquetas inmutables por versión, gratis y accesible desde el servidor |
| Ejecutar en producción | ONNX Runtime | Liviano, rápido en CPU, sin PyTorch |
| CI | GitHub Actions | La misma que usa el resto del sistema |

## Nivel de madurez

| Nivel | Descripción | ¿Aplica? |
|---|---|---|
| 0 · Manual | Cuadernos ejecutados a mano, modelos copiados a mano, sin trazabilidad | Es lo que se evita |
| **1 · Pipeline automatizado** | Pipeline por etapas, datos y modelos versionados, experimentos registrados, compuerta automática, reentrenamiento a pedido | **Objetivo del proyecto** |
| 2 · CI/CD del pipeline completo | Reentrenamiento disparado solo por datos nuevos y monitoreo en producción | Fuera de alcance: no hay datos de producción reutilizables (RNF08) |
