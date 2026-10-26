# 2026-10-26 — Reorganización del tablero de Trello

## Qué se hizo

- **Revisión cruzada** del tablero, del repositorio (funcionalidades 001 a 030, PR #2 a #43, ADR, investigaciones), de `docs/guias/pendientes.md`, del informe en Google Docs (AE2) y de las consignas de la AE1 y la AE2.
- **Listas** alineadas con el Capítulo V del informe: Backlog, En análisis (nueva), En desarrollo, En pruebas y Completado.
- **Etiquetas nuevas**: prioridad (P1, P2, P3), responsable (Autora, Agente IA, Tutores) y área (Desarrollo, Infraestructura, Documento, Relevamiento, Gestión).
- **Completado**: una tarjeta por funcionalidad integrada, con su especificación, su Pull Request y la fecha de integración como vencimiento. También las entrevistas (Veron, Insaurralde, Silva, Miskinich), la encuesta, las pruebas de canales, las entregas AE1 y AE2, los ADR y las investigaciones. Las 18 tarjetas viejas que ya estaban hechas se movieron con un comentario que indica dónde quedó cada una.
- **En pruebas**: 023, 024, 027, 029 y 030, que esperan la verificación de la autora.
- **En desarrollo**: 010, con las tareas pendientes del entrenamiento como lista.
- **Backlog**: lo de `pendientes.md`, las validaciones futuras con usuarios, las deudas de la AE1 y la AE2, una tarjeta por capítulo vacío del protocolo, la gestión (bitácora individual, portafolio, AE3) y una tarjeta por cuestión abierta para los tutores.
- **Archivadas** (con comentario): prototipo en TensorFlow y comparación de prototipos (el sistema usa solo PyTorch y ONNX Runtime), y tarjetas del conjunto de datos absorbidas por la 010.

## Decisiones

- **Columnas iguales a las del informe** (decisión de la autora): el tribunal ve el tablero como Anexo L, así que debe coincidir con lo que declara el Capítulo V. El límite de una tarea en curso por columna no se aplica; se corrige la frase en el informe.
- **Fechas de integración como vencimiento** de las tarjetas completadas, porque las tarjetas se crearon todas hoy y sin la fecha no se vería la evolución real del trabajo (portafolio de la AE1, punto d).
- **El badge de cobertura** se incluye en la tarjeta del prototipo v1 como evidencia de la integración continua (la autora no tenía preferencia).
- **Las historias de usuario** se marcan como completadas: la autora las tiene en un documento aparte.

## Pendiente

- Inconsistencia entre F1 ≥ 0,85 (informe) y AUC ≥ 0,90 (010): tarjeta para los tutores.
- La autora no tiene hecho el portafolio de la AE1 y la AE2: quedó como tarjeta P1.
- Cuando se publique la consigna de la AE3, agregar sus tareas.
