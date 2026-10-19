# Especificación: 007 — Motor de análisis y capa 1 (metadatos)

- **Rama**: `funcionalidad/007-motor-de-analisis`
- **Estado**: Aprobada (por el asistente, según el reparto del 2026-10-16; pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF38, RF39, RF43, RF46; RNF07 (CA2, integridad antes de analizar), RNF13 (análisis en segundo plano)
- **Reglas de negocio aplicadas**: RN19, RN25, RN26, RN27, RN29
- **Casos de uso**: CU27 y la parte de CU28 que ejecuta las capas (sin el informe)

## Problema

Las imágenes ya están en el caso, pero todavía nadie las analiza. Esta funcionalidad agrega el botón "Analizar", el procesamiento en segundo plano con su progreso y la primera capa: el análisis de metadatos EXIF, XMP y PNG.

La capa de metadatos ya tenía un buen avance en el repositorio anterior (`valentinasalmon/TIF`): sus siete reglas, su escala de severidad y sus pruebas se revisan, se reescriben con la interfaz común de capas (ADR-0006) y se mejoran.

## Alcance

### Incluido

**Solicitar el análisis (RF38)**
- El Responsable o un Colaborador elige imágenes del caso (por defecto, las que todavía no se analizaron) y presiona "Analizar". Sin imágenes elegidas, el botón queda deshabilitado.
- El caso tiene que estar en Borrador o Analizado. Mientras el análisis está en curso, el caso queda En análisis: no admite cambios ni otro análisis.
- Antes de analizar cada imagen se recalcula su huella SHA-256. Si no coincide con la registrada, la imagen se excluye y se informa como anomalía de integridad.

**Procesamiento en segundo plano (RF46)**
- El análisis se encola y lo ejecuta un proceso trabajador (ADR-0004).
- La pantalla muestra el estado, sin recargar a mano:
  - En cola.
  - En proceso, con la imagen y la capa en curso.
  - Finalizado.
  - Fallido.
- Si el análisis se interrumpe (por ejemplo, se cae el proceso trabajador), queda Fallido, el caso vuelve a su estado anterior y se avisa a quien lo pidió.
- Al finalizar, el caso pasa a Analizado y se avisa por correo a quien lo pidió.

**Capa 1: metadatos (RF39)**
- Extracción con ExifTool (EXIF, XMP, IPTC, datos PNG) y Pillow.
- Indicios que detecta:
  - Software de edición o de generación declarado.
  - Historial de edición en XMP.
  - Parámetros de generación de IA en los datos de un PNG.
  - Origen sintético declarado en el vocabulario IPTC.
  - Fechas imposibles: posteriores a la carga o anteriores al lanzamiento del dispositivo declarado.
  - Modificación muy posterior a la captura.
  - Dispositivo declarado sin los datos que ese fabricante suele incluir.
  - Dimensiones típicas de modelos generativos.
- La ausencia de metadatos se informa como dato, aclarando que puede deberse a la recompresión de las aplicaciones de mensajería y que no implica manipulación por sí misma.
- El resultado incluye una tabla con los metadatos relevantes.

**Resultado por capa (RF43)**
- Cada capa devuelve:
  - Un nivel de indicio de 0 % a 100 %, con el método de cálculo documentado.
  - La lista de anomalías.
  - Una conclusión redactada como indicio, con la recomendación de consultar a un profesional (RN27).
- Si una capa falla, su resultado es "No disponible" con el motivo, y el resto sigue (RN26).
- No hay puntaje que combine las capas.
- Se registra la versión de cada capa y de sus herramientas (RN29).

**Historial**: el caso conserva todos sus análisis; cada uno muestra sus resultados.

**Auditoría**: solicitud, finalización y falla de cada análisis, e imágenes excluidas por integridad.

### Excluido

- Capas 2 (C2PA), 3 (ELA) y 4 (red neuronal): funcionalidades 009, 011 y 012. El motor queda preparado para registrarlas sin cambiar las existentes.
- Informe PDF: funcionalidad 008. Hasta entonces, el resultado se consulta en pantalla.
- Límite mensual de análisis del plan (CU27 paso 3): funcionalidad 014.
- Panel y notificaciones en la plataforma: funcionalidad 013 (en la 007 solo se envía el correo).

## Criterios de aceptación

### Solicitar
- [ ] **CA1**: Dado un caso en Borrador o Analizado, cuando el Responsable o un Colaborador elige imágenes y presiona "Analizar", entonces el análisis se encola, el caso pasa a En análisis y la pantalla muestra el progreso (RF38 CA1).
- [ ] **CA2**: Sin imágenes elegidas, el botón "Analizar" está deshabilitado; un pedido sin imágenes, con imágenes de otro caso, de un Lector o sobre un caso en otro estado se rechaza (RF38 CA2, RN19, RN20).
- [ ] **CA3**: Dado un caso En análisis, entonces no se puede pedir otro análisis hasta que termine (RF38 CA3).
- [ ] **CA4**: Dada una imagen cuya huella recalculada no coincide con la registrada, entonces se excluye del análisis y se informa como anomalía de integridad (RF38 CA4, RNF07).

### Procesar
- [ ] **CA5**: El estado del análisis (en cola, en proceso con imagen y capa, finalizado o fallido) se actualiza en la pantalla sin recargarla (RF46 CA1).
- [ ] **CA6**: Dada una interrupción del procesamiento, entonces el análisis queda Fallido, el caso vuelve a su estado anterior y se avisa por correo a quien lo pidió (RF46 CA2).
- [ ] **CA7**: Dado un análisis terminado, entonces el caso pasa a Analizado, queda en el historial y se avisa por correo a quien lo pidió.

### Capa de metadatos
- [ ] **CA8**: Dada una imagen que declara un editor o un generador conocido en `Software` o `CreatorTool`, entonces se informa como anomalía (RF39 CA1).
- [ ] **CA9**: Dada una fecha de captura posterior a la carga, o anterior al lanzamiento del dispositivo declarado, entonces se informa como fecha imposible (RF39 CA2).
- [ ] **CA10**: Dada una imagen sin metadatos, entonces se informa su ausencia como dato, sin elevar el nivel de indicio (RF39 CA3).
- [ ] **CA11**: El resultado incluye la tabla de metadatos relevantes extraídos (RF39 CA4).

### Resultado por capa
- [ ] **CA12**: Cada resultado tiene nivel de indicio (0 a 100), anomalías y conclusión con la recomendación de consultar a un profesional; ninguna conclusión usa términos de veredicto (RF43 CA1, CA2; RN27).
- [ ] **CA13**: Dada la falla de una capa, entonces su resultado es "No disponible" con el motivo y el análisis continúa (RF43 CA3, RN26).
- [ ] **CA14**: No se calcula ni se muestra un puntaje que combine capas, y cada resultado registra la versión de la capa y de sus herramientas (RF43 CA4, RN29).

## Preguntas abiertas

- Ninguna que bloquee. Las severidades y el cálculo del nivel de indicio son propuestas documentadas en el plan, para validar con los tutores.
