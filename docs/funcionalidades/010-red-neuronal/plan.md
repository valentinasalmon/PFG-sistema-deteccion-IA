# Plan técnico: 010 — Red neuronal: ciclo de vida, entrenamiento y exportación

Referencia: [especificacion.md](especificacion.md) · Guía conceptual: [ciclo de vida de la red neuronal](../../guias/ciclo-de-vida-red-neuronal.md) · Decisiones: [ADR-0014](../../arquitectura/decisiones/0014-ciclo-de-vida-y-mlops-del-clasificador.md), [ADR-0015](../../arquitectura/decisiones/0015-arquitectura-y-contrato-de-inferencia-del-clasificador.md).

## Resumen de la solución

El clasificador se construye como un **paquete de Python** (`red_neuronal/clasificador/`) con un módulo por etapa del ciclo de vida: obtención, validación y preparación de datos, entrenamiento, evaluación, exportación, compuerta y publicación. Cada etapa es una función pura con entradas y salidas en disco, invocable por línea de comandos (`python -m clasificador <etapa> --configuracion <archivo.yaml>`). Los cuadernos de Kaggle **no contienen lógica**: clonan el repositorio en un commit concreto, instalan el paquete y llaman a las etapas. Así todo el código se revisa, se prueba en la integración continua sin GPU y se reutiliza.

El modelo es una red convolucional **EfficientNet-B0** preentrenada en ImageNet, ajustada por transferencia de aprendizaje como clasificador binario (real / sintética). Se entrena con aumentaciones que simulan la recompresión por mensajería y se **calibra** con *temperature scaling* para que la salida pueda leerse como una probabilidad. Se exporta a ONNX con la calibración y la sigmoide incluidas en el grafo, de modo que el backend recibe directamente la probabilidad.

El preprocesamiento de inferencia (recortes, normalización y promedio) vive en un subpaquete **sin dependencias de PyTorch** (`clasificador.inferencia`), que usan tanto la evaluación como el backend de la funcionalidad 012. Hay **una sola implementación** del contrato de entrada del modelo, y esa coincidencia se prueba automáticamente. Las herramientas de MLOps son: Kaggle Datasets privados para las versiones de datos, MLflow para el seguimiento de experimentos y un repositorio privado de Hugging Face Hub como registro de modelos (ver ADR-0014).

## Capas afectadas

La arquitectura en capas de la constitución rige el backend. `red_neuronal/` es un componente independiente del monorepositorio y se organiza por **etapas del pipeline**, con la misma regla de dependencias: los módulos de etapa dependen de las interfaces, nunca de una implementación concreta de un servicio externo.

