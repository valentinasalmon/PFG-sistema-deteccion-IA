# Plan técnico: 008 — Informe PDF e historial

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

- **`ServicioInformes.generar(analisis)`**:
  - Arma los datos con `app/informes/informe_analisis.py` y convierte la plantilla `informe_analisis.html` a PDF con WeasyPrint.
  - Guarda el PDF en el almacenamiento (`informes/<aleatorio>.pdf`).
  - Suma el `Informe` a la transacción, con la huella SHA-256 del PDF.
  - Marca como `en_informe` las imágenes verificadas que incluye (RN24).
- **Generación al final del análisis**:
  - `ServicioAnalisis._finalizar` llama a `generar` antes de pasar el análisis a Finalizado.
  - Si falla, deshace solo lo del informe, registra la falla en el log y el análisis termina igual.
  - Quien puede pedir análisis lo vuelve a generar con `POST …/analisis/<id>/informe`.
- **Miniaturas embebidas**: las vistas reducidas se leen del almacenamiento y van dentro del PDF como datos, así el documento no depende de enlaces que vencen.
- **Plantillas compartidas**: `app/informes/plantillas.py` concentra el entorno Jinja2, los filtros de fecha (incluida la hora de Argentina) y la conversión a PDF. Lo usan el informe y la copia de datos de la 019.
- **Historial y descarga**:
  - `GET /api/casos/<id>/informes` lista los informes.
  - `GET …/informes/<id>/descarga` devuelve un enlace firmado de 5 minutos, igual que las imágenes, y la descarga queda en la auditoría.
- **Eliminación**: `ArchivosDeCasos` también anota los PDF de los casos que se eliminan, para borrarlos después de confirmar y guardar sus huellas en la auditoría (RN21).

## Capas afectadas

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Modelos | `app/modelos/informe.py`; `imagen.py` (`en_informe` pasa a columna); `caso.py` (`informes`, `tiene_informes` real); `analisis.py` (`informe`) | Datos |
| Repositorios | `repositorio_informes.py` | Consultas |
| Documentos | `app/informes/plantillas.py`, `informe_analisis.py`, `app/plantillas/informes/informe_analisis.html`; `copia_de_datos.py` usa el entorno común | PDF |
| Servicios | `servicio_informes.py`; `servicio_analisis.py` (genera al finalizar); `servicio_imagenes.py` (`ArchivosDeCasos` con PDF); `servicio_correos.py`; `auditoria.py`; `fabrica.py` | Reglas |
| Esquemas y rutas | `app/esquemas/analisis.py` (`informe_a_dict`), `app/rutas/informes.py` | API |
| Migraciones | `7d203719a8cb_crear_tabla_de_informes.py` | Tabla y columna |
| Frontend | `src/api/informes.js`, `SeccionInformes.jsx`, `SeccionAnalisis.jsx` (descargar o generar), `PaginaCaso.jsx` | Pantallas |

## Contenido del informe

| Parte | Contenido |
|---|---|
| Encabezado | Número de caso y de análisis, y aviso de que son indicios y no veredictos |
| Datos del caso | Número, expediente, tipo, fecha y lugar del hecho, espacio |
| Solicitud | Nombre, perfil, colegio de abogados o empresa, fecha y hora del pedido (hora de Argentina), cantidad de imágenes |
| Cómo leer este informe | Escala del nivel de indicio; las capas no se suman ni se promedian |
| Por imagen | Vista reducida, huella SHA-256, estado del sello de tiempo (pendiente hasta la 016), integridad |
| Por capa | Nivel con barra, conclusión, hallazgos con su severidad, tabla de metadatos, recuadro "¿Qué significa?" y versión |
| Versiones | Plataforma, cada capa con sus herramientas, plantilla, WeasyPrint |
| Limitaciones y advertencia legal | Cinco puntos: indicios y no dictamen; falsos positivos y negativos; metadatos borrables; generadores nuevos; consultar a un perito |
| Pie de página | Caso, fecha y hora de generación, número de página |

## Cambios en datos

- `informes`: `id`, `id_caso` (FK `CASCADE`), `id_analisis` (FK `CASCADE`, único), `clave` (única), `huella`, `tamanio` y `generado_en`.
- `imagenes.en_informe`: booleano, falso por defecto.

## Bibliotecas nuevas

Ninguna: WeasyPrint ya estaba desde la 019.

## Estrategia de pruebas

- **Unitarias**: el HTML del informe contiene cada dato pedido. Los textos explicativos no tienen términos de veredicto. También se prueban la capa no disponible, la imagen alterada, la empresa de una aseguradora y la cuenta eliminada, se genera un PDF real y se verifica la hora de Argentina.
- **Integración**:
  - Generación con huella y descarga idéntica.
  - Un informe nuevo no toca el anterior.
  - RN24, y reabrir a Analizado.
  - Imagen alterada sin marca.
  - Falla y regeneración.
  - Permisos del Lector y de quien no tiene acceso.
  - Borrado del PDF con el caso.
- **Frontend**: historial, descarga desde el historial y desde el análisis, regeneración, el Lector sin regeneración, errores.
- **Manual**: recorrido en navegador y revisión visual del PDF descargado.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| WeasyPrint sin las bibliotecas del sistema | Ya están en el script de WSL y en la integración continua; si falla, el análisis termina y el informe se regenera después |
| PDF de muchas imágenes, pesado o lento | Se embeben miniaturas de 480 px, no los originales |
| Textos explicativos con términos de veredicto | Prueba automática con la lista de términos prohibidos (encontró uno durante el desarrollo) |
