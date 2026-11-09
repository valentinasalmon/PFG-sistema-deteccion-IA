# 2026-10-30 — Red neuronal (010): exploración de datos, receta v1 y cuaderno de entrenamiento completo

## Qué se hizo

- **Exploración de candidatos (T25)** en el paquete: `clasificador/datos/exploracion.py` y el subcomando `python -m clasificador explorar`. Para cada conjunto de `configuracion/candidatos_v1.yaml` verifica la revisión exacta, la licencia de la ficha (sin licencia verificable, excluido), las columnas, los conteos por clase y por generador (leyendo solo columnas livianas) y el formato y la calidad JPEG de una muestra. Propone el bloque de la receta. Cuaderno `02_exploracion_datos_colab.ipynb`, que corre en CPU.
- **Receta v1 provisoria (T27)** en `configuracion/v1.yaml`. El esquema suma `archivos` (muestreo por archivos), `generadores_incluidos`, `cuota_por_generador` y `clase_fija`.
- **Cuaderno de entrenamiento completo (T29)**, `03_entrenamiento_completo_colab.ipynb`: saltea las etapas terminadas con el subcomando nuevo `estado`, guarda los datos preparados en Drive (`evidentia/datos/<receta>/preparado.tar`, T28) y evalúa el conjunto propio si ya está en Drive.
- **Evaluación:** «no visto» se compara contra las reales de prueba (antes solo tenía sintéticas y el AUC no se podía calcular); el conjunto propio se desglosa también por escena y conserva el nombre original de cada archivo.
- **Búsqueda de fotos reales** de lesiones, obras y viviendas (investigación del 2026-10-30, sección nueva).
- **Guía paso a paso del conjunto propio** (`docs/guias/guia-paso-a-paso-conjunto-propio.md`), pedida por la autora: lista maestra de 90 prompts numerados con las partes ya elegidas, versiones v1, v2 y v3 de cada prompt, 20 ediciones, carpetas, rutina por imagen, fotos reales a sacar y cómo buscar conjuntos y pasarlos al chat.
- Pruebas: 203 (antes 177), cobertura 97 %, pylint 10/10.

## Decisiones (del agente, con su justificación)

- **Las fotos reales de escenas del sistema (CarDD, SCIN, MOCS) no se usan para entrenar**: en el entrenamiento no hay sintéticas de esas escenas, así que el modelo aprendería el tema («auto dañado = real»). Van al conjunto propio, para evaluar.
- **El generador reservado se toma con una fuente aparte** y la fuente principal lo excluye: si no, al pasar a «no visto» desbalancearía el entrenamiento.
- **Un mismo prompt en todas las herramientas**, con el número de prompt en el nombre del archivo: compara las herramientas con el mismo contenido.
- **Lesiones repartidas en seis tonos de piel**, cinco prompts por tono y dos de cada uno en la prioridad A.
- **Conjuntos de heridas de Kaggle y Roboflow descartados**: fotos juntadas de internet, sin origen verificable y, en un caso, reducidas a un tamaño fijo (atajo de formato).
- **Meta AI desde la web**, no dentro de WhatsApp: ahí la imagen ya llega comprimida.
- Los cuadernos se numeraron 02 y 03 porque el 01 ya es la prueba de concepto; la evaluación del conjunto propio quedó dentro del 03.

## Problemas

- Desde el entorno del agente no se puede acceder a Hugging Face (403 del proxy): los nombres de columnas y de generadores de OpenFake y los demás candidatos quedan «a confirmar» hasta correr el cuaderno 02.

## Pendiente

- Autora: aceptar las condiciones de los conjuntos en Hugging Face y correr el cuaderno 02 en CPU; pasar la tabla, los generadores y la propuesta.
- Agente: completar `v1.yaml` con esos datos y preparar la copia de las muestras de CarDD, SCIN y MOCS a Drive.
- Autora: empezar la prioridad A de la lista maestra (E04).
- Tablero de Trello: actualizado en la segunda parte de la sesión (ver abajo).

