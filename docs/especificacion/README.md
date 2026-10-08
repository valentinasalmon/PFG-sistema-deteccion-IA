# Especificación del sistema

Esta carpeta contiene la especificación funcional del proyecto final de grado. Es la fuente de verdad del desarrollo guiado por especificaciones: ningún módulo se implementa sin un requisito y un caso de uso que lo respalden, y cada prueba de aceptación se deriva de los criterios definidos aquí.

## Índice

| Documento | Contenido |
|---|---|
| [01-vision-y-alcance.md](01-vision-y-alcance.md) | Propósito, alcance, actores, glosario y modelo de negocio |
| [02-reglas-de-negocio.md](02-reglas-de-negocio.md) | Reglas de negocio (RN) que condicionan a los requisitos |
| [03-requisitos-funcionales.md](03-requisitos-funcionales.md) | Requisitos funcionales (RF) con criterios de aceptación |
| [04-requisitos-no-funcionales.md](04-requisitos-no-funcionales.md) | Requisitos no funcionales (RNF) con criterios de aceptación |
| [05-casos-de-uso.md](05-casos-de-uso.md) | Casos de uso (CU) con flujos principal y alternativos |
| [06-cuestiones-abiertas.md](06-cuestiones-abiertas.md) | Decisiones pendientes y supuestos adoptados |

## Convenciones de redacción

- **Identificadores**: `RN`, `RF`, `RNF` y `CU`, seguidos de dos dígitos. Un identificador nunca se reutiliza; si un requisito se descarta, se marca como **Descartado** y se conserva el número.
- **Prioridad** (MoSCoW): **Debe** (imprescindible para la entrega), **Debería** (importante, negociable), **Podría** (deseable si el tiempo lo permite).
- **Criterios de aceptación**: se redactan con el formato *Dado / Cuando / Entonces*, de modo que puedan traducirse directamente a pruebas automatizadas.
- **Marcas**:
  - **[PROPUESTA]**: valor o comportamiento sugerido por el equipo de desarrollo que aún requiere confirmación.
  - **[A DEFINIR]**: decisión pendiente; ver `06-cuestiones-abiertas.md`.
- **Trazabilidad**: cada caso de uso indica los requisitos que realiza, y cada requisito indica las reglas de negocio que aplica.

## Estado

Versión 0.1 — borrador para validación con la autora del proyecto.
