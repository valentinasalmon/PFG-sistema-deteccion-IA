# Tareas: 010 — Red neuronal: ciclo de vida, entrenamiento y exportación

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md) · [guía del ciclo de vida](../../guias/ciclo-de-vida-red-neuronal.md)

Orden: base del paquete → configuración → datos → modelo y entrenamiento → exportación e inferencia (T14 se adelantó a T10, porque el `Dataset` reutiliza el preprocesamiento de inferencia) → evaluación → seguimiento y registro → línea de comandos → **prueba de concepto en Kaggle** → datos reales → entrenamiento completo → evaluación en condiciones reales → publicación → documentación.

Cada tarea de código incluye **sus propias pruebas**: no se pasa a la siguiente con pruebas en rojo. Las tareas marcadas **(externa)** las hace la autora fuera del repositorio y pueden avanzar en paralelo desde el principio.

Todos los comandos de verificación se ejecutan desde `red_neuronal/` con el entorno virtual activado, salvo que se indique otra cosa.

## Fase A — Tareas externas (en paralelo desde el inicio)

- [x] **E01 (externa)** — Crear la cuenta de Kaggle y verificar el teléfono (requisito para usar la GPU).
  - Verificación: en un cuaderno nuevo, *Settings → Accelerator* ofrece "GPU T4 x2".
- [x] **E02 (externa)** — Crear la cuenta de Hugging Face, generar un *token* de escritura y cargarlo como secreto `HF_TOKEN` en Kaggle (*Add-ons → Secrets*). Aceptar los términos de uso de los conjuntos que lo pidan (se listan en T27).
- [ ] **E05 (externa)** — Como el repositorio es privado, crear en GitHub un *token* de grano fino **de solo lectura** (*Settings → Developer settings → Fine-grained tokens*, permiso *Contents: Read-only*, solo para este repositorio) y cargarlo en Kaggle como secreto `GITHUB_TOKEN`.
  - Verificación: la sección 3 del cuaderno de prueba de concepto clona el repositorio sin error.
  - Verificación: en Kaggle, `from kaggle_secrets import UserSecretsClient; UserSecretsClient().get_secret("HF_TOKEN")` devuelve el *token* sin error. **Nunca imprimirlo.**
- [ ] **E03 (externa)** — Crear en Hugging Face el repositorio de modelos **privado** `pfg-clasificador-sintetico`.
  - Verificación: el repositorio aparece como *Private* en el perfil.
- [ ] **E04 (externa)** — Armar el conjunto propio siguiendo el protocolo de T26: imágenes de ChatGPT, Gemini y Copilot, fotos reales propias, fotos editadas con IA, y sus versiones por WhatsApp y captura. Guardarlo **fuera del repositorio**.
  - Verificación: la planilla de control del protocolo está completa.

## Fase B — Base del paquete

- [x] **T01** — Crear el `.gitignore` de la raíz: datos, modelos, `backend/modelos_onnx/`, `mlruns/`, `.env`, entornos virtuales, cachés de Python y de Node, y archivos de Jupyter temporales.
  - Archivos: `.gitignore`
  - Verificación: crear `red_neuronal/datos/prueba.jpg` y `red_neuronal/modelos/prueba.onnx`; `git status` no los muestra. Borrarlos.
  - Commit: `tarea(repositorio): agregar gitignore`
- [x] **T02** — Crear el paquete instalable: `pyproject.toml` con dependencias base (numpy, Pillow, onnxruntime), extra `[entrenamiento]` y extra `[desarrollo]`, configuración de flake8 (vía `setup.cfg` o `.flake8`), pylint, pytest y cobertura; `clasificador/__init__.py` con la versión del paquete; eliminar los `.gitkeep` reemplazados.
  - Archivos: `red_neuronal/pyproject.toml`, `red_neuronal/.flake8`, `red_neuronal/clasificador/__init__.py`, `red_neuronal/pruebas/__init__.py`, `red_neuronal/pruebas/conftest.py`
  - Verificación: `python -m venv .venv && source .venv/bin/activate && pip install -e ".[entrenamiento,desarrollo]"` termina sin errores y `python -c "import clasificador; print(clasificador.__version__)"` imprime la versión.
  - Commit: `construccion(clasificador): crear paquete instalable`
