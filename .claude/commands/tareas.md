---
description: Genera la lista de tareas ejecutables (tareas.md) a partir del plan técnico y las implementa.
---

Instrucciones:

1. Identificá la funcionalidad: el número indicado en `$ARGUMENTS` o la de número más alto con plan y sin tareas.
2. Leé `especificacion.md` y `plan.md`.
3. Redactá `tareas.md` a partir de `docs/funcionalidades/plantillas/tareas.md`. Cada tarea es chica, verificable por sí misma e indica archivos y commit. Incluí siempre tareas de pruebas, de verificación en el navegador o contra el servicio real, y de documentación.
4. Implementá tarea por tarea, con docstrings que digan qué requisito realiza. Antes de cada commit corré la calidad mínima de `CLAUDE.md` (los ganchos de `.claude/hooks/` ya revisan el estilo de cada archivo que editás).
5. Marcá cada tarea en `tareas.md` y cada criterio cumplido en `especificacion.md`.
6. Al terminar, corré `/cerrar-etapa` y avisale a la autora que la rama está lista para su Pull Request.
