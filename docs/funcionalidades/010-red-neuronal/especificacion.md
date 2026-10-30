# Especificación: 010 — Red neuronal: ciclo de vida, entrenamiento y exportación

- **Rama**: `funcionalidad/010-red-neuronal`
- **Estado**: Borrador
- **Requisitos que realiza**: RNF24; contribuye a RNF19 y RNF20 (calidad e integración continua del código de `red_neuronal/`) y prepara RF42, que se integra en la funcionalidad 012
- **Reglas de negocio aplicadas**: RN27, RN29
- **Casos de uso**: —
- **Guía conceptual**: [Ciclo de vida de la red neuronal](../../guias/ciclo-de-vida-red-neuronal.md)

## Problema

La capa 4 del análisis necesita un clasificador que estime la probabilidad de que una imagen sea íntegramente sintética. Las imágenes que reciben abogados y aseguradoras no suelen provenir de generadores académicos, sino de las herramientas comerciales que usa cualquier persona (ChatGPT, Gemini, Copilot, Midjourney), y en general llegan recomprimidas por aplicaciones de mensajería, que eliminan los metadatos y el manifiesto C2PA. En ese escenario el clasificador es el único indicio disponible, por lo que debe entrenarse con generadores variados y evaluarse en las condiciones reales de uso.

Un modelo no es un archivo aislado sino el producto de un **ciclo de vida**: datos, preparación, entrenamiento, evaluación, exportación, publicación, uso en producción y reentrenamiento cuando aparecen generadores nuevos. Para que el resultado sea defendible ante terceros (RN29) y mantenible en el tiempo, ese ciclo debe estar automatizado, versionado y verificado con las mismas prácticas de ingeniería que el resto del sistema (MLOps).

## Alcance

### Incluido
- **Prueba de concepto**: un recorrido completo y mínimo del pipeline (datos → entrenamiento → evaluación → ONNX → inferencia en CPU) con un subconjunto chico, para validar el diseño antes del entrenamiento completo.
- **Pipeline reproducible** dividido en etapas independientes: obtención de datos, validación de datos, preparación, entrenamiento, evaluación, exportación y publicación del modelo.
- Selección, verificación de licencias y muestreo balanceado de los conjuntos de datos públicos de entrenamiento.
- Armado de un conjunto de prueba propio con generadores comerciales y fotografías reales del ámbito del sistema.
- Entrenamiento por transferencia de aprendizaje de una red neuronal convolucional y exportación a ONNX.
- **Seguimiento de experimentos**: registro de cada ejecución con sus parámetros, datos y métricas.
- **Registro de modelos**: versionado de cada modelo publicado con su ficha, fuera del repositorio.
- **Integración continua** del código de `red_neuronal/`: análisis estático y pruebas automáticas.
- **Compuerta de promoción**: verificación automática de que un modelo cumple los criterios antes de quedar disponible para el backend.
- Documentación del ciclo de vida, de los flujos y de cada versión del modelo.

### Excluido
- Integración del modelo en el motor de análisis y en el informe PDF (funcionalidad 012).
- Despliegue del modelo en AWS (funcionalidad 017).
- Monitoreo del modelo en producción con datos de casos reales: los casos son confidenciales (RNF08) y no se reutilizan para entrenar. El reentrenamiento se dispara por la aparición de generadores nuevos, no por datos de usuarios.
- Detección de ediciones parciales como requisito: solo se mide (CA13). Las ediciones se abordan con las capas 2 y 3 (funcionalidades 009 y 011).
- Uso comercial del modelo: ver *Preguntas abiertas*.

## Criterios de aceptación

### Prueba de concepto

- [x] **CA1 — Recorrido completo**: con un subconjunto de no más de 10 000 imágenes, el pipeline se ejecuta de punta a punta y produce un modelo ONNX que clasifica una imagen en CPU. La prueba de concepto no exige umbral de desempeño; su objetivo es validar el pipeline y estimar tiempos y recursos del entrenamiento completo, que se registran en la bitácora.

### Datos

- [ ] **CA2 — Fuentes de entrenamiento**: el modelo se entrena con un subconjunto balanceado entre imágenes reales y sintéticas, tomado de Community Forensics (versión *Small*), OpenFake, MS COCOAI y ShareGPT-4o-Image. La licencia de cada conjunto se verifica y se registra; un conjunto sin licencia verificable se excluye.
- [ ] **CA3 — Versionado de datos**: cada conjunto preparado se identifica con un manifiesto versionado en el repositorio que lista el origen, el generador, la clase, la partición y la huella SHA-256 de cada imagen. Las imágenes no se suben al repositorio.
- [ ] **CA4 — Validación de datos**: antes de entrenar se verifica automáticamente que no haya imágenes corruptas ni duplicadas, que no haya solapamiento entre particiones y que las clases estén balanceadas. Si alguna verificación falla, el pipeline se detiene.
- [ ] **CA5 — Prevención de atajos**: las imágenes reales y las sintéticas comparten formato, compresión y rango de tamaños, de modo que el modelo no pueda distinguirlas por características ajenas a la generación. Se documenta cómo se verificó.
- [ ] **CA6 — Partición**: los conjuntos de entrenamiento, validación y prueba se obtienen con una semilla fija. Al menos un generador queda fuera del entrenamiento y se usa solo como generador no visto.