| Componente | Archivos nuevos o modificados | Responsabilidad |
|---|---|---|
| Raíz | `.gitignore` (nuevo) | Ignorar `red_neuronal/datos/`, `red_neuronal/modelos/`, `backend/modelos_onnx/`, `mlruns/`, `.env`, entornos virtuales y cachés. **Hoy el repositorio no tiene `.gitignore`.** |
| Paquete | `red_neuronal/pyproject.toml` | Metadatos, dependencias base (inferencia) y extra `[entrenamiento]`; configuración de flake8, pylint, pytest y cobertura. |
| Configuración | `clasificador/configuracion.py`, `red_neuronal/configuracion/*.yaml` | Esquema validado (pydantic) de la configuración de cada ejecución: fuentes, cantidades, semilla, hiperparámetros, rutas y umbrales. |
| Datos | `clasificador/datos/fuentes.py` | Interfaz `FuenteDatos` y una implementación por conjunto público (Community Forensics, OpenFake, MS COCOAI, ShareGPT-4o-Image) y por el conjunto propio (carpeta local). |
| Datos | `clasificador/datos/manifiesto.py` | Entidad `RegistroImagen`, lectura y escritura del manifiesto y cálculo de su huella. |
| Datos | `clasificador/datos/validacion.py` | Verificaciones: imágenes corruptas, duplicados exactos (SHA-256), solapamiento entre particiones y balance de clases. |
| Datos | `clasificador/datos/preparacion.py` | Normalización anti-atajos (todo a JPEG con calidad aleatoria acotada, misma distribución de tamaños para ambas clases) y partición con semilla, incluido el generador reservado como no visto. |
| Datos | `clasificador/datos/conjunto.py`, `aumentacion.py` | `Dataset` de PyTorch a partir del manifiesto y aumentaciones de entrenamiento (recompresión JPEG, reescalado, recorte, volteo). |
| Modelo | `clasificador/modelo/arquitecturas.py` | Fábrica `crear_modelo(nombre, preentrenado)` sobre timm, y envoltorio exportable con temperatura y sigmoide. |
| Entrenamiento | `clasificador/entrenamiento/entrenador.py` | Bucle de entrenamiento con precisión mixta, parada temprana por AUC de validación y guardado del mejor punto de control. |
| Entrenamiento | `clasificador/entrenamiento/calibracion.py` | Ajuste de la temperatura sobre la partición de validación. |
| Evaluación | `clasificador/evaluacion/metricas.py` | Exactitud, precisión, exhaustividad, F1, AUC, curva ROC, matriz de confusión y error de calibración (ECE), en total y por grupo (generador, versión de recompresión). |
| Evaluación | `clasificador/evaluacion/evaluador.py` | Ejecuta el modelo ONNX sobre un manifiesto con el preprocesamiento de inferencia y produce el informe de métricas. |
| Exportación | `clasificador/exportacion/onnx.py` | Exportación a ONNX con metadatos, verificación de coincidencia con PyTorch (≤ 0,001) y medición de la latencia en CPU. |
| Inferencia | `clasificador/inferencia/preprocesamiento.py`, `predictor.py` | Contrato de entrada del modelo y `PredictorOnnx`. Solo depende de numpy, Pillow y onnxruntime. Lo reutiliza el backend en la funcionalidad 012. |
| Seguimiento | `clasificador/seguimiento/experimentos.py` | Interfaz `RegistradorExperimentos`; implementaciones `RegistradorMlflow` y `RegistradorNulo` (pruebas). |
| Registro | `clasificador/registro/registro_modelos.py` | Interfaz `RegistroModelos`; implementaciones `RegistroHuggingFace` y `RegistroLocal` (pruebas). |
| Registro | `clasificador/registro/compuerta.py` | Compuerta de promoción: umbral de AUC, coincidencia ONNX, ficha completa, huella del manifiesto y árbol de Git limpio. |
| Registro | `clasificador/registro/ficha.py`, `plantillas/ficha_modelo.md.j2` | Generación de la ficha del modelo a partir de las métricas y la configuración. |
| CLI | `clasificador/__main__.py` | Subcomandos `obtener`, `validar`, `preparar`, `entrenar`, `evaluar`, `exportar`, `publicar`. |
| Cuadernos | `red_neuronal/cuadernos/00_prueba_de_concepto.ipynb`, `01_exploracion_datos.ipynb`, `02_entrenamiento.ipynb`, `03_evaluacion_conjunto_propio.ipynb` | Orquestación en Kaggle y visualización. Sin lógica propia. |
| Pruebas | `red_neuronal/pruebas/` | Pruebas unitarias y de integración del pipeline con imágenes generadas en memoria. |
| Integración continua | `.github/workflows/red_neuronal.yml` | flake8, pylint, pytest y cobertura en cada cambio de `red_neuronal/`. |
| Documentación | `red_neuronal/informes/<version>/ficha.md`, `docs/arquitectura/estructura-del-repositorio.md`, `CLAUDE.md` | Fichas por versión; estructura y comandos de calidad actualizados. |

La carpeta `red_neuronal/scripts/` prevista en la estructura se reemplaza por el paquete `clasificador/` y su línea de comandos.

## Patrones aplicados

