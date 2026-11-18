# 2026-11-16 — Funcionalidad 045, etapa 3: que la política se cumpla sola

## Qué se hizo

La autora pidió aplicar el arnés: no abrir Pull Requests para cualquier cosa ni hacer commits por cambios mínimos, y un repositorio más escalable. La política del 2026-11-05 había quedado solo como texto.

- **Diagnóstico** de los Pull Requests #67 a #96 (14 días): 8 pasos a `main`, uno después de cada funcionalidad; 6 Pull Requests de la 010; 4 duplicados o con la base equivocada; 5 merges «incorporar desarrollo».
- **Integración continua**: el paso «Forma del Pull Request» rechaza los Pull Requests hacia `desarrollo` con merges o más de 3 commits. Simulado sobre los reales, habría frenado el #87, el #89 y el #95.
- **`compactar_rama.sh`**: rebasa sobre `desarrollo` y deja la rama en un commit, con las líneas `Co-Authored-By`; probado en un repositorio de prueba (3 commits → 1, contenido y co-autoría conservados).
- **Reglas** en `CLAUDE.md`, `/cerrar-etapa`, `/especificar` y la guía de flujo de trabajo.
- **Control de numeración** en el verificador y **`limpiar_ramas.sh`** más prudente.
- **El trabajo de las etapas 1 y 2 (escritas como 038 y 039) se unificó en la 045** y llega como un solo commit sobre la última versión de `desarrollo`.

## Decisiones tomadas

- **La compuerta es la integración continua, no un gancho del agente**: frenar los `git push` impediría guardar seguido, y la sesión en la nube pierde lo que no subió.
- **Hasta 3 commits por Pull Request**: código, documentación y una corrección de la revisión. Con *squash* habilitado por la autora, este límite sobraría.
- **El paso a `main` por hito** (`docs/versiones.md`) o corrección urgente, alineado con la regla de versiones que ya estaba en `desarrollo`.
- **Número 045**: el 044 lo usa una rama en curso (`funcionalidad/044-portada-y-identidad`).

## Problemas encontrados y cómo se resolvieron

- **Otra vez faltaban 6 entradas en el índice de la bitácora**: el verificador de la etapa 1 todavía no estaba en `desarrollo`, así que nada lo impedía. Se completó el índice.
- **El aviso de numeración daba falsos positivos** con ramas viejas de tandas: ahora compara solo las carpetas nuevas que agrega una rama sin integrar. Encontró un choque real en la rama del informe (`039-arnes-del-informe`).
- **Una sustitución automática de números tocó una guía ajena** (un prompt numerado 044 del conjunto propio): se detectó al revisar `git status` y se revirtió antes de guardar.

## Cómo se probó

- 23 pruebas del arnés correctas; flake8 sin errores y pylint 10/10 en el verificador.
- shellcheck sin avisos en `compactar_rama.sh` y `limpiar_ramas.sh`; YAML de la integración continua válido.
- `compactar_rama.sh` en un repositorio de prueba; `limpiar_ramas.sh` en simulación sobre el remoto real (58 para borrar, 2 abandonadas).
- Verificador sobre el repositorio: sin errores.

## Pendientes

- **Autora**: integrar este Pull Request; correr `limpiar_ramas.sh --aplicar --archivar`; habilitar el borrado automático de ramas y decidir el *squash* (`docs/arnes/propuesta-flujo-de-integracion.md`).
- **Sesión del informe** (`claude/gracious-thompson-9slyyn`): renumerar su `039-arnes-del-informe` antes de integrar.
