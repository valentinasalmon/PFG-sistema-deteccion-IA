# ADR-0021: Arnés para el trabajo asistido por IA, con reglas que se hacen cumplir solas

- **Estado**: Aceptada (pedido de la autora, 2026-11-02)
- **Fecha**: 2026-11-02
- **Requisitos relacionados**: RNF02, RNF17, RNF19; funcionalidad 036

## Contexto

La mayor parte del código la escribe un agente de IA (Claude Code). Desde el inicio el proyecto tuvo reglas escritas (`CLAUDE.md`, constitución), un flujo guiado por especificaciones y controles en git y en la integración continua. Pero:

- algunas reglas importantes eran **solo texto**: «nunca leer ni subir secretos» dependía de que el agente la recordara;
- los errores de estilo se descubrían recién en la integración continua, minutos después y fuera de la sesión;
- los comandos `/especificar`, `/planificar` y `/tareas` seguían describiendo el reparto del trabajo anterior al 2026-10-16;
- no había un documento que mostrara el arnés como sistema ni un registro de por qué cambió cada regla.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Dejar las reglas como texto en `CLAUDE.md` | Nada que mantener | Depende de la memoria del modelo; una sesión larga o resumida puede olvidarlas |
| Reglas de permisos de Claude Code (`permissions.deny`) | Configuración simple | Solo coinciden por ruta y herramienta: no entienden un `cat .env` dentro de un comando ni explican el motivo al agente |
| **Ganchos (*hooks*) de Claude Code con scripts propios, versionados en el repositorio** | Se ejecutan siempre, bloquean antes de la acción, devuelven el motivo al agente, se prueban como cualquier código | Dependen de que `python3` esté en la máquina; hay que mantenerlos |

## Decisión

1. **Ganchos versionados** en `.claude/settings.json` y `.claude/hooks/`:
   - `proteger_secretos.py` (`PreToolUse`): bloquea leer, editar o nombrar en un comando los archivos secretos; permite los de ejemplo.
   - `revisar_estilo.py` (`PostToolUse`): corre flake8 o ESLint sobre el archivo recién editado y le devuelve los errores al agente; si la herramienta no está instalada, no hace nada.
2. **Comando `/cerrar-etapa`**: convierte la «documentación obligatoria al cerrar una etapa» en un procedimiento de pasos verificables.
3. **Comandos del flujo alineados** con el reparto vigente.
4. **Documentación del arnés** en `docs/arnes/`: el mapa (guías, sensores, memoria, persona en el circuito) y el **registro de cambios**, que se completa en cada cierre de etapa.
5. **Regla nueva**: toda integración con un servicio externo se prueba contra el servicio real antes de darla por terminada, y su estado se ve en `/estado`.

## Consecuencias

- La regla de secretos pasa de «el agente debería recordarla» a «no puede violarla»: el gancho bloqueó, al probarlo, un comando del propio agente.
- Los errores de estilo se corrigen en el momento, no en la integración continua.
- Cualquier persona que use Claude Code en el repositorio (la autora en su máquina o un agente en la nube) recibe el mismo arnés.
- Hay que mantener los ganchos: un falso positivo (por ejemplo, un comando que nombra `.env` sin abrirlo) se resuelve ajustando el script y registrándolo.