| Patrón | Dónde | Por qué |
|---|---|---|
| **Pipeline** (etapas con entradas y salidas en disco) | `__main__.py` y un módulo por etapa | Cada etapa se ejecuta, se prueba y se repite por separado; si se corta la sesión de Kaggle, se retoma desde la última etapa completa. |
| **Strategy** | `FuenteDatos`, `RegistradorExperimentos`, `RegistroModelos` | Igual que las integraciones del backend: los servicios externos (Hugging Face, MLflow) se reemplazan por simulaciones en las pruebas y pueden cambiarse sin tocar las etapas. |
| **Factory** | `crear_modelo`, `crear_fuente`, `crear_registro` | La configuración elige la implementación por nombre; agregar una arquitectura o una fuente no modifica el código existente. |
| **Configuración externa validada** | `configuracion.py` + YAML | Los hiperparámetros no están en el código (CA8) y un error de configuración falla al inicio, no después de una hora de entrenamiento. |
| **Envoltorio (*Decorator* estructural)** | `ModeloExportable` | Agrega temperatura y sigmoide al modelo sin modificarlo, para exportar un grafo que ya devuelve una probabilidad. |

## Contratos

### Entidades

```python
@dataclass(frozen=True)
class RegistroImagen:
    """Una imagen del manifiesto. Realiza: RNF24 CA2."""
    huella_sha256: str
    ruta_relativa: str        # relativa a la raíz del conjunto preparado
    clase: int                # 0 = real, 1 = sintética
    fuente: str               # "community_forensics", "openfake", "propio", ...
    generador: str            # "real", "gpt-image", "sdxl", "gemini", ...
    particion: str            # "entrenamiento" | "validacion" | "prueba" | "no_visto"
    variante: str             # "original" | "whatsapp" | "captura" | "editada"

@dataclass(frozen=True)
class ResultadoValidacion:
    """Resultado de validar un manifiesto. Realiza: CA4."""
    es_valido: bool
    errores: list[str]
    resumen: dict[str, int]   # conteos por clase, generador y partición

@dataclass(frozen=True)
class Prediccion:
    """Salida del predictor para una imagen. Realiza: RF42 CA1, RN29."""
    probabilidad_sintetica: float   # en [0, 1], calibrada
    version_modelo: str             # "MAJOR.MINOR.PATCH"
```

### Etapas (línea de comandos y funciones)

| Etapa | Función | Entrada | Salida | Falla si |
|---|---|---|---|---|
| `obtener` | `obtener(config) -> Path` | Fuentes y cantidades por generador | Imágenes + `manifiesto_crudo.csv` | Una fuente no está disponible o no alcanza la cantidad pedida |
| `validar` | `validar(manifiesto) -> ResultadoValidacion` | Manifiesto | `validacion.json` | Corruptas, duplicados, solapamiento o desbalance mayor al tolerado (`ErrorValidacionDatos`) |
| `preparar` | `preparar(config, manifiesto) -> Path` | Manifiesto validado | Imágenes normalizadas + `manifiesto.csv` + su huella | — |
| `entrenar` | `entrenar(config, manifiesto) -> Path` | Manifiesto y configuración | `mejor.pt`, temperatura y ejecución registrada | — |
| `evaluar` | `evaluar(modelo_onnx, manifiesto) -> InformeMetricas` | Modelo ONNX y manifiesto de prueba | `metricas.json`, curvas y matrices | — |
| `exportar` | `exportar(punto_control, destino) -> Path` | Punto de control | `modelo.onnx` con metadatos | La diferencia con PyTorch supera 0,001 (`ErrorExportacion`) |
| `publicar` | `publicar(directorio_version, registro) -> str` | Modelo, métricas, ficha y manifiesto | Versión publicada | La compuerta rechaza (`ErrorCompuerta`, con la lista de criterios incumplidos) |

### Contrato de inferencia (compartido con el backend, ver ADR-0015)

```python
class PredictorOnnx:
    """Ejecuta el clasificador en CPU. Realiza: RF42, RNF24 CA1."""
    def __init__(self, ruta_modelo: Path) -> None: ...
    @property
    def version(self) -> str: ...
    def predecir(self, imagen: PIL.Image.Image) -> Prediccion: ...
```

