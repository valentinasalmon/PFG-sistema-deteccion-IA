# Plan técnico: 007 — Motor de análisis y capa 1 (metadatos)

Referencias: [especificacion.md](especificacion.md) · [ADR-0004](../../arquitectura/decisiones/0004-procesamiento-asincrono-rq.md) (RQ) · [ADR-0006](../../arquitectura/decisiones/0006-capas-de-analisis-strategy.md) (capas como Strategy) · [ADR-0013](../../arquitectura/decisiones/0013-cola-de-analisis-intercambiable.md) (cola intercambiable) · [análisis de reutilización del TIF](../../arquitectura/reutilizacion-repositorio-tif.md).

## Resumen de la solución

1. **Pedido.**
   - `ServicioAnalisis.solicitar` valida el permiso, el estado del caso y las imágenes.
   - Crea el `Analisis` (en cola) con una fila por imagen, pasa el caso a En análisis (guarda el estado anterior), registra la auditoría y confirma.
   - Recién después encola el trabajo, así el trabajador nunca lee un análisis que todavía no existe.
2. **Cola** (ADR-0013). Tres implementaciones con la misma interfaz `encolar(funcion, *argumentos)`:
   - **RQ** en producción (ADR-0004).
   - **Hilo** en desarrollo: no hace falta levantar un trabajador aparte.
   - **Sincrónica** en las pruebas.
3. **Procesamiento** (`ServicioAnalisis.procesar`, sin Flask). Pasa el análisis a En proceso. Por cada imagen:
   - Lee el original del almacenamiento y recalcula la huella. Si no coincide, excluye la imagen con una anomalía de integridad.
   - Ejecuta cada capa registrada y guarda su resultado. Si una capa lanza una excepción, su resultado es "No disponible" con el motivo (RN26).
   - Actualiza el progreso (imagen y capa) y confirma después de cada paso.
   - Al terminar: análisis Finalizado, caso Analizado, auditoría y correo. Si falla algo general: análisis Fallido, el caso vuelve a su estado anterior, auditoría y correo.
4. **Interrupciones.** Si un análisis en cola o en proceso no avanza durante 15 minutos (`TIEMPO_MAXIMO_SIN_AVANCE`), la siguiente consulta lo marca como Fallido con el mismo tratamiento. Así se cubre la caída del trabajador sin depender de la cola (RF46 CA2).
5. **Capas** (ADR-0006).
   - `app/analisis/base.py` define `Anomalia`, `ResultadoCapa`, `ContextoImagen` y la interfaz `CapaAnalisis` (`nombre`, `version()`, `analizar(contenido, contexto)`).
   - Las capas son funciones puras: reciben los bytes y el contexto, no tocan la base.
   - `app/analisis/registro.py` arma la lista de capas activas: hoy, solo metadatos.

## Revisión de la capa de metadatos del TIF

Código revisado: `app/services/metadatos_service.py` y `tests/test_metadatos_exif.py` del repositorio `valentinasalmon/TIF` (commit `ccdddd0`).

### Qué funciona y se conserva

| Elemento del TIF | Evaluación | En la 007 |
|---|---|---|
| Detección del formato por firma binaria | Correcta | Ya está en `app/utilidades/imagenes.py` (006); se reusa |
| ExifTool con `-json -G0:1` y claves aplanadas (`EXIF:IFD0:Make` → `Make`), con encoding UTF-8 | Correcto y probado | Se conserva |
| `str()` antes de `.lower()` (ExifTool devuelve números JSON) | Correcto | Se conserva, con prueba de regresión |
| Software conocido en `Software` o `CreatorTool` (severidad directo) | Útil | Se conserva y se amplía la lista; se separan editores y generadores para que el texto sea preciso |
| Historial XMP (`History`) (directo) | Útil | Se conserva |
| Parámetros de generación en los datos de un PNG (directo) | Útil | Se conserva y se amplía: `parameters` (AUTOMATIC1111), `workflow` (ComfyUI) y más palabras clave |
| MakerNotes ausentes con marca conocida (fuerte) | Útil | Se conserva; se suman marcas (Canon, Nikon, Sony, Fujifilm, Olympus, Panasonic, OnePlus, Oppo, Vivo, Realme) |
| `ModifyDate` más de 24 h después de `DateTimeOriginal` (moderado) | Útil | Se conserva |
| Bloque de captura vacío con dispositivo declarado (moderado) | Útil | Se conserva |
| Dimensiones típicas de IA (débil) | Útil | Se conserva y se amplía con las salidas de DALL·E 3, GPT Image y SDXL |
| Escala de severidad: directo, fuerte, moderado, débil, neutro | Útil | Se conserva |
| Pruebas que escriben metadatos con ExifTool sobre imágenes generadas | Buen modelo | Se reescriben con el mismo enfoque |

### Qué se corrige o mejora