- [x] **T03** — Crear los generadores de datos de prueba en `conftest.py`: *fixtures* que crean en una carpeta temporal imágenes reales y sintéticas simuladas (ruido y figuras con Pillow), en varios formatos y tamaños, y un manifiesto mínimo.
  - Archivos: `red_neuronal/pruebas/conftest.py`
  - Verificación: `pytest` ejecuta una prueba trivial que usa las *fixtures*.
  - Commit: `pruebas(clasificador): agregar fixtures de imagenes sinteticas`
- [x] **T04** — Integración continua: el *workflow* ejecuta flake8, pylint y pytest con cobertura ≥ 80 % sobre Python 3.12 (backend) y 3.13 (Kaggle), solo cuando cambian `red_neuronal/` o el propio *workflow*. PyTorch se instala en su versión para CPU.
  - Archivos: `.github/workflows/red_neuronal.yml`
  - Verificación: subir la rama; la pestaña *Actions* de GitHub muestra el *workflow* en verde.
  - Commit: `integracion(clasificador): agregar workflow de calidad`

## Fase C — Configuración

- [x] **T05** — Esquema de configuración con pydantic: secciones `datos` (fuentes, cantidades por generador, generadores reservados, semilla), `entrenamiento` (arquitectura, épocas, tamaño de lote, tasa de aprendizaje, paciencia), `exportacion` (*opset*, tolerancia) y `compuerta` (AUC mínimo). Función `cargar_configuracion(ruta)`.
  - Archivos: `clasificador/configuracion.py`, `red_neuronal/configuracion/prueba_de_concepto.yaml`, `pruebas/test_configuracion.py`
  - Verificación: las pruebas cubren un archivo válido, un campo faltante y un valor fuera de rango.
  - Commit: `funcionalidad(clasificador): agregar configuracion validada`

## Fase D — Datos

- [x] **T06** — Manifiesto: `RegistroImagen`, `escribir_manifiesto`, `leer_manifiesto` y `huella_manifiesto` (SHA-256 del contenido ordenado).
  - Archivos: `clasificador/datos/__init__.py`, `clasificador/datos/manifiesto.py`, `pruebas/datos/test_manifiesto.py`
  - Verificación: ida y vuelta sin pérdida; la huella no cambia al reordenar filas y sí cambia al modificar una.
  - Commit: `funcionalidad(clasificador): agregar manifiesto de imagenes`
- [x] **T07** — Validación de datos: corruptas, duplicados por huella, solapamiento entre particiones, generadores reservados presentes en el entrenamiento y desbalance mayor al tolerado. Devuelve `ResultadoValidacion` con todos los errores juntos.
  - Archivos: `clasificador/datos/validacion.py`, `pruebas/datos/test_validacion.py`
  - Verificación: una prueba por cada tipo de error y una con un manifiesto válido.
  - Commit: `funcionalidad(clasificador): agregar validacion de datos`
- [x] **T08** — Preparación: normalización anti-atajos (todas las imágenes a RGB y JPEG con calidad aleatoria acotada y semilla; misma distribución de tamaños para ambas clases) y partición estratificada por generador con semilla.
  - Archivos: `clasificador/datos/preparacion.py`, `pruebas/datos/test_preparacion.py`
  - Verificación: misma semilla, mismo manifiesto; después de preparar, ambas clases tienen formato JPEG y rangos de tamaño equivalentes; los generadores reservados quedan en la partición `no_visto`.
  - Commit: `funcionalidad(clasificador): agregar preparacion y particion de datos`
