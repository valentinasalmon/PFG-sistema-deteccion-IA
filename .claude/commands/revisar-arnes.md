---
description: Revisa que el arnés funcione como declara, pone al día su documentación y propone al menos una mejora concreta.
---

Instrucciones (pedido de la autora, 2026-11-05: «el arnés debe trabajar todo el tiempo, mejorarse día a día y distribuir la información de manera adecuada»). Se corre al menos una vez por semana, al empezar una sesión larga y cuando el aviso de inicio de sesión muestra problemas.

1. **Lo declarado frente a lo real**: corré `python3 .claude/hooks/verificar_arnes.py --actualizar`. Corregí todos los errores (enlaces rotos, comandos, ganchos, skills, funcionalidades, bitácora o ADR fuera de su índice) y atendé los avisos. Si el clon no tiene todo el historial, primero `git fetch --unshallow origin`.
2. **Los controles funcionan**: corré la calidad mínima de `CLAUDE.md` (backend y frontend) y las pruebas de los ganchos (`python3 -m unittest discover -s .claude/hooks -p "pruebas_*.py"`). Un control que no se pudo ejecutar se informa como **no verificado**, nunca como correcto.
3. **Estados al día**: compará la tabla de `docs/funcionalidades/README.md`, las casillas de cada `tareas.md` y las ramas sin integrar (`git branch -r --no-merged origin/desarrollo`). Corregí los estados que no coincidan con la realidad.
4. **Lo que espera a la autora**: listá las propuestas del arnés pendientes (`docs/arnes/propuesta-*.md`) y las cuestiones abiertas sin resolver de `docs/especificacion/06-cuestiones-abiertas.md`. No se resuelven por ella: se le recuerdan.
5. **Mejora**: revisá la bitácora y el registro desde la última revisión. Por cada problema que se repitió, o que un control podría haber evitado, proponé una regla, un comando, un gancho o un control. Si es chico y no debilita ningún control, implementalo con sus pruebas; si cambia un control existente o es grande, dejalo como propuesta en `docs/arnes/` para la autora.
6. **Distribución**: anotá cada cambio en `docs/arnes/registro-de-cambios.md`, actualizá el mapa `docs/arnes/README.md` si cambió alguna pieza, la bitácora, `docs/informe-final/insumos.md` si hay un hallazgo para el informe y el tablero de Trello.
7. **Informe a la autora**: qué se verificó y cómo, qué estaba desactualizado y se corrigió, qué no se pudo verificar, qué espera su decisión y qué mejora se hizo o se propone.