| Problema en el TIF | Mejora |
|---|---|
| Ruta fija a `tools/exiftool.exe` (solo Windows) | Configuración `RUTA_EXIFTOOL` (por defecto, `exiftool` del sistema) |
| Dos llamadas a ExifTool (todo y XMP) sobre un archivo en disco | Una sola llamada que lee la imagen por la entrada estándar: no se escriben copias temporales de la evidencia |
| "Fecha de creación del sistema" con `os.path.getctime` (en el servidor es la fecha de copia) | Fecha de carga registrada en la base (RF39 CA2) |
| Solo comparaba la fecha del sistema con `DateTimeOriginal` | Se agrega la fecha anterior al lanzamiento del dispositivo declarado (RF39 CA2), con una tabla de modelos editable |
| Historial XMP pedido sin `-struct`: la regla nunca se activaba | `-struct` y prueba de regresión |
| Sin lectura de las declaraciones C2PA | Software y origen declarados en el C2PA, informados sin verificar la firma (la verifica la capa 2) |
| Sin regla para la ausencia de metadatos | Anomalía de severidad neutra con la aclaración de RF39 CA3; no eleva el nivel |
| No leía el origen sintético IPTC (`DigitalSourceType`) | Se detecta `trainedAlgorithmicMedia` y `compositeSynthetic` en XMP (directo) |
| Clasificación en cuatro categorías de texto | Nivel de indicio de 0 a 100 con un método documentado (RF43) |
| La capa guardaba en la base (`AnalisisRepository`) | La capa es pura y devuelve un `ResultadoCapa`; el servicio persiste (ADR-0006) |
| Sin conclusión redactada ni recomendación | Conclusión como indicio, con la recomendación de consultar a un profesional (RN27) y prueba de que no aparecen palabras de veredicto |
| Sin tabla de metadatos en el resultado | Tabla de campos relevantes (RF39 CA4) |
| Soporte HEIC | Se quita: la plataforma solo acepta JPEG y PNG (RN22) |
| `ConclusionFinal`, que combinaba capas | Se descarta (RN27, ADR-0006) |

### Hallazgos durante la implementación

- **La regla de historial XMP del TIF nunca se activaba.** El TIF pedía `-XMP:History` sin `-struct`. Así, ExifTool no devuelve la clave `History`, sino `HistoryAction`, `HistoryWhen`, etc. (se verificó con ExifTool 12.76 sobre una imagen con historial). La capa nueva usa `-struct` y tiene una prueba de regresión.
- **Las imágenes de ChatGPT y Gemini no traen EXIF ni XMP**: lo que declaran está en las credenciales de contenido (C2PA). ExifTool lee esas declaraciones sin verificar la firma: acciones con `softwareAgent` y `digitalSourceType`, y `claim_generator_info`.
  - La capa de metadatos las informa como origen o software declarado, con la aclaración "sin verificar su firma".
  - La conclusión remite a la capa de credenciales de contenido (009) para la verificación.
  - Sin esto, la v0.1 informaría "sin metadatos" para una imagen que declara haber sido generada con IA.

### Resultado con las imágenes de prueba del TIF

Se analizaron las diez imágenes de `tests/imagenes_prueba/` del TIF (generadas con ChatGPT y Gemini y enviadas por distintos canales). No se copiaron al repositorio.

| Canal | ChatGPT | Gemini |
|---|---|---|
| Archivo original | 90 (C2PA declara ChatGPT y origen sintético; dimensiones típicas) | 90 (C2PA declara origen sintético) |
| WhatsApp como documento | 90 | 90 |
| Correo electrónico | 90 | 90 |
| WhatsApp como foto | 20 (solo las dimensiones; sin metadatos) | 0 (sin metadatos) |
| Captura de pantalla | 0 (sin metadatos) | 0 (sin metadatos) |

Coincide con el experimento de canales del TIF: WhatsApp como foto y la captura de pantalla eliminan toda la información. En esos casos la capa informa la ausencia de metadatos como dato (RF39 CA3), y las capas 3 y 4 son las que pueden aportar indicios.

### Cálculo del nivel de indicio de la capa de metadatos

Cada anomalía tiene una severidad, y cada severidad tiene un valor base:

| Severidad | Base |
|---|---|
| Directo | 90 |
| Fuerte | 70 |
| Moderado | 45 |
| Débil | 20 |
| Neutro | 0 |

**Nivel** = base de la anomalía más grave + 10 por cada otra anomalía moderada o más grave. El resultado tiene un **máximo de 90**.

Ejemplos:
- Solo dimensiones típicas de IA: 20.
- Dos moderadas: 55.
- Una fuerte y una moderada: 80.
- Software de edición declarado: 90.

El máximo de la capa es 90 porque el indicio más fuerte del sistema es un manifiesto C2PA válido que declara IA (RN28, capa 2). Este cálculo es una propuesta para validar con los tutores.

