# Especificación: 036 — Arnés para el trabajo asistido por IA

- **Rama**: `funcionalidad/036-arnes`
- **Estado**: Implementada
- **Requisitos que realiza**: RNF02 (protección de secretos), RNF17 (calidad del código), RNF19 (documentación)
- **Reglas de negocio aplicadas**: —
- **Casos de uso**: — (funcionalidad del proceso de desarrollo, no del producto)

## Problema

La autora desarrolla la plataforma con un agente de IA que escribe la mayor parte del código. Las reglas del proyecto estaban escritas, pero algunas dependían de la memoria del agente (no tocar secretos), los errores de estilo se detectaban tarde, los comandos del flujo describían un reparto del trabajo ya reemplazado y no había una vista del arnés como sistema ni de cómo fue evolucionando. Además, la cátedra pidió exponer la parte de *harness engineering* del proyecto.

## Alcance

### Incluido
- Ganchos de Claude Code versionados: protección de secretos (antes de actuar) y revisión de estilo (después de editar).
- Comando `/cerrar-etapa` y actualización de `/especificar`, `/planificar` y `/tareas` al reparto vigente.
- Mapa del arnés y registro de cambios en `docs/arnes/`, ADR-0021 y referencias en `CLAUDE.md`.
- Regla nueva sobre integraciones externas probadas contra el servicio real.

### Excluido
- Cambios en el producto (backend, frontend o infraestructura).
- Ganchos que corran las pruebas completas en cada edición (demasiado lentos; quedan en la integración continua).

## Criterios de aceptación

- [x] **CA1**: El arnés está documentado como sistema (guías, sensores, memoria, persona en el circuito y mejora continua), con un diagrama y la ubicación de cada pieza.
- [x] **CA2**: Si el agente intenta leer, editar o usar en un comando `.env`, `terraform.tfvars`, `backend.hcl`, el estado de Terraform o una clave, la acción se bloquea y el agente recibe el motivo; los archivos de ejemplo y los mensajes de commit que solo los nombran no se bloquean.
- [x] **CA3**: Al editar un archivo Python del backend o JavaScript del frontend con errores de estilo, el agente recibe los errores en el momento; si la herramienta no está instalada, no se interrumpe el trabajo.
- [x] **CA4**: Los comandos del flujo describen el reparto del trabajo vigente y existe `/cerrar-etapa` con los pasos de cierre.
- [x] **CA5**: Cada cambio del arnés queda en un registro con su fecha y el problema que lo motivó, reconstruido desde el inicio del proyecto.
- [x] **CA6**: Los ganchos tienen pruebas automáticas que cubren los casos de bloqueo y de paso.

## Preguntas abiertas

- Ninguna.
