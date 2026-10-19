# 2026-10-19 — Funcionalidad 007: motor de análisis y capa 1 (metadatos)

## Qué se hizo

Las imágenes del caso ya se analizan. Se eligen, se presiona "Analizar" y el análisis corre en segundo plano con su progreso visible. La primera capa revisa los metadatos.

Documentos: [especificación](../funcionalidades/007-motor-de-analisis/especificacion.md), [plan](../funcionalidades/007-motor-de-analisis/plan.md) (incluye la revisión del código del TIF), [tareas](../funcionalidades/007-motor-de-analisis/tareas.md) y [ADR-0013](../arquitectura/decisiones/0013-cola-de-analisis-intercambiable.md). La rama `funcionalidad/007-motor-de-analisis` parte de `desarrollo` con la 006 integrada.

- **Capa de metadatos** (`app/analisis/metadatos.py`): reescritura de `metadatos_service.py` del repositorio anterior (`valentinasalmon/TIF`).
  - **Se conservan**:
    - Sus siete reglas: software declarado, historial XMP, parámetros de generación en PNG, MakerNotes, cronología, bloque de captura y dimensiones típicas.
    - Su escala de severidad.
    - El aplanado de claves de ExifTool y la defensa ante valores numéricos.
  - **Se mejoran**:
    - Una sola lectura de ExifTool por la entrada estándar, sin copias de la evidencia en disco.
    - La ruta de ExifTool es configurable (el TIF usaba un `.exe` de Windows).
    - Se usa la fecha de carga en lugar de la "fecha del sistema".
    - Se agrega la fecha anterior al lanzamiento del dispositivo, con una tabla editable.
    - Se agregan el origen sintético IPTC y las declaraciones de las credenciales de contenido (C2PA) sin verificar.
    - La ausencia de metadatos se informa como dato neutro.
    - Hay un nivel de indicio de 0 a 100 con un método documentado.
    - La conclusión no tiene veredicto e incluye la recomendación de consultar a un perito.
    - Se arma una tabla de metadatos relevantes.
    - La capa es pura (no escribe en la base).
- **Motor**:
  - `ServicioAnalisis` y la interfaz común de capas (ADR-0006).
  - Verificación de la huella antes de analizar.
  - Una capa que falla queda "No disponible" y el resto sigue.
  - Progreso por imagen y por capa, y detección de análisis interrumpidos.
  - Historial de análisis y correos de fin y de falla.
- **Cola intercambiable** (ADR-0013): RQ en producción (con `backend/trabajador.py`), un hilo del servidor en desarrollo y ejecución en el momento en las pruebas.
- **Frontend**:
  - Casillas para elegir imágenes (por defecto, las no analizadas) y el botón "Analizar".
  - Progreso consultado cada dos segundos.
  - Sección "Análisis" con el historial y, por cada imagen y capa: nivel de indicio, conclusión, hallazgos con su severidad, metadatos extraídos y versión.

## Revisión del código del TIF