La equivalencia con la clasificación del TIF se mantiene: una anomalía directa, o dos fuertes, o una fuerte y una moderada daban "fuerte", y ahora dan 80 o más.

## Capas afectadas

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Análisis | `app/analisis/base.py`, `metadatos.py`, `dispositivos.py`, `registro.py` | Capas puras |
| Integraciones | `app/integraciones/cola.py` | Cola RQ, en hilo o sincrónica |
| Modelos | `app/modelos/analisis.py` (`Analisis`, `AnalisisImagen`, `ResultadoCapa`, `Anomalia`) | Tablas |
| Repositorios | `repositorio_analisis.py` | Consultas |
| Servicios | `servicio_analisis.py`, `servicio_correos.py`, `auditoria.py`, `fabrica.py` | Reglas y orquestación |
| Esquemas y rutas | `app/esquemas/analisis.py`, `app/rutas/analisis.py`; `app/esquemas/imagenes.py` (imagen ya analizada) | API |
| Tareas | `app/tareas/analisis.py`, `backend/trabajador.py` | Entrada del trabajador RQ |
| Configuración | `RUTA_EXIFTOOL`, `COLA_ANALISIS`, `TIEMPO_MAXIMO_SIN_AVANCE` | — |
| Migraciones | Tablas de análisis | — |
| Frontend | `src/api/analisis.js`, `SeccionImagenes.jsx` (selección y "Analizar"), `SeccionAnalisis.jsx` (progreso, historial y resultados), `PaginaCaso.jsx` | Pantallas |

## Contratos

| Método y ruta | Respuesta |
|---|---|
| `POST /api/casos/<id>/analisis` | Cuerpo `{"imagenes": [ids]}`; responde 202 con el análisis en cola |
| `GET /api/casos/<id>/analisis` | Historial: estado, fechas, solicitante y cantidad de imágenes |
| `GET /api/casos/<id>/analisis/<id_analisis>` | Estado, progreso y resultados por imagen y por capa |

Acciones de auditoría: `analisis.solicitud`, `analisis.finalizacion`, `analisis.falla` y `analisis.integridad`.

## Cambios en datos

- `analisis`:
  - Columnas: `id`, `id_caso` (FK `CASCADE`), `id_solicitante` (FK `SET NULL`), `estado` (`en_cola`, `en_proceso`, `finalizado`, `fallido`), `estado_anterior_caso`, `imagen_actual`, `capa_actual`, `motivo_falla`, `versiones` (JSON), `creado_en`, `iniciado_en`, `finalizado_en` y `actualizado_en`.
- `analisis_imagenes`:
  - Columnas: `id`, `id_analisis` (FK `CASCADE`), `id_imagen` (FK `SET NULL`), `nombre`, `huella`, `orden` e `integridad` (`verificada` o `alterada`).
  - Conserva el nombre y la huella aunque la imagen se elimine.
- `resultados_capa`:
  - Columnas: `id`, `id_analisis_imagen` (FK `CASCADE`), `capa`, `estado` (`completado` o `no_disponible`), `nivel`, `conclusion`, `motivo`, `detalle` (JSON) y `version`.
- `anomalias`:
  - Columnas: `id`, `id_resultado` (FK `CASCADE`), `campo`, `valor`, `descripcion` y `severidad`.

## Bibliotecas nuevas

- **RQ 2.12.0**: cola de trabajos sobre Redis (ADR-0004).
- **ExifTool** del sistema (paquete `libimage-exiftool-perl`, ya incluido en el script de entorno).

## Estrategia de pruebas

- **Unitarias de la capa**: imágenes generadas en memoria con metadatos escritos por ExifTool para cada regla, con los mismos casos del TIF más los nuevos. También:
  - Regresión de valores numéricos.
  - Cálculo del nivel.
  - Palabras de veredicto prohibidas.
  - ExifTool ausente: la capa queda "No disponible".
- **Integración**: pedido, permisos, estados, integridad alterada, capa que falla, análisis interrumpido, historial, correos y auditoría, con la cola sincrónica.
- **Cola**: implementación RQ con un Redis falso; implementación en hilo.
- **Frontend**: selección, botón deshabilitado, progreso con consulta periódica y resultados.
- **Manual**: recorrido en navegador con imágenes generadas con y sin metadatos, con la cola en hilo.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| ExifTool no instalado en el servidor | La capa queda "No disponible" con el motivo; `/api/salud` no se ve afectado. Se documenta la instalación |
| Falsos positivos por software de fábrica (por ejemplo, la versión del sistema del teléfono en `Software`) | La lista solo tiene editores y generadores, no fabricantes |
| La tabla de fechas de lanzamiento queda desactualizada | Archivo de datos editable; un modelo desconocido no genera anomalía |
| Hilos en desarrollo y procesos de Flask con recarga | El hilo abre su propio contexto de aplicación y sesión de base; en producción se usa RQ |
