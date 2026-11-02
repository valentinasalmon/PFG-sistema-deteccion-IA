---
description: Crea el plan técnico (plan.md) de una funcionalidad ya especificada.
---

Instrucciones:

1. Identificá la funcionalidad: el número indicado en `$ARGUMENTS` o la de número más alto con especificación y sin plan.
2. Leé su `especificacion.md`, `docs/constitucion.md`, los ADR de `docs/arquitectura/decisiones/` y el código existente en las capas que se van a tocar.
3. Redactá `plan.md` a partir de `docs/funcionalidades/plantillas/plan.md`: capas afectadas, patrones, contratos, cambios en datos, bibliotecas con su justificación, estrategia de pruebas, excepciones y riesgos.
4. Si el plan requiere una decisión de arquitectura nueva, escribí el ADR en `docs/arquitectura/decisiones/`. Si es de gran impacto, registrala además como cuestión abierta para la autora.
5. Commit: `documentacion(NNN): agregar plan tecnico`. Seguí con `/tareas`.