- **Entrada del grafo ONNX**: tensor `float32` de forma `[N, 3, 224, 224]`, RGB, normalizado con media y desvío de ImageNet.
- **Salida del grafo**: tensor `float32` de forma `[N, 1]` con la probabilidad calibrada de cada recorte.
- **Preprocesamiento** (`preprocesamiento.py`): conversión a RGB; reducción solo si el lado mayor supera 1024 px; ampliación solo si el lado menor es menor a 224 px; cinco recortes de 224 × 224 (cuatro esquinas y centro) **sin reescalar** la imagen, para no borrar las huellas de alta frecuencia de la generación.
- **Agregación**: promedio de las cinco probabilidades.
- **Metadatos ONNX** (`metadata_props`): `version`, `arquitectura`, `temperatura`, `tamanio_recorte`, `media`, `desvio`, `huella_manifiesto`, `commit`.

### Versionado del modelo

- `MAJOR`: cambia el contrato de entrada o salida, o la arquitectura.
- `MINOR`: reentrenamiento con datos nuevos.
- `PATCH`: corrección sin datos nuevos, por ejemplo una recalibración.
- Las versiones publicadas son inmutables y no se borran (RN29).

## Cambios en datos

No hay cambios en la base de datos. La persistencia de la funcionalidad 012 (versión del modelo en el resultado de la capa) se define en esa funcionalidad.

Archivos y almacenes:

| Qué | Dónde | Versionado |
|---|---|---|
| Receta de cada conjunto (fuentes, revisión de cada conjunto de Hugging Face, cantidades, semilla) | `red_neuronal/configuracion/datos_vN.yaml` en Git | Git |
| Imágenes preparadas + `manifiesto.csv` | Kaggle Dataset **privado** `pfg-datos-entrenamiento` | Versiones del Kaggle Dataset; su huella queda en la ficha |
| Conjunto propio (CA12, CA13) | Kaggle Dataset **privado** `pfg-conjunto-propio` | Versiones del Kaggle Dataset |
| Ejecuciones de entrenamiento | MLflow (base SQLite `mlruns/mlflow.db` y artefactos en la salida de Kaggle, empaquetados junto con cada versión publicada) | Identificador de ejecución en la ficha |
| Modelos publicados | Repositorio privado de Hugging Face Hub, una etiqueta `vMAJOR.MINOR.PATCH` por versión | Etiquetas de Git del Hub, inmutables |
| Fichas del modelo | `red_neuronal/informes/<version>/ficha.md` en Git | Git |

## Bibliotecas nuevas

Las versiones exactas se fijan en `pyproject.toml` y en un archivo de restricciones al implementar la primera tarea, tomando las disponibles en la imagen de Kaggle para evitar reinstalar PyTorch.

| Biblioteca | Grupo | Para qué se usa |
|---|---|---|
| numpy, Pillow | base | Preprocesamiento de inferencia |
| onnxruntime | base | Inferencia en CPU (RNF24 CA1); la misma que usará el backend |
| torch, torchvision | entrenamiento | Entrenamiento y aumentaciones |
| timm | entrenamiento | EfficientNet-B0 preentrenada con una interfaz única para comparar arquitecturas |
| onnx | entrenamiento | Escritura de metadatos y guardado del modelo en un único archivo |
| onnxscript | entrenamiento | Requerido por el exportador de `torch.export`, el predeterminado desde PyTorch 2.9 (el anterior está obsoleto) |
| scikit-learn | entrenamiento | Métricas, curva ROC y matriz de confusión |
| datasets, huggingface_hub | entrenamiento | Lectura en *streaming* de los conjuntos públicos y registro de modelos |
| mlflow | entrenamiento | Seguimiento de experimentos (CA9), con base SQLite local |
| pydantic, PyYAML | entrenamiento | Configuración validada (CA8) |
| pandas | entrenamiento | Lectura y análisis de manifiestos |
| matplotlib | entrenamiento | Curvas ROC y matrices de confusión para la ficha |
| Jinja2 | entrenamiento | Plantilla de la ficha del modelo (ya prevista en el backend) |
| pytest, pytest-cov, flake8, pylint | desarrollo | Calidad (RNF19) |

