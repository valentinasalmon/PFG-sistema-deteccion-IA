# Especificación: 006 — Carga de imágenes, huella y almacenamiento

- **Rama**: `funcionalidad/006-imagenes`
- **Estado**: Aprobada (por el asistente, según el reparto del 2026-10-16; pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF34, RF35 (sin sello de tiempo ni informes), RF36; RNF03 (CA1), RNF05, RNF06, RNF07 (huella), RNF09 (CA2)
- **Reglas de negocio aplicadas**: RN15 (solo el límite de imágenes por caso), RN19, RN21 (archivos de los casos eliminados), RN22, RN23, RN24 (preparada para la 008)
- **Casos de uso**: CU25 a CU27

## Problema

El caso ya existe, pero todavía no puede contener la evidencia: las imágenes del siniestro o del reclamo. Para que después se puedan analizar (007) y citar en un informe (008), cada imagen tiene que guardarse sin modificarse, con una huella que pruebe su integridad, y solo deben verla las personas con permiso sobre el caso.

## Alcance

### Incluido

**Cargar (RF34)**
- El Responsable y los Colaboradores cargan una o más imágenes en un caso en Borrador o Analizado.
- Cada archivo se valida por separado y la pantalla informa el resultado de cada uno.
- Solo se aceptan JPEG y PNG. El formato se determina por la firma binaria del contenido, no por la extensión ni por el tipo que declara el navegador.
- El tamaño máximo es de 20 MB por imagen (RN22, propuesta).
- La huella SHA-256 se calcula al recibir el archivo, antes de cualquier procesamiento, y el original nunca se modifica (RN23).
- Se registran:
  - Nombre original, tamaño, formato y dimensiones.
  - Huella y quién la cargó.
- Una imagen con la misma huella que otra del mismo caso se informa como duplicada y no se vuelve a guardar.
- Límite de imágenes por caso según el plan del espacio (CP-02): Personal 20, Organización Básico 50, Organización Profesional 100.

**Consultar (RF35)**
- La pantalla del caso muestra las imágenes con:
  - Una vista previa (miniatura).
  - El nombre original, el formato, las dimensiones y el tamaño.
  - La huella SHA-256, la fecha de carga y quién la cargó.
- La miniatura es una copia reducida, aparte del original.
- La vista previa y la descarga del original usan enlaces firmados que vencen a los 5 minutos.

**Eliminar (RF36)**
- El Responsable y los Colaboradores eliminan una imagen de un caso en Borrador o Analizado, con confirmación.
- Se borran el original y la miniatura, con todas sus versiones, y la auditoría guarda la huella.
- Una imagen incluida en un informe no puede eliminarse (RN24). Los informes llegan con la 008; la regla queda preparada.

**Archivos de los casos eliminados (RN21)**
- Al eliminar un caso, una organización con sus casos o una cuenta con sus organizaciones, también se borran sus imágenes del almacenamiento.
- La auditoría de la eliminación del caso guarda las huellas de los archivos eliminados.

**Almacenamiento**
- Hay dos implementaciones intercambiables, como prevé la estructura del repositorio:
  - **S3** para producción: bucket privado, cifrado en reposo y versionado (RNF03 CA1).
  - **Local** para el desarrollo y las pruebas: carpeta del servidor que nunca se sube al repositorio.
- Las rutas de los archivos no son predecibles ni contienen datos personales (RNF09 CA2).

**Auditoría**: carga (exitosa, rechazada o duplicada), descarga del original y eliminación, con la huella.

### Excluido

- Sello de tiempo en Blockchain Federal Argentina y su estado: funcionalidad 016.
- Análisis de las imágenes: funcionalidad 007.
- Informes en los que fue incluida la imagen: funcionalidad 008.
- Límite de almacenamiento total del plan y cambio de plan: funcionalidad 014.
- Creación del bucket real en AWS: funcionalidad 017 (Terraform).

## Criterios de aceptación

### Cargar
- [ ] **CA1**: Dado un JPEG o PNG válido de hasta 20 MB en un caso en Borrador o Analizado, cuando lo carga el Responsable o un Colaborador, entonces se guarda sin modificar, con su huella SHA-256, el nombre original, el tamaño, el formato, las dimensiones y quién lo cargó (RF34 CA1, RN23).
- [ ] **CA2**: Dado un archivo con extensión de imagen cuyo contenido no es JPEG ni PNG, entonces se rechaza indicando que el formato real no es válido (RF34 CA2, RN22).
- [ ] **CA3**: Dado un archivo de más de 20 MB, o un caso que ya tiene el máximo de imágenes de su plan, entonces se rechaza indicando el límite (RF34 CA3, RN15).
- [ ] **CA4**: Dada una imagen con la misma huella que otra del caso, entonces se informa que es un duplicado y no se vuelve a guardar (RF34 CA4).
- [ ] **CA5**: Dada una carga de varios archivos, entonces cada uno se valida por separado y se informa el resultado de cada uno (RF34 CA5).
- [ ] **CA6**: Dado un Lector, o un caso Cerrado o Archivado, entonces no se pueden cargar ni eliminar imágenes (RN19, RN20).

### Consultar
- [ ] **CA7**: Dado un usuario con permiso sobre el caso, entonces ve las imágenes con su vista previa y sus datos técnicos; sin permiso, el caso responde como si no existiera (RF35 CA1, RNF05).
- [ ] **CA8**: La vista previa y la descarga del original se sirven con enlaces firmados que vencen a los 5 minutos; un enlace vencido o alterado no entrega nada (RF35 CA2).

### Eliminar
- [ ] **CA9**: Dada una imagen que no está en ningún informe, cuando se elimina, entonces se borran el original y la miniatura con todas sus versiones, y la auditoría guarda la huella (RF36 CA1).
- [ ] **CA10**: Dado un caso, una organización o una cuenta que se elimina, entonces también se borran del almacenamiento las imágenes de sus casos, y la auditoría guarda sus huellas (RN21).

### Almacenamiento
- [ ] **CA11**: Las claves de los archivos son aleatorias y no contienen datos personales; en S3, los archivos se guardan cifrados (RNF03, RNF09 CA2).

## Preguntas abiertas

- Ninguna que bloquee. El tamaño máximo de 20 MB (RN22) y los límites por plan (CP-02) siguen como propuestas.
