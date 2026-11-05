# 2026-11-05 — Funcionalidad 039: orden del repositorio y del flujo de integración

## Qué se hizo

La autora preguntó si no había demasiados commits y Pull Requests, y pidió limpiar las ramas en desuso, unir las tandas de diseño y mejorar la organización y el README, con criterio de ingeniería. Se midió primero y se cambió después.

- **Diagnóstico** sobre `desarrollo`: 353 commits en 18 días con actividad, 135 (38 %) solo de documentación, 73 Pull Requests con una mediana de 3 commits, 8 de ellos tandas de diseño de una misma funcionalidad, 18 merges «traer desarrollo», 62 ramas en el remoto (51 integradas) y una sola etiqueta para 14 pasos a producción.
- **Política** de ramas, commits, Pull Requests y versiones en `docs/guias/flujo-de-trabajo.md`, `CLAUDE.md`, `/especificar` y `/cerrar-etapa`.
- **`infraestructura/scripts/limpiar_ramas.sh`**: clasifica cada rama (integrada, superada, con contenido propio, activa) y borra las que sobran; por defecto solo simula.
- **Aviso nuevo del verificador** cuando hay ramas integradas sin borrar, con 2 pruebas.
- **Diseño unificado**: historial de las cinco tandas de la 034 en su especificación, línea completa del diseño (022, 028, 033, 034, 037) en la tabla de funcionalidades, y estados corregidos.
- **README principal** reescrito.
- **Propuesta** de configuración de GitHub en `docs/arnes/propuesta-flujo-de-integracion.md`.

## Decisiones tomadas

- **El problema no es la cantidad de commits** (commits chicos facilitan revisar y revertir), sino la cantidad de Pull Requests, que son revisiones de la autora, y las ramas olvidadas, que confunden a la sesión siguiente.
- **No se reescribe historia compartida**: las tandas ya integradas se unifican en la documentación.
- **El README no lleva números**: enlaza al mapa del arnés, donde los calcula el verificador.
- **Ramas conservadas**: `main`, `desarrollo`, las de trabajo en curso (010, 018, 037) y las de otras sesiones activas. El script decide por actividad: un día si la rama está integrada, tres si no.
- **La 038 y la 039 van en la misma rama de la sesión**, para que sean un solo Pull Request.

## Problemas encontrados y cómo se resolvieron

- **El remoto rechaza (403) borrar ramas o subir etiquetas desde la sesión del agente**: solo puede subir a su propia rama. No se buscó otra vía: el script queda listo para la autora y probado en simulación (52 ramas para borrar, 2 para archivar).
- **`recursos/marca-evidentia` figuraba con contenido propio** aunque sus logos son idénticos a los de `desarrollo` (se agregaron en otro commit): el script compara además los archivos que cambió la rama.
- **Estados contradictorios**: la 028 decía «la segunda tanda espera validación» (estaba validada e integrada en el #47) y la 034, «Aprobada» y «cuatro tandas» (eran cinco, todas integradas).
- **Declaraciones de la guía que no se cumplían**: «se elimina la rama» y las versiones etiquetadas. Ahora tienen un script, un aviso y una propuesta.

## Cómo se probó

- Verificador: 21 pruebas correctas (8 de los ganchos, 13 del verificador); flake8 sin errores y pylint 10/10.
- `limpiar_ramas.sh`: shellcheck sin avisos; simulación sobre el remoto real.
- Verificador sobre el repositorio: sin errores.

## Pendientes

- **Autora**: correr `infraestructura/scripts/limpiar_ramas.sh --aplicar --archivar` desde su máquina y decidir la propuesta de configuración de GitHub (borrado automático de ramas, *squash*, etiquetas por versión).
- **Autora**: etiquetar el próximo paso a `main` como `v0.2`.