### Entrenamiento y evaluación

- [ ] **CA7 — Reproducibilidad**: con el mismo manifiesto, la misma configuración y la misma semilla, una nueva ejecución obtiene métricas equivalentes (diferencia en el área bajo la curva ROC menor a 0,01).
- [ ] **CA8 — Configuración externa**: los hiperparámetros, las rutas y la semilla se definen en archivos de configuración versionados, no en el código.
- [ ] **CA9 — Seguimiento de experimentos**: cada ejecución de entrenamiento queda registrada con la versión del código, el manifiesto de datos, la configuración, el entorno y las métricas, y puede compararse con las anteriores.
- [ ] **CA10 — Umbral de aceptación**: sobre el conjunto de prueba de generadores conocidos, el área bajo la curva ROC es ≥ 0,90 (RNF24 CA3).
- [ ] **CA11 — Métricas**: se reportan exactitud, precisión, exhaustividad, F1, área bajo la curva ROC, curva ROC y matriz de confusión, en total y por generador.

### Condiciones reales de uso

- [ ] **CA12 — Conjunto propio**: se arma un conjunto de prueba con al menos 50 imágenes por herramienta (ChatGPT, Gemini, Copilot y, si hay acceso, Midjourney) y al menos 200 fotografías reales propias, de escenas del ámbito del sistema: daños en vehículos, lesiones, daños en viviendas, documentos, recibos y capturas de conversaciones. Se evalúa en tres versiones (original, enviada por WhatsApp y captura de pantalla) y se reporta el desempeño por herramienta y por versión, sin umbral obligatorio. Ninguna de estas imágenes se sube al repositorio.
- [ ] **CA13 — Ediciones**: se evalúan al menos 50 fotografías reales editadas con ChatGPT y Gemini y se reporta el resultado, sin umbral obligatorio.

### Exportación, publicación y ciclo de vida

- [ ] **CA14 — Exportación**: el modelo se exporta a ONNX y se ejecuta en CPU con ONNX Runtime. Sobre una muestra del conjunto de prueba, su salida coincide con la del modelo original (diferencia absoluta máxima de 0,001 en la probabilidad) y se registra el tiempo de inferencia por imagen.
- [ ] **CA15 — Compuerta de promoción**: un modelo solo se publica como apto para producción si cumple CA10 y CA14 y tiene su ficha completa. La verificación es automática y su resultado queda registrado.
- [ ] **CA16 — Registro de modelos**: cada modelo publicado tiene una versión con formato `MAJOR.MINOR.PATCH`, su huella SHA-256 y su ficha. El backend puede obtener una versión concreta por su identificador, y la versión queda registrada en cada informe (RN29, RNF24 CA4).
- [ ] **CA17 — Ficha del modelo**: cada versión tiene una ficha en `red_neuronal/informes/` con los conjuntos de datos y sus licencias, el manifiesto, la partición, la arquitectura, los hiperparámetros, la semilla, el entorno de entrenamiento, las métricas de CA11 a CA14 y las limitaciones: no detecta ediciones parciales, su desempeño puede disminuir frente a generadores no vistos (con los valores medidos) y su resultado es un indicio, no un veredicto (RN27).
- [ ] **CA18 — Reentrenamiento**: está documentado cuándo se reentrena (por ejemplo, ante un generador comercial nuevo cuyo desempeño en el conjunto propio cae de forma significativa), cómo se incorporan los datos nuevos y cómo se publica la nueva versión sin romper la reproducibilidad de los informes anteriores.

### Ingeniería del código

- [ ] **CA19 — Calidad**: el código de `red_neuronal/` está en módulos con docstrings y en español (RNF21), separado de los cuadernos. Los cuadernos solo orquestan y muestran resultados; la lógica vive en módulos reutilizables y probados.
- [ ] **CA20 — Integración continua**: cada envío al repositorio que modifique `red_neuronal/` ejecuta automáticamente el análisis estático y pruebas que no requieren GPU ni descargar datos: preparación y validación de datos con imágenes de prueba mínimas, un paso de entrenamiento sobre un lote diminuto, exportación a ONNX y coincidencia de salidas, y cálculo de métricas.
- [ ] **CA21 — Repositorio limpio**: no se suben al repositorio conjuntos de datos, imágenes propias, modelos entrenados ni credenciales de Google, GitHub o Hugging Face; las credenciales se configuran como secretos de la plataforma.

## Preguntas abiertas

- **Licencias no comerciales**: casi todos los conjuntos son solo para investigación. Alcanza para el proyecto final, pero si la plataforma se comercializa (CP-01), el modelo debe reentrenarse con datos de licencia compatible. Se registra como trabajo futuro.
- **Gemini y Copilot**: no hay datos públicos de entrenamiento confirmados para estos generadores, por lo que se evalúan como generadores no vistos.
- **Disponibilidad de las herramientas**: al armar el conjunto propio se verifica qué modelo usa cada herramienta en ese momento, y se registra junto con la fecha.
- **Herramientas de MLOps** (seguimiento de experimentos, registro de modelos, versionado de datos): se eligen en el plan técnico y se registran como ADR.