## Segunda parte: decisiones de la autora sobre el alcance

- **Viviendas fuera** (CP-39 resuelta; se numeró primero CP-33 y después CP-38, ya usadas en desarrollo para Clarity y los precios): se quitaron de CA12 de la especificación.
- **Sin versión de WhatsApp**: la persona afectada sube sus fotos desde el enlace de carga, así que llegan como original, captura o generadas con IA. El conjunto propio queda con dos versiones (original y captura). Se actualizaron la especificación (CA12), los capítulos 1, 2, 4, 5, 6, 11 y 12 de `docs/red-neuronal/`, el glosario, el protocolo, la guía y la tarea T32. El código sigue admitiendo la variante `whatsapp` (no estorba y permite volver a medirla).
- **Guía:** sección nueva para aceptar las condiciones de cada conjunto en Hugging Face (con el permiso que necesita un token de grano fino) y abrir y correr el cuaderno 02 en Colab.
- **Insumos del informe:** relevamiento completo de fuentes con la decisión y el motivo de cada una.
- **Trello:** tarjeta de la 010 con las casillas de T24, T26 y T29 marcadas, T32 sin WhatsApp, descripción y comentario de actualización; tarjeta nueva para que la autora corra el cuaderno 02.


## 2026-11-02: autos sin repetir en la lista maestra

La autora notó que en la lista maestra se repetían los modelos de auto (12 modelos para 32 prompts) y solo cambiaba el daño: así varias imágenes muestran casi el mismo auto y aportan poco. Se cambió el auto de los prompts 13 a 32 por 20 modelos nuevos, de modo que cada auto aparece una sola vez. Los prompts 1 a 12 quedaron iguales para no tirar lo ya generado; de la prioridad A hay que rehacer el 17, 18, 19, 20, 25, 26, 27 y 28.

## 2026-11-03: revisión del avance de la autora en Drive

- Conjunto propio: el prompt 1 está hecho en ChatGPT, Gemini y Copilot, con original y captura. Las carpetas se crearon en mayúsculas (`SINTETICA/GEMINI/ORIGINAL`) y en la raíz de Mi unidad.
- Se hizo que la fuente de carpeta local lea las carpetas sin distinguir mayúsculas de minúsculas, con su prueba: así no hace falta renombrarlas.
- Pendiente de la autora: mover `SINTETICA` y `REAL` dentro de `evidentia/conjunto-propio/` y renombrar las capturas `001-choque-01.png` a `01-choque-001.png` (primero la escena, después el número).
- La carpeta `evidentia/exploracion/` está vacía. La copia del cuaderno 02 guardada en Drive muestra por qué: la exploración arrancó con Community Forensics y a los 62 s terminó con el **código -9** (Colab mató el proceso por falta de memoria).
- **Causa:** para describir 24 imágenes de muestra se leía el primer grupo de filas con `read_row_group`, y pyarrow baja el bloque entero de la columna de imágenes. Se comprobó con un Parquet de prueba de 300 MB: tanto `read_row_group` como `iter_batches` leen los 300 MB aunque se pidan 24 filas.
- **Corrección:** antes de bajar la muestra se lee en los metadatos el tamaño del bloque (66 KB de lectura para saberlo) y, si pasa de 256 MB, se omite y se anota como aviso; los conteos por clase y generador siguen, porque leen solo columnas livianas (66 KB en la misma prueba). Además los resultados se guardan después de cada candidato y el cuaderno corre cada candidato en su propio proceso (`--solo`), así un corte no se lleva a los demás. 206 pruebas, pylint 10/10.

## 2026-11-04: exploración ejecutada y receta v1 completa

