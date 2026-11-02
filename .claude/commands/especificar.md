---
description: Crea la especificación de una funcionalidad (docs/funcionalidades/NNN-nombre/especificacion.md) a partir de una descripción.
---

Instrucciones (reparto del trabajo vigente desde el 2026-10-16: el agente escribe y sube; la autora revisa e integra):

1. Leé `docs/constitucion.md`, la especificación general en `docs/especificacion/` y el mapa del arnés en `docs/arnes/README.md`.
2. A partir de la descripción de `$ARGUMENTS`, identificá los requisitos (RF, RNF), reglas (RN) y casos de uso (CU) que cubre. Si la funcionalidad figura en la tabla de `docs/funcionalidades/README.md`, usá ese número y nombre; si no, tomá el siguiente número libre y agregala a la tabla.
3. Creá la rama `funcionalidad/NNN-nombre` desde `desarrollo`.
4. Redactá `docs/funcionalidades/NNN-nombre/especificacion.md` a partir de `docs/funcionalidades/plantillas/especificacion.md`, **sin detalles de implementación** y con criterios de aceptación verificables.
5. Lo que puedas resolver con la especificación y la constitución, decidilo y registralo. Lo que sea una decisión de la autora (alcance, legal, privacidad, arquitectura de gran impacto, lo que validan los tutores) va a `docs/especificacion/06-cuestiones-abiertas.md` con una propuesta provisoria.
6. Commit: `documentacion(NNN): agregar especificacion de ...`. Seguí con `/planificar`.