- [x] **T09** — Fuentes de datos: interfaz `FuenteDatos`, fábrica `crear_fuente`, implementación `FuenteCarpetaLocal` (conjunto propio y pruebas) e implementación `FuenteHuggingFace` genérica parametrizada por conjunto, revisión, columnas de imagen, clase y generador. Etapa `obtener` que toma la cantidad pedida por generador y escribe el manifiesto crudo.
  - Archivos: `clasificador/datos/fuentes.py`, `clasificador/datos/obtencion.py`, `pruebas/datos/test_fuentes.py`
  - Verificación: `FuenteCarpetaLocal` sobre las *fixtures*; `FuenteHuggingFace` probada con un conjunto simulado en memoria (sin red).
  - Commit: `funcionalidad(clasificador): agregar fuentes de datos`
- [x] **T10** — `Dataset` de PyTorch y aumentaciones de entrenamiento: recompresión JPEG aleatoria, reescalado aleatorio, recorte aleatorio de 224 px y volteo horizontal. La partición de evaluación usa el preprocesamiento de inferencia de T14 (se completa entonces).
  - Archivos: `clasificador/datos/conjunto.py`, `clasificador/datos/aumentacion.py`, `pruebas/datos/test_conjunto.py`
  - Verificación: el `Dataset` devuelve tensores `[3, 224, 224]` y la clase correcta; las aumentaciones con semilla son reproducibles.
  - Commit: `funcionalidad(clasificador): agregar dataset y aumentaciones`

## Fase E — Modelo y entrenamiento

- [x] **T11** — Fábrica de modelos sobre timm (`crear_modelo(nombre, preentrenado)`) con salida de un *logit*, y `ModeloExportable` (temperatura + sigmoide).
  - Archivos: `clasificador/modelo/__init__.py`, `clasificador/modelo/arquitecturas.py`, `pruebas/modelo/test_arquitecturas.py`
  - Verificación: forma de salida `[N, 1]`; `ModeloExportable` devuelve valores en [0, 1]; un nombre desconocido lanza un error claro.
  - Commit: `funcionalidad(clasificador): agregar fabrica de modelos`
- [x] **T12** — Entrenador: bucle con precisión mixta (solo con GPU), AUC de validación por época, parada temprana, guardado del mejor punto de control y reanudación desde un punto de control. Recibe un `RegistradorExperimentos` (T17), por ahora usado como `RegistradorNulo`.
  - Archivos: `clasificador/entrenamiento/__init__.py`, `clasificador/entrenamiento/entrenador.py`, `pruebas/entrenamiento/test_entrenador.py`
  - Verificación: con el modelo sin preentrenar y 40 imágenes, dos pasos reducen la pérdida; la reanudación continúa desde la época guardada.
  - Commit: `funcionalidad(clasificador): agregar entrenador`
- [x] **T13** — Calibración por *temperature scaling* sobre la partición de validación y cálculo del error de calibración esperado (ECE).
  - Archivos: `clasificador/entrenamiento/calibracion.py`, `pruebas/entrenamiento/test_calibracion.py`
  - Verificación: con *logits* sobreconfiados construidos a mano, la temperatura ajustada es mayor que 1 y el ECE baja.
  - Commit: `funcionalidad(clasificador): agregar calibracion por temperatura`

## Fase F — Exportación e inferencia

- [x] **T14** — Preprocesamiento de inferencia sin PyTorch: conversión a RGB, límites de 1024 y 224 px, cinco recortes de 224 × 224 y normalización de ImageNet.
  - Archivos: `clasificador/inferencia/__init__.py`, `clasificador/inferencia/preprocesamiento.py`, `pruebas/inferencia/test_preprocesamiento.py`
  - Verificación: imágenes chicas, grandes, verticales, con transparencia y en escala de grises producen `[5, 3, 224, 224]`; valores normalizados conocidos; **el módulo no importa `torch`** (prueba que lo verifica).
  - Commit: `funcionalidad(clasificador): agregar preprocesamiento de inferencia`
