# Plan técnico: 039 — Orden del repositorio y del flujo de integración

## Piezas

| Pieza | Archivo | Tipo |
|---|---|---|
| Política de ramas, commits, Pull Requests y versiones | `docs/guias/flujo-de-trabajo.md`, `CLAUDE.md`, `/especificar`, `/cerrar-etapa` | Guía y reglas |
| Limpieza de ramas | `infraestructura/scripts/limpiar_ramas.sh` | Script de bash (shellcheck en la integración continua) |
| Control de ramas integradas sin borrar | `.claude/hooks/verificar_arnes.py` (`revisar_ramas`) y sus pruebas | Aviso al iniciar cada sesión |
| Configuración de GitHub | `docs/arnes/propuesta-flujo-de-integracion.md` | Propuesta para la autora |
| Historial del diseño | `docs/funcionalidades/README.md` (sección «Diseño de la interfaz»), especificaciones de la 028 y la 034 | Documentación |
| README principal | `README.md` | Documentación |

## Decisiones técnicas

- **Medir antes de cambiar.** El diagnóstico (commits por día, commits solo de documentación, Pull Requests por funcionalidad, merges de sincronización, ramas integradas, etiquetas) sale de `git log` sobre `desarrollo`; está en la especificación.
- **No se busca tener menos commits, sino menos Pull Requests y ninguna rama olvidada.** Los commits chicos facilitan revisar y revertir; el costo está en cada revisión de la autora y en las ramas que confunden a la sesión siguiente.
- **No se reescribe historia compartida.** Las tandas ya integradas se unifican en la documentación, no en git.
- **Clasificación de ramas** en el script: integrada (`rev-list` vacío), superada (`git cherry` sin cambios propios, o los archivos que tocó ya iguales en `desarrollo`), con contenido propio (se archiva en una etiqueta antes de borrarla) y activa (actividad en el último día si está integrada, en los últimos tres si no). Por defecto solo simula.
- **El README no lleva números**: enlaza al mapa del arnés, donde los calcula el verificador. Un número escrito a mano en el README sería otra declaración que se desactualiza.
- **Squash, borrado automático y etiquetas automáticas** cambian la configuración de GitHub o el camino de producción, y el *squash* cambia las métricas del informe: quedan como propuesta.

## Riesgos

- **Borrar una rama en uso por otra sesión**: el script conserva las ramas con actividad reciente y acepta una lista `CONSERVAR`; una rama borrada por error se restaura desde su Pull Request o desde la etiqueta de archivo.
- **La sesión del agente no puede borrar ramas ajenas** (403): la limpieza la corre la autora con el script.
