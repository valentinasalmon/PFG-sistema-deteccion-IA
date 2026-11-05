# Especificación: 039 — Orden del repositorio y del flujo de integración

- **Rama**: `claude/charming-turing-j7esco` (rama de la sesión del agente, junto con la 038, para que sea un solo Pull Request)
- **Estado**: Implementada la parte del agente. Esperan a la autora: correr la limpieza de ramas (CA2) y decidir la configuración de GitHub
- **Requisitos que realiza**: RNF17 (calidad del código), RNF19 (documentación)
- **Reglas de negocio aplicadas**: —
- **Casos de uso**: — (funcionalidad del proceso de desarrollo, no del producto)

## Problema

El 2026-11-05 la autora preguntó si no había demasiados commits y Pull Requests, pidió limpiar las ramas en desuso, unir las tandas de diseño, mejorar la organización del repositorio y el README principal, siempre con criterio de ingeniería.

Diagnóstico con datos del 2026-11-05 (sobre `desarrollo`):

| Indicador | Valor | Lectura |
|---|---|---|
| Commits | 353 en 18 días con actividad (~19 por día) | Commits chicos son una buena práctica; la cantidad sola no es el problema |
| Commits solo de documentación | 135 (38 %) | El seguimiento se sube en commits sueltos |
| Pull Requests | 73 (~4 por día), mediana de 3 commits | Cada uno cuesta una revisión de la autora: **este es el costo real** |
| Tandas de diseño en ramas y Pull Requests separados | 8 (5 de la 034, 3 de la 028) | Una funcionalidad partida en varias ramas |
| Merges «traer `desarrollo`» a una rama | 18 | Ruido en el historial |
| Ramas en el remoto | 62, de las cuales 51 ya integradas | La guía decía «se elimina la rama» y no se hacía |
| Pasos a producción (`desarrollo` → `main`) | 14, con una sola etiqueta (`v0.1`) | La guía declara versiones etiquetadas y no se cumple |
| Estados de las funcionalidades de diseño | 028 y 034 con estados distintos en su especificación y en la tabla | Lo declarado no coincide |

## Alcance

### Incluido
- Política escrita de ramas, commits y Pull Requests (una funcionalidad, una rama, un Pull Request; tandas como etapas de la misma rama; seguimiento en el mismo Pull Request; borrar la rama al integrar; versiones etiquetadas).
- Limpieza de las ramas remotas integradas o superadas, con una etiqueta de archivo para las que tenían contenido propio.
- Control nuevo en el verificador del arnés: avisa cuando hay ramas integradas sin borrar.
- Historial unificado del diseño de la interfaz (022, 028, 033, 034 y 037) y estados corregidos.
- README principal al día.
- Propuesta para la autora sobre la configuración de GitHub (integración con *squash*, borrado automático de ramas, etiqueta por versión).

### Excluido
- Reescribir la historia ya integrada (no se reescribe historia compartida).
- Borrar ramas de trabajo en curso (010, 018, 037 y las de otras sesiones activas).
- Cambiar la configuración de GitHub: no hay acceso desde la sesión y es una decisión de la autora.

## Criterios de aceptación

- [x] **CA1**: `docs/guias/flujo-de-trabajo.md` define la política de ramas, commits, Pull Requests y versiones, con su justificación, y los comandos del flujo la aplican.
- [ ] **CA2**: En el remoto no quedan ramas integradas ni superadas, salvo las de trabajo en curso; lo que tenía contenido propio queda en una etiqueta `archivo/…`. *Pendiente: el script está listo y probado en simulación (52 para borrar, 2 para archivar), pero lo corre la autora porque la sesión del agente recibe 403 al borrar ramas ajenas.*
- [x] **CA3**: El verificador del arnés avisa si hay ramas remotas integradas en `desarrollo` sin borrar, con pruebas.
- [x] **CA4**: Las tandas de diseño están en un solo historial, con su Pull Request y su bitácora, y los estados de la 028 y la 034 coinciden en todos los documentos.
- [x] **CA5**: El README principal describe el sistema, el estado, cómo levantarlo y dónde está cada documento, sin datos desactualizados.
- [x] **CA6**: La propuesta de configuración de GitHub está en `docs/arnes/` y el verificador la recuerda.

## Preguntas abiertas

- Integrar con *squash* cambia cómo se cuentan los commits (un commit por funcionalidad en `desarrollo`). Lo decide la autora: ver la propuesta.
