# Plan técnico: 006 — Carga de imágenes, huella y almacenamiento

Referencia: [especificacion.md](especificacion.md) · Decisión de arquitectura: [ADR-0012](../../arquitectura/decisiones/0012-almacenamiento-de-imagenes-intercambiable.md).

## Resumen de la solución

- **Tabla nueva `imagenes`**:
  - Guarda los datos técnicos y la huella.
  - Los archivos (original y miniatura) viven en el almacenamiento, bajo claves aleatorias.
- **`ServicioImagenes`**:
  - Reusa los permisos del caso, con `ServicioCasos.caso_con_permiso`.
  - Valida cada archivo en este orden: huella SHA-256 primero (RN23), tamaño, firma binaria (RN22), integridad con Pillow, duplicado en el caso y límite del plan.
  - Genera la miniatura (480 px, JPEG) como copia aparte.
- **`ArchivosDeCasos`**:
  - Al eliminar casos (directamente, con su organización o con la baja de una cuenta), anota sus archivos antes de quitarlos y devuelve sus huellas para la auditoría.
  - Los borra después de confirmar la base (RN21).
- **Una solicitud por archivo**: la pantalla envía los archivos de a uno. Así cada archivo se valida por separado y se informa su resultado (RF34 CA5), sin solicitudes enormes. Flask corta antes las solicitudes de más de 21 MB y responde 413 con el límite.

## Capas afectadas

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Modelos | `app/modelos/imagen.py`; `caso.py` (relación `imagenes`) | Tabla y restricciones |
| Repositorios | `repositorio_imagenes.py` | Consultas |
| Integraciones | `app/integraciones/almacenamiento.py` (`AlmacenamientoS3`, `AlmacenamientoLocal`) | Archivos y enlaces firmados |
| Utilidades | `app/utilidades/imagenes.py` | Firma binaria, dimensiones, miniatura, bombas de descompresión |
| Servicios | `servicio_imagenes.py`; `servicio_casos.py`, `servicio_organizaciones.py`, `servicio_datos_personales.py` (archivos de los casos eliminados); `auditoria.py`; `fabrica.py` | Reglas |
| Esquemas y rutas | `app/esquemas/imagenes.py`, `app/rutas/imagenes.py`, `errores.py` (413) | API |
| Configuración | `ALMACENAMIENTO`, `DIRECTORIO_ALMACENAMIENTO`, `S3_*`, `TAMANIO_MAXIMO_IMAGEN`, `MAX_CONTENT_LENGTH`, `VIGENCIA_ENLACE_ARCHIVO`, `LADO_MINIATURA`, `imagenes_por_caso` en los planes; `.gitignore` | — |
| Migraciones | `6df33b3b5d51_crear_tabla_de_imagenes.py` | Tabla |
| Frontend | `src/api/cliente.js` (FormData), `src/api/imagenes.js`, `SeccionImagenes.jsx`, `PaginaCaso.jsx`, `utilidades/archivos.js`, estilos | Pantalla |

## Contratos

| Método y ruta | Respuesta |
|---|---|
| `GET /api/casos/<id>/imagenes` | `{imagenes, limite, tamanio_maximo, puede_modificar}` |
| `POST /api/casos/<id>/imagenes` (multipart, `archivo`) | 201 `{imagen, mensaje}`. Errores: 400 (formato, dañada, tamaño, vacío), 409 `imagen_duplicada`, `limite_imagenes` o `caso_solo_lectura`, 413 si la solicitud es demasiado grande |
| `GET /api/casos/<id>/imagenes/<id>/descarga` | `{url}` firmada por 5 minutos |
| `DELETE /api/casos/<id>/imagenes/<id>` | 409 `imagen_en_informe` desde la 008 |
| `GET /api/archivos/<token>` | Archivo del almacenamiento local (solo desarrollo y pruebas) |

Acciones de auditoría: `imagen.carga` (exitosa o rechazada con el motivo), `imagen.descarga` e `imagen.eliminacion`. La huella se registra con la clave `sha256`: el filtro de la auditoría descarta las claves con "huella" o "hash", que se reservan para la contraseña. `caso.eliminacion` y `organizacion.eliminacion` registran `sha256_eliminados`.

## Cambios en datos

Tabla `imagenes`:
- Columnas: `id`, `id_caso` (FK `CASCADE`), `clave`, `clave_miniatura`, `nombre_original`, `formato` (`jpeg` o `png`), `tamanio`, `ancho`, `alto`, `huella` (índice), `id_usuario` (FK `SET NULL`) y `cargada_en`.
- Únicos: `(id_caso, huella)`, `clave` y `clave_miniatura`.

## Bibliotecas nuevas

- **Pillow 13.0.0**: dimensiones, verificación y miniaturas. También la usarán las capas de análisis (ELA).
- **boto3 1.43.114**: S3 en producción.
- **moto 5.2.4** (solo desarrollo): simula S3 en las pruebas.

## Estrategia de pruebas

- **Integración**:
  - Cada criterio de aceptación con imágenes generadas en memoria.
  - Permisos y estados.
  - Enlaces alterados y vencidos.
  - Borrado de archivos al eliminar una imagen, un caso, una organización y una cuenta.
  - Fallas del almacenamiento.
- **Unitarias**: firma binaria, imágenes truncadas, bombas de descompresión, miniatura, y adaptadores S3 (con `moto`) y local.
- **Frontend**: galería, carga múltiple con resultados, permisos, descarga, eliminación y vista previa vencida.
- **Manual**: recorrido en navegador con imágenes generadas.

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Archivos huérfanos si falla el borrado después de confirmar | Quedan en el log con su clave; la 015 puede agregar una limpieza periódica |
| Imágenes muy grandes en píxeles agotan la memoria | Pillow rechaza las bombas de descompresión y se convierten en "imagen dañada" |
| Vistas previas que vencen con la pantalla abierta | Botón para volver a pedir el listado con enlaces nuevos |
