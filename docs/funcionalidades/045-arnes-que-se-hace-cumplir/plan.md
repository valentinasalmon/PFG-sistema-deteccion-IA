# Plan técnico: 045 — Un arnés que se hace cumplir

## Etapa 1 — Revisión continua del arnés

### Piezas

| Pieza | Archivo | Tipo |
|---|---|---|
| Verificador | `.claude/hooks/verificar_arnes.py` | Script de Python de la biblioteca estándar |
| Pruebas del verificador | `.claude/hooks/pruebas_verificar_arnes.py` | `unittest`, sobre un repositorio mínimo temporal |
| Gancho de inicio de sesión | `.claude/settings.json` (`SessionStart`) | Corre `verificar_arnes.py --sesion` |
| Integración continua | `.github/workflows/integracion-continua.yml` | Paso «Documentación del arnés al día (045)» en el trabajo del backend |
| Comandos | `.claude/commands/revisar-arnes.md` (nuevo) y `cerrar-etapa.md` | Texto para el agente |
| Reglas | `CLAUDE.md` | Sección «El arnés se revisa solo y mejora siempre» |

### Decisiones técnicas

- **Errores y avisos.** Lo que hace falso un documento de forma objetiva (un enlace o un índice) es error y frena la integración. Lo que depende del momento (los números, un cambio todavía sin registrar) es aviso: no tiene sentido frenar un Pull Request porque los números del mapa cambiaron con el propio Pull Request.
- **Los números se calculan, no se escriben a mano.** `--actualizar` reescribe la tabla del mapa del arnés desde el repositorio. La fila de pruebas cuenta las funciones de prueba escritas (`def test_` en el backend, `it(` y `test(` en el frontend), no las ejecutadas: se puede calcular sin instalar nada. Por eso se llama «Pruebas automáticas escritas».
- **Historial completo.** Los números solo se calculan si ninguna raíz de la historia de `HEAD` es un corte del clon. En la integración continua el clon tiene un solo commit y esos controles se omiten; en un clon parcial pero que llega al primer commit, se calculan.
- **El inicio de sesión nunca bloquea.** El modo `--sesion` imprime un resumen (que Claude Code agrega al contexto del agente) y sale con 0.
- **Dónde vive.** En `.claude/hooks/`, junto a los otros controles del arnés, para que el paso existente de la integración continua corra también sus pruebas (`pruebas_*.py`).

### Riesgos

- **Avisos que se ignoran.** Mitigación: `/cerrar-etapa` corre `--actualizar` y no cierra con errores, y `CLAUDE.md` pide atender el aviso de inicio de sesión.
- **Falsos positivos de enlaces** en documentos con ejemplos. Mitigación: se ignoran los bloques de código y las URL con esquema.

## Etapa 2 — Orden del repositorio y del flujo de integración

### Piezas

| Pieza | Archivo | Tipo |
|---|---|---|
| Política de ramas, commits, Pull Requests y versiones | `docs/guias/flujo-de-trabajo.md`, `CLAUDE.md`, `/especificar`, `/cerrar-etapa` | Guía y reglas |
| Limpieza de ramas | `infraestructura/scripts/limpiar_ramas.sh` | Script de bash (shellcheck en la integración continua) |
| Control de ramas integradas sin borrar | `.claude/hooks/verificar_arnes.py` (`revisar_ramas`) y sus pruebas | Aviso al iniciar cada sesión |
| Configuración de GitHub | `docs/arnes/propuesta-flujo-de-integracion.md` | Propuesta para la autora |
| Historial del diseño | `docs/funcionalidades/README.md` (sección «Diseño de la interfaz»), especificaciones de la 028 y la 034 | Documentación |
| README principal | `README.md` | Documentación |

### Decisiones técnicas

- **Medir antes de cambiar.** El diagnóstico (commits por día, commits solo de documentación, Pull Requests por funcionalidad, merges de sincronización, ramas integradas, etiquetas) sale de `git log` sobre `desarrollo`; está en la especificación.
- **No se busca tener menos commits, sino menos Pull Requests y ninguna rama olvidada.** Los commits chicos facilitan revisar y revertir; el costo está en cada revisión de la autora y en las ramas que confunden a la sesión siguiente.
- **No se reescribe historia compartida.** Las tandas ya integradas se unifican en la documentación, no en git.
- **Clasificación de ramas** en el script: integrada (`rev-list` vacío), superada (`git cherry` sin cambios propios, o los archivos que tocó ya iguales en `desarrollo`), con contenido propio (se archiva en una etiqueta antes de borrarla) y activa (actividad en el último día si está integrada, en los últimos tres si no). Por defecto solo simula.
- **El README no lleva números**: enlaza al mapa del arnés, donde los calcula el verificador. Un número escrito a mano en el README sería otra declaración que se desactualiza.
- **Squash, borrado automático y etiquetas automáticas** cambian la configuración de GitHub o el camino de producción, y el *squash* cambia las métricas del informe: quedan como propuesta.

### Riesgos

- **Borrar una rama en uso por otra sesión**: el script conserva las ramas con actividad reciente y acepta una lista `CONSERVAR`; una rama borrada por error se restaura desde su Pull Request o desde la etiqueta de archivo.
- **La sesión del agente no puede borrar ramas ajenas** (403): la limpieza la corre la autora con el script.

## Etapa 3 — Que la política se cumpla sola

### Piezas

| Pieza | Archivo | Tipo |
|---|---|---|
| Forma del Pull Request | `.github/workflows/integracion-continua.yml` (trabajo «commits») | Paso que falla con merges o más de 3 commits hacia `desarrollo` |
| Compactación | `infraestructura/scripts/compactar_rama.sh` | Script de bash (shellcheck en la integración continua) |
| Reglas | `CLAUDE.md`, `/cerrar-etapa`, `docs/guias/flujo-de-trabajo.md` | Texto para el agente |

### Decisiones técnicas

- **El control va en la integración continua, no en un gancho del agente.** Un gancho que frene los `git push` impediría guardar seguido, y la sesión en la nube puede perder lo que no subió. Se guarda seguido en la rama y se compacta antes del Pull Request; la integración continua es la compuerta.
- **Máximo de 3 commits, no 1**: deja lugar a un commit de código, uno de documentación y una corrección pedida en la revisión, sin obligar a reescribir la rama por cada comentario.
- **Merges, ninguno**: sincronizar con `rebase` deja el historial lineal y sin commits de proceso.
- **Solo hacia `desarrollo`**: el paso de `desarrollo` a `main` es por naturaleza una integración de varios cambios.
- **Si la autora habilita *squash*** el límite de commits sobra (cada Pull Request llega como un commit); el de merges se puede mantener.