## Estrategia de pruebas

**Principio**: la integración continua no tiene GPU ni descarga datos. Las pruebas usan imágenes generadas en memoria (ruido y figuras con Pillow) y un modelo diminuto (`crear_modelo("efficientnet_b0", preentrenado=False)` sobre recortes de 32 px), de modo que la suite completa corra en pocos minutos en CPU.

| Tipo | Qué se prueba |
|---|---|
| Unitarias: datos | El manifiesto se escribe y se lee sin pérdida; su huella es estable. La validación detecta una imagen corrupta, un duplicado, un solapamiento entre particiones y un desbalance. La preparación con la misma semilla produce el mismo manifiesto. El generador reservado nunca aparece en el entrenamiento. Después de normalizar, ambas clases tienen el mismo formato (CA5). |
| Unitarias: inferencia | Recortes en imágenes chicas, grandes, verticales, con transparencia y en escala de grises. La normalización da valores conocidos. La agregación promedia. |
| Unitarias: métricas | Sobre casos construidos a mano, los valores coinciden con el cálculo esperado (AUC = 1 con separación perfecta y 0,5 con predicciones constantes) y la agrupación por generador es correcta. |
| Unitarias: compuerta | Rechaza con AUC menor a 0,90, con diferencia ONNX mayor a 0,001, con ficha incompleta, con huella de manifiesto distinta o con árbol de Git sucio, e informa todos los motivos juntos. |
| Unitarias: configuración | Rechaza archivos con campos faltantes o valores fuera de rango. |
| Integración: pipeline mínimo | `preparar → entrenar (2 pasos) → exportar → evaluar → publicar` sobre 40 imágenes en memoria, con `RegistradorNulo` y `RegistroLocal`: la pérdida baja, el ONNX coincide con PyTorch y la versión queda publicada. |
| Integración: contrato | La misma imagen da la misma probabilidad con `PredictorOnnx` y con el modelo de PyTorch más el preprocesamiento de evaluación (una sola implementación). |
| Manual (Kaggle) | Prueba de concepto (CA1), entrenamiento completo, evaluación del conjunto propio y publicación real en Hugging Face. |

Cobertura mínima: 80 % sobre `clasificador/`. Los cuadernos quedan fuera de la medición porque no tienen lógica.

## Excepciones a la constitución

Ninguna. La organización por etapas de `red_neuronal/` no contradice la arquitectura en capas, que la constitución define para `backend/app/`. Las reglas transversales sí se cumplen: Strategy para los servicios externos, simulaciones en las pruebas, cobertura del 80 %, español y docstrings.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| El modelo aprende atajos (formato, tamaño, temática) en lugar de huellas de generación | Normalización JPEG y de tamaños para ambas clases (CA5); evaluación por generador; revisión de errores en el cuaderno de exploración |
| Algún conjunto requiere aceptar términos o deja de estar disponible | Verificación en `01_exploracion_datos` antes del entrenamiento; las fuentes son intercambiables (Strategy) |
| Cuota de GPU de Kaggle (unas 30 h por semana) | Prueba de concepto para estimar tiempos; puntos de control por época para retomar; recortes de 224 px |
| Diferencias entre la versión de Python o de bibliotecas de Kaggle y la del backend | El paquete de inferencia solo depende de numpy, Pillow y onnxruntime; versión de *opset* fija; integración continua con Python 3.12 (backend) y 3.13 (imagen de Kaggle) |
| Desempeño bajo frente a generadores comerciales no vistos | Se mide y se declara en la ficha (CA11 a CA13); disparador de reentrenamiento (CA18) |
| Fuga de datos personales del conjunto propio | Kaggle Dataset privado; `.gitignore`; nunca se usa en entrenamiento |
| Licencias no comerciales | Registradas en la ficha; reentrenamiento si se comercializa (pregunta abierta de la especificación) |
| Credenciales expuestas | `HF_TOKEN` como secreto de Kaggle y de GitHub; nunca en archivos |
