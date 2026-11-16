---
description: Cierra una etapa de trabajo con toda la documentación obligatoria del arnés (bitácora, tareas, insumos, Trello) y deja la rama lista para el Pull Request.
---

Instrucciones (aplican la sección «Documentación obligatoria al cerrar una etapa» de `CLAUDE.md`):

1. **Calidad**: corré la calidad mínima de `CLAUDE.md` (backend y frontend, según lo que se tocó). Si algo falla, no cierres: corregí primero.
2. **Bitácora**: creá `docs/bitacora/AAAA-MM-DD-<tema>.md` con qué se hizo, las decisiones y su justificación, cómo se probó y qué queda pendiente.
3. **Seguimiento**: marcá las tareas en `tareas.md`, los criterios en `especificacion.md` y el estado en `docs/funcionalidades/README.md`.
4. **Decisiones**: si hubo una decisión de arquitectura, escribí el ADR. Si hubo una decisión de la autora o pendiente de ella, actualizá `docs/especificacion/06-cuestiones-abiertas.md`.
5. **Informe final**: agregá a `docs/informe-final/insumos.md` todo hallazgo, problema o decisión que deba quedar en el informe.
6. **Arnés**: si en la etapa se cambió una regla, un comando, un gancho o un control, registralo en `docs/arnes/registro-de-cambios.md` con el motivo. Después corré `python3 .claude/hooks/verificar_arnes.py --actualizar`: actualiza los números del mapa del arnés y no se cierra con errores (enlaces rotos, índices o tablas desactualizados). Si en la etapa algo falló dos veces por la misma causa, proponé el control que lo evite (ver `/revisar-arnes`).
7. **Trello**: mové las tarjetas afectadas y agregá las que falten, según `docs/guias/tablero-trello.md`.
8. **Entrega**: compactá la rama en un commit por funcionalidad con `infraestructura/scripts/compactar_rama.sh <archivo-con-el-mensaje> --subir` (rebasa sobre `desarrollo`; la integración continua rechaza merges y más de 3 commits). Avisale a la autora en qué rama está el trabajo y el título y la descripción del Pull Request; si ya hay uno abierto para la rama, decile que se actualizó ese y no pidas otro. Recordale borrar la rama al integrar. **No propongas pasar `desarrollo` a `main`** salvo que se haya completado un hito de `docs/versiones.md` o sea una corrección urgente de producción.