El detalle está en el [plan](../funcionalidades/007-motor-de-analisis/plan.md#revisión-de-la-capa-de-metadatos-del-tif). Lo más importante:

- **Defecto encontrado**: la regla de historial XMP del TIF **nunca se activaba**. Pedía `-XMP:History` a ExifTool sin `-struct`, y en ese modo ExifTool devuelve `HistoryAction`, `HistoryWhen`, etc., no `History`. Se verificó con ExifTool 12.76 sobre una imagen con historial. La capa nueva usa `-struct` y tiene una prueba de regresión.
- **Hallazgo con imágenes reales**: las imágenes de ChatGPT y Gemini no traen EXIF ni XMP, solo el manifiesto C2PA. Sin leer sus declaraciones, la capa habría informado "sin metadatos". Ahora informa el generador y el origen declarados, aclarando que la firma se verifica en la capa 2 (009).
- **Prueba con las diez imágenes de canales del TIF** (no se copiaron al repositorio):
  - Original, WhatsApp como documento y correo: nivel 90.
  - WhatsApp como foto y captura de pantalla: 0, o 20 por las dimensiones.
  - Coincide con el experimento de canales del TIF.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA3 Pedido | Pruebas de API y de pantalla: cola, caso En análisis, imágenes elegidas por defecto, botón deshabilitado, sin imágenes, imágenes de otro caso, Lector, caso cerrado, análisis en curso | Cumplidos |
| CA4 Integridad | Prueba que altera el archivo guardado: la imagen se excluye y queda en la auditoría | Cumplido |
| CA5 – CA7 Procesamiento | Progreso con consultas periódicas (prueba de pantalla y navegador), interrupción por falta de avance, falla general, cola caída, correos de fin y de falla | Cumplidos |
| CA8 – CA11 Capa | 37 pruebas unitarias con imágenes generadas y metadatos escritos por ExifTool | Cumplidos |
| CA12 – CA14 Resultado | Conclusiones sin términos de veredicto, capa no disponible (sin ExifTool y por excepción), sin puntaje global, versión de la capa y de ExifTool | Cumplidos |

**Cifras:**
- Backend: 343 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 179 pruebas, cobertura del 98 %, ESLint sin errores y compilación correcta.
- Migración `161ae29f2074`: probada con `upgrade`, `check` y `downgrade` en PostgreSQL.

**Recorrido en navegador real** con la cola en hilo y ExifTool, con tres imágenes:
- Un JPEG que declara Photoshop y un iPhone 15 Pro con fecha de captura de 2021. Resultado 90: editor declarado, MakerNotes ausentes, fecha anterior al lanzamiento y parámetros de captura ausentes.
- Un PNG sin metadatos. Resultado 0, con la aclaración sobre la mensajería.
- Una imagen de ChatGPT. Resultado 90 por las declaraciones C2PA.
- El progreso se vio en pantalla y los resultados llegaron en 2,3 segundos.
- El caso pasó a Analizado y llegó el correo de aviso.
- Las imágenes analizadas quedaron desmarcadas para el próximo análisis.
- A 375 px no hay desbordes y no hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Nivel de indicio**: base de la anomalía más grave (directo 90, fuerte 70, moderado 45, débil 20, neutro 0) + 10 por cada otra moderada o más grave, con un máximo de 90. El 100 queda reservado al manifiesto C2PA válido que declara IA (RN28). Mantiene la equivalencia con la clasificación del TIF. **Para validar con los tutores.**
- **Cola en hilo para el desarrollo** (ADR-0013): no hace falta acordarse de un trabajador, y se ve el progreso real. En producción es RQ, como dice ADR-0004.
- **Interrupciones por falta de avance** (15 minutos sin progreso): cubre la caída del trabajador con cualquier cola, sin depender de RQ.
- **Las declaraciones C2PA se leen en la capa 1, sin verificar la firma, y se aclara.** La verificación es de la capa 2 (009).
- **Tolerancia de un día** entre la fecha de captura y la de carga, porque EXIF no guarda la zona horaria.
- **Al terminar, el caso pasa a Analizado** sin esperar el informe PDF, que llega con la 008.
- **Correo de fin y de falla**, aunque las notificaciones generales son de la 013, porque el usuario puede irse de la pantalla (ADR-0004).
- **Código compartido**: `registrar_en_caso` en la auditoría (lo usan imágenes y análisis) y `crear_estudio` en las pruebas, para evitar repeticiones.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| Importación circular entre la fábrica de servicios y la tarea de la cola | El trabajo se encola por su ruta de importación (`"app.tareas.analisis.ejecutar_analisis"`), como lo acepta RQ |
| `meter` mostraba el porcentaje dos veces (contenido alternativo y texto) | El porcentaje se muestra una sola vez junto a la barra |
| Las pruebas viejas de la pantalla del caso pedían rutas nuevas sin simular | Se agregó la respuesta vacía del historial de análisis |

## Pendientes

- **Autora**:
  - Revisar e integrar el Pull Request de la 007.
  - Validar con los tutores las severidades y el cálculo del nivel de indicio.
  - En tu computadora, `pip install -r requirements-dev.txt` (instala RQ) y `flask --app wsgi db upgrade`.
- **008**: informe PDF del análisis (WeasyPrint ya está), `Imagen.en_informe` y `Caso.tiene_informes`.
- **009, 011 y 012**: las capas 2 a 4 se suman en `app/analisis/registro.py`.
- **014**: límite mensual de análisis por plan (CU27 paso 3).