- [x] **T15** — Exportación a ONNX con metadatos, verificación de coincidencia con PyTorch (≤ 0,001) y medición de la latencia en CPU. `PredictorOnnx` que lee los metadatos, aplica el preprocesamiento y promedia los recortes.
  - Archivos: `clasificador/exportacion/__init__.py`, `clasificador/exportacion/onnx.py`, `clasificador/inferencia/predictor.py`, `pruebas/exportacion/test_onnx.py`, `pruebas/inferencia/test_predictor.py`
  - Verificación: la exportación de un modelo diminuto coincide con PyTorch; una diferencia forzada lanza `ErrorExportacion`; `PredictorOnnx.predecir` devuelve una `Prediccion` con la versión de los metadatos.
  - Commit: `funcionalidad(clasificador): agregar exportacion onnx y predictor`

## Fase G — Evaluación

- [x] **T16** — Métricas (exactitud, precisión, exhaustividad, F1, AUC, curva ROC, matriz de confusión, ECE) en total y por grupo, y evaluador que ejecuta `PredictorOnnx` sobre un manifiesto y guarda `metricas.json` y los gráficos.
  - Archivos: `clasificador/evaluacion/__init__.py`, `clasificador/evaluacion/metricas.py`, `clasificador/evaluacion/evaluador.py`, `pruebas/evaluacion/test_metricas.py`, `pruebas/evaluacion/test_evaluador.py`
  - Verificación: AUC = 1 con separación perfecta y 0,5 con predicción constante; agrupación por generador y por variante correcta; un grupo de una sola clase informa AUC "no calculable" en lugar de fallar.
  - Commit: `funcionalidad(clasificador): agregar metricas y evaluador`

## Fase H — Seguimiento, registro y compuerta

- [x] **T17** — Seguimiento de experimentos: interfaz `RegistradorExperimentos`, `RegistradorMlflow` (almacén de archivos) y `RegistradorNulo`. Registra el commit, la configuración, la huella del manifiesto, el entorno y las métricas.
  - Archivos: `clasificador/seguimiento/__init__.py`, `clasificador/seguimiento/experimentos.py`, `pruebas/seguimiento/test_experimentos.py`
  - Verificación: `RegistradorMlflow` en una carpeta temporal crea la ejecución con sus parámetros y métricas.
  - Commit: `funcionalidad(clasificador): agregar seguimiento de experimentos`
- [x] **T18** — Ficha del modelo: plantilla Jinja2 y generador que la completa con datos y licencias, manifiesto, partición, arquitectura, hiperparámetros, semilla, entorno, métricas y limitaciones (con la leyenda de que es un indicio y no un veredicto).
  - Archivos: `clasificador/registro/__init__.py`, `clasificador/registro/ficha.py`, `clasificador/plantillas/ficha_modelo.md.j2`, `pruebas/registro/test_ficha.py`
  - Verificación: la ficha generada contiene todas las secciones de CA17; si falta un dato obligatorio, se lanza un error.
  - Commit: `funcionalidad(clasificador): agregar ficha del modelo`
- [x] **T19** — Compuerta de promoción: AUC ≥ umbral, coincidencia ONNX, ficha completa, huella del manifiesto y árbol de Git limpio. Informa todos los motivos de rechazo juntos.
  - Archivos: `clasificador/registro/compuerta.py`, `pruebas/registro/test_compuerta.py`
  - Verificación: una prueba por criterio incumplido y una aprobada.
  - Commit: `funcionalidad(clasificador): agregar compuerta de promocion`
- [x] **T20** — Registro de modelos: interfaz `RegistroModelos`, `RegistroLocal` y `RegistroHuggingFace` (sube el ONNX, la ficha, las métricas y el empaquetado de MLflow, y crea la etiqueta `vX.Y.Z`; rechaza una versión existente). Operación `obtener(version)` que descarga y verifica la huella.
  - Archivos: `clasificador/registro/registro_modelos.py`, `pruebas/registro/test_registro_modelos.py`
  - Verificación: `RegistroLocal` completo; `RegistroHuggingFace` con el cliente de `huggingface_hub` simulado (sin red); publicar dos veces la misma versión falla.
  - Commit: `funcionalidad(clasificador): agregar registro de modelos`

