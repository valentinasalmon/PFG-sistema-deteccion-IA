# 2026-11-02 — Funcionalidad 036: arnés para el trabajo asistido por IA

## Contexto

La cátedra pidió que cada estudiante exponga la parte de *harness engineering* de su proyecto. Al revisarla con la autora quedó claro que el proyecto tenía un arnés (reglas, flujo guiado por especificaciones, controles y memoria), pero disperso, con reglas que eran solo texto y con comandos desactualizados. La autora pidió armar un arnés válido con todo lo que había.

## Qué se hizo

- **Gancho de secretos** (`.claude/hooks/proteger_secretos.py`, antes de cada acción del agente): bloquea leer, editar o usar en un comando `.env`, `terraform.tfvars`, `backend.hcl`, el estado de Terraform y claves; permite los archivos de ejemplo y los mensajes de commit. Al activarlo, **bloqueó un comando del propio agente** que creaba un `.env` de prueba: es la evidencia de que funciona.
- **Gancho de estilo** (`revisar_estilo.py`, después de cada edición): flake8 o ESLint sobre el archivo editado; los errores vuelven al agente en el momento.
- **Pruebas de los ganchos** (8, con `unittest`) y un paso nuevo en la integración continua.
- **Comandos**: `/especificar`, `/planificar` y `/tareas` alineados al reparto vigente desde el 2026-10-16 (todavía decían que la autora creaba los archivos); `/cerrar-etapa` nuevo.
- **Documentación**: `docs/arnes/README.md` (mapa con diagrama: guías, sensores, memoria, persona en el circuito, mejora continua, números y límites), `docs/arnes/registro-de-cambios.md` (historia del arnés desde el 2026-10-08, reconstruida desde git y la bitácora) y ADR-0021.
- **`CLAUDE.md`**: referencia al arnés, regla de no evadir un bloqueo de gancho, regla nueva de integraciones externas probadas contra el servicio real y registro obligatorio de cambios del arnés.

## Decisiones

- Ganchos en Python de la biblioteca estándar, porque `python3` está en todas las máquinas donde corre el agente y no hace falta `jq`.
- El gancho de estilo no bloquea si la herramienta no está instalada: el control definitivo sigue siendo la integración continua.
- Regla nueva motivada por el caso del sello en Hedera: pasó todas las pruebas automáticas, pero en producción el PDF salía con el sello pendiente.

## Pruebas

- 8 pruebas de los ganchos en verde; flake8 sobre los ganchos sin errores.
- Prueba en vivo: el gancho de secretos bloqueó un comando del agente en esta misma sesión.

## El arnés en acción (mismo día)

1. Al commitear esta funcionalidad, el gancho de secretos **bloqueó el commit del propio agente**: el mensaje nombraba un archivo secreto. Es un falso positivo: la excepción para mensajes de commit no cubría comandos encadenados ni heredocs.
2. El agente intentó corregir el gancho y **el control de permisos de Claude Code se lo impidió** por ser auto-modificación de un control de seguridad.
3. El agente no buscó la vuelta. Commiteó con un mensaje que no nombra esos archivos y dejó la corrección escrita en `docs/arnes/propuesta-ajuste-gancho-secretos.md` para que la apruebe la autora.

Esto muestra las tres capas del arnés trabajando juntas: el sensor que bloquea, la protección del propio sensor y la persona en el circuito que decide.

## Pendiente

- Que la autora apruebe o rechace el ajuste del gancho de secretos.
- Exponer el arnés en clase (el miércoles), con el mapa de `docs/arnes/README.md` y el registro de cambios.
