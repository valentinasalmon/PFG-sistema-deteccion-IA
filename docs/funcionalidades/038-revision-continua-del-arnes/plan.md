# Plan técnico: 038 — Revisión continua del arnés

## Piezas

| Pieza | Archivo | Tipo |
|---|---|---|
| Verificador | `.claude/hooks/verificar_arnes.py` | Script de Python de la biblioteca estándar |
| Pruebas del verificador | `.claude/hooks/pruebas_verificar_arnes.py` | `unittest`, sobre un repositorio mínimo temporal |
| Gancho de inicio de sesión | `.claude/settings.json` (`SessionStart`) | Corre `verificar_arnes.py --sesion` |
| Integración continua | `.github/workflows/integracion-continua.yml` | Paso «Documentación del arnés al día (038)» en el trabajo del backend |
| Comandos | `.claude/commands/revisar-arnes.md` (nuevo) y `cerrar-etapa.md` | Texto para el agente |
| Reglas | `CLAUDE.md` | Sección «El arnés se revisa solo y mejora siempre» |

## Decisiones técnicas

- **Errores y avisos.** Lo que hace falso un documento de forma objetiva (un enlace o un índice) es error y frena la integración. Lo que depende del momento (los números, un cambio todavía sin registrar) es aviso: no tiene sentido frenar un Pull Request porque los números del mapa cambiaron con el propio Pull Request.
- **Los números se calculan, no se escriben a mano.** `--actualizar` reescribe la tabla del mapa del arnés desde el repositorio. La fila de pruebas cuenta las funciones de prueba escritas (`def test_` en el backend, `it(` y `test(` en el frontend), no las ejecutadas: se puede calcular sin instalar nada. Por eso se llama «Pruebas automáticas escritas».
- **Historial completo.** Los números solo se calculan si ninguna raíz de la historia de `HEAD` es un corte del clon. En la integración continua el clon tiene un solo commit y esos controles se omiten; en un clon parcial pero que llega al primer commit, se calculan.
- **El inicio de sesión nunca bloquea.** El modo `--sesion` imprime un resumen (que Claude Code agrega al contexto del agente) y sale con 0.
- **Dónde vive.** En `.claude/hooks/`, junto a los otros controles del arnés, para que el paso existente de la integración continua corra también sus pruebas (`pruebas_*.py`).

## Riesgos

- **Avisos que se ignoran.** Mitigación: `/cerrar-etapa` corre `--actualizar` y no cierra con errores, y `CLAUDE.md` pide atender el aviso de inicio de sesión.
- **Falsos positivos de enlaces** en documentos con ejemplos. Mitigación: se ignoran los bloques de código y las URL con esquema.