- La autora volvió a correr el cuaderno 02 con la corrección: terminó en 25 minutos, cada conjunto en su proceso. Community Forensics y OpenFake quedaron incluidos; Treasure, MLLM-Generated, ShareGPT-4o y CarDD no están en Parquet; Semi-Truths no declara una licencia verificable; ConstructionSite espera la aprobación del acceso. Detalle en el capítulo 4.
- **La propuesta automática no alcanzaba:** pedía 50 generadores con 400 imágenes cada uno, pero en los archivos elegidos solo 6 generadores pasan de 160 imágenes. La descarga se habría cortado con «la fuente se agotó». Se rehízo a mano: sin lista de generadores, con cuota por generador, y con cantidades calculadas sobre lo disponible.
- **Hallazgos para el informe:** cada archivo de Community Forensics tiene una sola clase y un bloque de hasta 4,1 GB; las reales de OpenFake son fotos de hasta 8 192 px y ~4 MB, contra ~880 px de las sintéticas (sesgo de tamaño y formato que la normalización neutraliza).
- **Decisiones (del agente):** la familia de Google (Imagen 4, Imagen 3, Nano Banana 2) como no vista, porque es lo que usa Gemini y sostiene la demostración de reentrenamiento; búfer de mezcla configurable por fuente (300 en OpenFake) para no agotar la RAM; el cuaderno 03 borra las imágenes crudas después de preparar y pide RAM amplia.
- 207 pruebas en verde.
- Pendiente: Pull Request de la rama, cuaderno 03 (entrenamiento completo), muestra de CarDD para el conjunto propio, pedir de nuevo el acceso a ConstructionSite.

## 2026-11-04 (tarde): depuración de los datos y arreglos del cuaderno 03

- A pregunta de la autora («¿usamos los conjuntos completos?»): no, se usa una muestra, pero la depuración tenía dos huecos. Se agregó: excluir por nombre los generadores que no hacen fotos (56 de Community Forensics y 10 de OpenFake) y descartar las imágenes de menos de 256 px, además de no agrandar nunca al normalizar. La receta quedó en 17 500 reales y 17 500 sintéticas. 209 pruebas, pylint 10/10.
- El cuaderno 03 falló en la sección 5 con `No module named 'onnxruntime'`: Colab no ve las bibliotecas instaladas después de abrir el cuaderno. Ahora consulta el estado de las etapas con un comando aparte, sin importar el paquete. Además, si la configuración cambió pero todavía no hay etapas hechas, la pisa en lugar de detenerse.
- El conjunto propio está en la carpeta del proyecto compartida por el tutor (`PFG 2026 - Valentina/RED NEURONAL`). El cuaderno 03 lo busca ahí. Se registró CP-40 sobre dónde guardar las fotos reales de personas.
- Segundo intento del cuaderno 03: `No module named 'onnx'`, esta vez dentro del comando aparte. La causa real era que **al cuaderno 03 le faltaba la celda de instalación del paquete** (al armarlo se copiaron las celdas de credenciales y clonado, pero no la de `pip install`). Se agregó, con una verificación en un proceso aparte que detiene el cuaderno con un mensaje claro si falta alguna biblioteca. Lección: los cuadernos también se revisan contra una ejecución real, no solo su sintaxis.

## 2026-11-05: entrenamiento completo

- La autora corrió el cuaderno 03 (con la instalación corregida). Preparar tardó 48 minutos; el entrenamiento llegó a las 15 épocas, con la mejor en la 12 (AUC de validación 0,948).
- Resultados (capítulo 11): **AUC de prueba 0,961, F1 0,904** (cumple los dos criterios de CP-07), familia de Google no vista con AUC 0,938, ONNX fiel y 22,9 ms por imagen.
- **Hallazgo:** en el conjunto propio (49 choques generados con ChatGPT, Gemini y Copilot) detecta solo 5. Falta sumar fotos reales de choques para medir el AUC por escena.
- El resumen que pegó la autora se había generado antes del entrenamiento; los resultados se leyeron directamente de los archivos que el cuaderno respaldó en Drive. No se ejecutó la publicación.

