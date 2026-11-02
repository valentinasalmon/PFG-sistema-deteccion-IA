# Plan técnico: 036 — Arnés para el trabajo asistido por IA

## Piezas

| Pieza | Archivo | Tipo |
|---|---|---|
| Configuración de ganchos | `.claude/settings.json` | Configuración del proyecto de Claude Code (se versiona) |
| Protección de secretos | `.claude/hooks/proteger_secretos.py` | `PreToolUse` sobre Read, Edit, Write, NotebookEdit, Grep, Glob y Bash |
| Revisión de estilo | `.claude/hooks/revisar_estilo.py` | `PostToolUse` sobre Edit y Write |
| Pruebas de los ganchos | `.claude/hooks/pruebas_ganchos.py` | `unittest` de la biblioteca estándar, sin dependencias |
| Comandos | `.claude/commands/*.md` | Texto para el agente |
| Documentación | `docs/arnes/`, ADR-0021, `CLAUDE.md` | Guías y memoria |

## Decisiones técnicas

- **Python de la biblioteca estándar**: `python3` está en la máquina de la autora (WSL), en la nube y en la integración continua; no hace falta instalar nada. No se usa `jq`, que puede no estar.
- **Contrato de Claude Code**: el gancho recibe el pedido como JSON por la entrada estándar (`tool_name`, `tool_input`, y en `PostToolUse` también `tool_response`). Código de salida 2 = bloquear (en `PreToolUse`) o devolver el texto de la salida de error al agente (en `PostToolUse`); 0 = seguir.
- **Ruta de los scripts** con `$CLAUDE_PROJECT_DIR`, para que funcionen desde cualquier carpeta.
- **Secretos por nombre de archivo**, con excepción de los sufijos de ejemplo. En comandos, el nombre tiene que aparecer como argumento suelto; se excluyen los mensajes de `git commit`.
- **Estilo**: flake8 desde `backend/` (toma su configuración) y ESLint desde `frontend/`; primero las herramientas del proyecto (`.venv`, `node_modules`) y si no, las del sistema.
- **Pruebas en la integración continua**: un paso en el trabajo del backend corre `python -m unittest` sobre las pruebas de los ganchos.

## Riesgos

- Falsos positivos del gancho de secretos (un comando que nombra `.env` sin abrirlo): se ajusta el patrón y se registra en el registro de cambios.
- Que la herramienta de estilo tarde mucho: tiempo máximo de 60 s, y si se pasa, no bloquea.