## Fase I — Pipeline completo

- [x] **T21** — Línea de comandos `python -m clasificador <etapa> --configuracion <yaml>` con los subcomandos `obtener`, `validar`, `preparar`, `entrenar`, `evaluar`, `exportar` y `publicar`, y códigos de salida distintos de cero ante errores.
  - Archivos: `clasificador/__main__.py`, `pruebas/test_cli.py`
  - Verificación: `python -m clasificador --help` lista las etapas; un error de validación devuelve un código distinto de cero.
  - Commit: `funcionalidad(clasificador): agregar linea de comandos del pipeline`
- [x] **T22** — Prueba de integración del pipeline mínimo: `preparar → validar → entrenar (2 pasos) → exportar → evaluar → publicar` sobre las *fixtures*, con `RegistradorNulo` y `RegistroLocal`; y prueba de contrato (misma probabilidad con `PredictorOnnx` y con PyTorch más el preprocesamiento de evaluación).
  - Archivos: `pruebas/integracion/test_pipeline.py`, `pruebas/integracion/test_contrato.py`
  - Verificación: `flake8 clasificador/ && pylint clasificador/ && pytest --cov=clasificador --cov-fail-under=80` en verde, local y en GitHub Actions.
  - Commit: `pruebas(clasificador): agregar pruebas de integracion del pipeline`

## Fase J — Prueba de concepto en Kaggle (CA1)

- [ ] **T23** — Cuaderno de prueba de concepto: clona el repositorio en un commit fijo, instala el paquete, lee `HF_TOKEN` de los secretos y ejecuta todas las etapas con `configuracion/prueba_de_concepto.yaml` (no más de 10 000 imágenes de Community Forensics *Small*). Publica en `RegistroLocal`, no en Hugging Face.
  - Archivos: `red_neuronal/cuadernos/00_prueba_de_concepto.ipynb`
  - Verificación: se ejecuta en Kaggle con GPU de punta a punta y produce un `.onnx` que `PredictorOnnx` usa en CPU.
  - Commit: `funcionalidad(clasificador): agregar cuaderno de prueba de concepto`
- [ ] **T24 (manual)** — Ejecutar la prueba de concepto en Kaggle y registrar los tiempos por etapa, el uso de memoria y de disco, y las métricas obtenidas (sin umbral). Estimar el tiempo del entrenamiento completo.
  - Verificación: entrada de bitácora con los valores medidos.
  - Commit: `documentacion(bitacora): registrar prueba de concepto de la red neuronal`

## Fase K — Datos reales

- [ ] **T25** — Cuaderno de exploración de datos: muestra de cada fuente, conteos por generador, formato, tamaño y compresión, ejemplos visuales, y verificación de disponibilidad, licencia y revisión de cada conjunto.
  - Archivos: `red_neuronal/cuadernos/01_exploracion_datos.ipynb`
  - Verificación: el cuaderno ejecutado muestra la tabla de fuentes con su licencia; las fuentes no disponibles o sin licencia verificable quedan excluidas y anotadas.
  - Commit: `funcionalidad(clasificador): agregar cuaderno de exploracion de datos`
- [ ] **T26** — Protocolo de recolección del conjunto propio: herramientas y fecha, cantidad por herramienta, lista de *prompts* por escena del ámbito del sistema, fotos reales equivalentes, fotos editadas, procedimiento para generar las versiones de WhatsApp y de captura, nombres de archivo, planilla de control y reglas de privacidad.
  - Archivos: `docs/guias/protocolo-conjunto-propio.md`
  - Verificación: la autora puede seguirlo sin preguntas (E04).
  - Commit: `documentacion(guias): agregar protocolo del conjunto propio`
- [ ] **T27** — Receta de datos versión 1 a partir de la exploración: fuentes, revisiones fijas, cantidades por generador y clase, generadores reservados como no vistos y semilla.
  - Archivos: `red_neuronal/configuracion/datos_v1.yaml`, `red_neuronal/configuracion/entrenamiento_v1.yaml`
  - Verificación: `python -m clasificador validar` sobre una muestra pequeña de la receta pasa.
  - Commit: `funcionalidad(clasificador): agregar receta de datos v1`
