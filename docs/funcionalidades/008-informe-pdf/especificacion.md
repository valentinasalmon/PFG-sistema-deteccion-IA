# Especificación: 008 — Informe PDF e historial

- **Rama**: `funcionalidad/008-informe-pdf`
- **Estado**: Completada (pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF44, RF45; RNF07 (CA3); completa RF29 CA1 (reabrir un caso con informes) y RN24 (imágenes de un informe)
- **Reglas de negocio aplicadas**: RN21, RN24, RN25, RN27, RN29
- **Casos de uso**: CU28 (generación del informe) y CU29

## Problema

El resultado del análisis ya se ve en pantalla, pero un abogado o una aseguradora necesita un documento para presentar y archivar:
- fijo en el tiempo;
- con los datos del caso, de quién lo pidió y de las versiones usadas;
- con explicaciones que entienda alguien sin formación técnica;
- con las limitaciones de cada técnica.

Con el informe se completa el primer flujo de punta a punta: crear el caso, cargar imágenes, analizarlas y descargar el informe. Ese flujo es la versión v0.1.

## Alcance

### Incluido

**Generar el informe (RF44)**
- Al finalizar cada análisis se genera un informe PDF en español y se guarda en el almacenamiento (S3 en producción).
- El informe no se modifica nunca: un análisis nuevo genera un informe nuevo y los anteriores se conservan.
- Contenido:
  - El caso: número, expediente, tipo, fecha y lugar del hecho.
  - Quién lo pidió: nombre, perfil y colegio de abogados o empresa.
  - La fecha y la hora del análisis.
  - Por cada imagen:
    - Su vista reducida y su huella SHA-256.
    - El estado del sello de tiempo. Hasta la 016 figura como "todavía no disponible".
    - Si su integridad no se pudo verificar, lo dice y no muestra resultados.
  - Por cada capa: el nivel de indicio, las anomalías y la conclusión. Si la capa no estuvo disponible, el motivo.
  - Un recuadro **"¿Qué significa?"** por capa, en lenguaje no técnico, y una explicación de la escala del nivel de indicio.
  - Las versiones de la plataforma, de cada capa y de sus herramientas (RN29).
  - Una sección de **limitaciones y advertencia legal**: la plataforma da indicios y no veredictos, y se recomienda consultar a un perito (RN27).
- Se guarda la huella SHA-256 del propio PDF: permite probar después que el documento no cambió.
- Las imágenes incluidas en un informe ya no pueden eliminarse (RN24). Un caso con informes vuelve a Analizado al reabrirlo (RF29 CA1).
- Si no se puede generar el informe, el análisis igual queda finalizado con sus resultados, y quien puede pedir análisis puede volver a generarlo.
- El correo de fin del análisis avisa que el informe está disponible.

**Historial y descarga (RF45)**
- La pantalla del caso muestra los informes del más reciente al más antiguo, con:
  - La fecha.
  - Quién pidió el análisis.
  - Las imágenes incluidas.
  - La huella del PDF.
- "Descargar" verifica el permiso, queda en la auditoría y entrega un enlace firmado que vence a los 5 minutos. Pueden descargar el Responsable, los Colaboradores y los Lectores.

**Eliminación (RN21)**: al eliminar un caso, una organización o una cuenta, también se borran los PDF de sus informes, y la auditoría guarda sus huellas.

### Excluido

- Sello de tiempo en Blockchain Federal Argentina: funcionalidad 016. El informe ya reserva su lugar.
- Mapas ELA y resultados de las capas 2 a 4: funcionalidades 009, 011 y 012. El informe muestra las capas que tenga el análisis.
- Firma digital del PDF: fuera del alcance (se evalúa como trabajo futuro).

## Criterios de aceptación

### Generar
- [x] **CA1**: Dado un análisis finalizado, entonces se genera un informe PDF y se guarda; el caso pasa a Analizado y el correo avisa que el informe está disponible (RF44 CA3).
- [x] **CA2**: El informe contiene los datos del caso y de quién lo pidió, la fecha y la hora, por cada imagen su vista reducida, su huella y el estado del sello, por cada capa el nivel, las anomalías y la conclusión, las versiones y la sección de limitaciones (RF44 CA1, RNF07 CA3, RN29).
- [x] **CA3**: Cada capa tiene un recuadro "¿Qué significa?" en lenguaje no técnico, y el informe no usa términos de veredicto (RF44 CA2, RN27).
- [x] **CA4**: Un informe guardado no se modifica: un análisis nuevo genera un informe nuevo y los anteriores se conservan, con la huella de cada PDF (RF44 CA4, RN25).
- [x] **CA5**: Una imagen incluida en un informe no se puede eliminar, y un caso con informes vuelve a Analizado al reabrirlo (RN24, RF29 CA1).
- [x] **CA6**: Si no se puede generar el informe, el análisis queda finalizado igual y el informe se puede volver a generar.

### Historial y descarga
- [x] **CA7**: Dado un usuario con permiso sobre el caso, entonces ve los informes del más reciente al más antiguo, con fecha, solicitante e imágenes incluidas (RF45 CA1).
- [x] **CA8**: La descarga verifica el permiso, queda en la auditoría y usa un enlace firmado que vence a los 5 minutos; sin permiso, el caso no existe (RF45 CA2, RNF05).

### Eliminación
- [x] **CA9**: Al eliminar un caso, una organización o una cuenta, se borran los PDF de sus informes y la auditoría guarda sus huellas (RN21).

## Preguntas abiertas

- Ninguna que bloquee. Los textos de "¿Qué significa?" y de la advertencia legal son una propuesta para revisar con los tutores.
