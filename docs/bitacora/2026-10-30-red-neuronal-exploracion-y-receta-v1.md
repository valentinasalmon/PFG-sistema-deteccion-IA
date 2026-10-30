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
- CP-33: confirmar si «daños en viviendas» sale de CA12.
- Tablero de Trello: el agente no tiene acceso en esta sesión; mover a mano las tarjetas de T25, T27 y T29.