- [ ] **T28 (manual)** — Ejecutar `obtener → validar → preparar` en Kaggle con la receta v1 y guardar el resultado como Kaggle Dataset **privado** `pfg-datos-entrenamiento` (versión 1). Cargar el conjunto propio de E04 como Kaggle Dataset **privado** `pfg-conjunto-propio`.
  - Verificación: ambos conjuntos aparecen como privados; la huella del manifiesto coincide con la calculada en la ejecución.

## Fase L — Entrenamiento, evaluación y publicación

- [ ] **T29** — Cuadernos de entrenamiento y de evaluación del conjunto propio, que solo orquestan las etapas.
  - Archivos: `red_neuronal/cuadernos/02_entrenamiento.ipynb`, `red_neuronal/cuadernos/03_evaluacion_conjunto_propio.ipynb`
  - Commit: `funcionalidad(clasificador): agregar cuadernos de entrenamiento y evaluacion`
- [ ] **T30 (manual)** — Entrenamiento completo en Kaggle con la configuración v1. Si no alcanza AUC ≥ 0,90, analizar los errores por generador, ajustar la configuración (por ejemplo, comparar con ConvNeXt-Tiny) y repetir; cada intento queda en MLflow.
  - Verificación: AUC ≥ 0,90 sobre la prueba de generadores conocidos (CA10).
- [ ] **T31 (manual)** — Verificación de reproducibilidad: repetir el entrenamiento con la misma configuración, manifiesto y semilla.
  - Verificación: diferencia de AUC < 0,01 (CA7).
- [ ] **T32 (manual)** — Evaluación en condiciones reales: conjunto propio por herramienta y por variante (original, WhatsApp, captura) y fotos editadas (CA12, CA13), y generadores no vistos.
  - Verificación: `metricas.json` con todos los grupos; gráficos en la salida de Kaggle.
- [ ] **T33 (manual)** — Exportar, generar la ficha y publicar la versión `1.0.0` en Hugging Face a través de la compuerta. Copiar la ficha al repositorio.
  - Archivos: `red_neuronal/informes/1.0.0/ficha.md` (y gráficos `.png` livianos)
  - Verificación: la etiqueta `v1.0.0` existe en el repositorio de Hugging Face; `RegistroHuggingFace.obtener("1.0.0")` descarga y verifica la huella; la ficha cumple CA17.
  - Commit: `documentacion(clasificador): agregar ficha del modelo 1.0.0`

## Fase M — Documentación

- [ ] **T34** — Documentar el reentrenamiento (CA18): disparadores, incorporación de datos, numeración de versiones y conservación de las anteriores; y el uso del paquete en `red_neuronal/README.md` (instalación, etapas, cuadernos, secretos).
  - Archivos: `red_neuronal/README.md`, `docs/guias/ciclo-de-vida-red-neuronal.md`
  - Commit: `documentacion(clasificador): documentar uso y reentrenamiento`
- [ ] **T35** — Bitácora de cierre: resultados, decisiones, problemas y pendientes para la funcionalidad 012; estado de la funcionalidad 010 en `docs/funcionalidades/README.md`.
  - Archivos: `docs/bitacora/AAAA-MM-DD-red-neuronal.md`, `docs/bitacora/README.md`, `docs/funcionalidades/README.md`
  - Commit: `documentacion(bitacora): registrar cierre de la funcionalidad 010`

## Cierre

- [ ] Pruebas, flake8, pylint y cobertura en verde (local y en GitHub Actions).
- [ ] Criterios de aceptación CA1 a CA21 de la especificación verificados (marcarlos en `especificacion.md`).
- [ ] Ningún dato, imagen propia, modelo ni credencial en el repositorio (`git ls-files red_neuronal/` revisado).
- [ ] Entrada en la bitácora y ADR si hubo decisiones de arquitectura nuevas.
