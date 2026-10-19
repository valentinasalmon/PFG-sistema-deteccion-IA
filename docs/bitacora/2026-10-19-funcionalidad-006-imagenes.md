# 2026-10-19 — Funcionalidad 006: carga de imágenes, huella y almacenamiento

## Qué se hizo

Los casos ya tienen evidencia: se cargan imágenes JPEG y PNG, se guardan sin modificar con su huella SHA-256, se consultan con su vista previa y se eliminan. Es el primer paso del flujo completo hacia la v0.1. Documentos: [especificación](../funcionalidades/006-imagenes/especificacion.md), [plan](../funcionalidades/006-imagenes/plan.md), [tareas](../funcionalidades/006-imagenes/tareas.md) y [ADR-0012](../arquitectura/decisiones/0012-almacenamiento-de-imagenes-intercambiable.md). La rama `funcionalidad/006-imagenes` parte de `desarrollo` con la 019 integrada.

- **Backend**:
  - Tabla `imagenes` (migración `6df33b3b5d51`).
  - Almacenamiento intercambiable: S3 en producción y carpeta local en desarrollo.
  - `ServicioImagenes`, con validación por firma binaria, huella, duplicados, límite por plan, miniaturas y enlaces firmados de 5 minutos.
  - Borrado de los archivos al eliminar un caso, una organización o una cuenta (RN21).
- **Frontend**: sección "Imágenes" en la pantalla del caso, que reemplaza el aviso de "próximamente":
  - Carga de varios archivos con el resultado de cada uno.
  - Galería con vista previa, datos técnicos y huella.
  - Descarga del original y eliminación con confirmación.
- **Otros**:
  - `backend/README.md` con la sección "Imágenes de los casos" y el error `externally-managed-environment` (entorno virtual sin activar) en "Problemas frecuentes".
  - Corrección de un defecto de pylint que había quedado de la 019.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA6 Cargar | Pruebas de API: original idéntico y huella, JPEG y PNG en varios modos de color, formato real inválido (texto, GIF, truncada, vacía), tamaño, 413, límite Personal y Básico, duplicado, archivos independientes, Lector, Colaborador y caso cerrado. Pruebas de pantalla | Cumplidos |
| CA7, CA8 Consultar | Pruebas de API: vista previa a 480 px, sin permiso = 404, descarga idéntica con nombre UTF-8, enlaces alterados y vencidos. Pruebas de pantalla | Cumplidos |
| CA9, CA10 Eliminar | Pruebas de API: archivos borrados con su huella en la auditoría al eliminar una imagen, un caso, una organización y una cuenta. Falla del almacenamiento sin caída | Cumplidos |
| CA11 Almacenamiento | Claves `imagenes/<32 hex>` sin el nombre del archivo; S3 con `AES256` y borrado de todas las versiones (prueba con `moto`) | Cumplido |

**Cifras:**
- Backend: 286 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 168 pruebas, cobertura del 98 %, ESLint sin errores y compilación correcta.
- Migración: probada con `upgrade`, `check` y `downgrade` en PostgreSQL.

**Recorrido en navegador real** con imágenes generadas para la prueba (nunca de casos reales):
- Carga de tres archivos: un JPEG de 3000 × 2000, un PNG y un texto con extensión `.jpg`. Los dos primeros se cargan y el tercero se rechaza por su formato real.
- Volver a cargar el mismo JPEG se informa como duplicado.
- El original descargado tiene exactamente el mismo tamaño que el cargado.
- La eliminación actualiza el contador.
- En el celular (375 px) no hay desbordes.
- Al cerrar el caso desaparece la opción de cargar.
- La carpeta `almacenamiento_local/` no aparece en `git status`.
- No hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Almacenamiento local en desarrollo, en lugar de S3 o MinIO.** La estructura del repositorio ya preveía "S3 y local". Así no tenés que instalar nada nuevo ni tener credenciales de AWS para desarrollar (ADR-0012).
- **Un archivo por solicitud.** Cumple "cada archivo se valida por separado" (RF34 CA5), da progreso por archivo y evita solicitudes de cientos de MB.
- **La huella se calcula antes de todo** y el original nunca pasa por Pillow para guardarse: se guarda el contenido recibido, byte por byte (RN23).
- **Miniatura aparte** (JPEG de 480 px): la vista previa no descarga 20 MB y el original queda intacto.
- **Enlaces firmados de 5 minutos**: la vista previa y la descarga cumplen RF35 CA2. La descarga del original queda en la auditoría.
- **La huella va en la auditoría con la clave `sha256`.** El filtro de seguridad de la 003 descarta las claves con "huella". Ese filtro hacía que la lista `huellas_eliminadas` de la 005 nunca se guardara: ahora se registra como `sha256_eliminados`.
- **Límites por plan** con los valores de CP-02 (Personal 20, Básico 50, Profesional 100), en la configuración hasta la 014.
- **Los archivos se borran después de confirmar la base.** Si falla el borrado, queda en el log; si falla la base al cargar, se borran los archivos recién escritos.
- **Las claves foráneas de SQLite activas en las pruebas** (desde la 019) permiten probar que las imágenes se van con su caso.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| La auditoría descartaba la huella de las imágenes | Clave `sha256`, con un comentario en el filtro que explica por qué |
| Una prueba del log fallaba solo con la suite completa: las pruebas de migraciones configuran el log de Alembic y apagan los existentes | La prueba vuelve a encender ese log |
| Después de cerrar el caso seguía visible "Elegir imágenes" hasta recargar la página | La sección se vuelve a montar cuando cambia el estado del caso |
| pylint marcaba demasiados atributos en `ServicioDatosPersonales` (venía de la 019) | Los repositorios se guardan en un diccionario |

## Pendientes

- **Autora**: revisar e integrar el Pull Request de la 006. El tamaño máximo de 20 MB (RN22) y los límites por plan (CP-02) siguen como propuestas.
- **007**: el motor de análisis lee los originales con `almacenamiento.leer`.
- **008**: `Imagen.en_informe` real (RN24).
- **016**: estado del sello de tiempo en la galería (RF35 CA1).
- **017**: bucket de S3 con cifrado, versionado y bloqueo de acceso público en Terraform.
