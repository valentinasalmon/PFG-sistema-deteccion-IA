# 015 · Retención y destrucción de datos

**Requisitos**: RF49, RF50, RF51 · **Reglas**: RN30 a RN33 (5 años desde el cierre, CCyC art. 2560)

## Objetivo

Que los casos cerrados o archivados se conserven 5 años y después se eliminen solos, con aviso previo y posibilidad de prórroga, sin perder la trazabilidad.

## Criterios de aceptación

- [x] **CA1 (RF49 CA1)**: una tarea diaria destruye los casos cerrados o archivados cuyo plazo venció, aplicando RN21. Se borran el caso, las imágenes, los análisis y los informes.
- [x] **CA2 (RF49 CA2)**: la destrucción queda en la auditoría con el número del caso y las huellas SHA-256 de los archivos destruidos.
- [x] **CA3 (RF50 CA1)**: cuando faltan 30 días, el Responsable recibe un correo una sola vez y el caso aparece destacado en su panel, en «Por vencer».
- [x] **CA4 (RF51 CA1)**: el Responsable prorroga 1 año un caso cerrado o archivado indicando el motivo. La nueva fecha y el motivo quedan en la auditoría.
- [x] **CA5 (RF51 CA2)**: una prórroga sin motivo se rechaza.
- [x] **CA6 (RN30)**: un caso reabierto no se destruye: reabrir detiene el plazo.
