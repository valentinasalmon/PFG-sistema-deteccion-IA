# ADR-0001: Monorepositorio

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RNF17, RNF20

## Contexto

El sistema tiene cuatro partes con tecnologías distintas: backend (Python/Flask), frontend (React), red neuronal (PyTorch) e infraestructura (Terraform). Lo desarrolla una sola persona y debe evaluarse como un todo.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Un repositorio por parte | Historiales y permisos independientes | Cambios que cruzan partes requieren varios commits coordinados; cuatro integraciones continuas |
| **Monorepositorio** | Un historial, una especificación, una integración continua; cambios atómicos entre partes | La integración continua debe distinguir qué parte cambió |

## Decisión

Un único repositorio con las carpetas `backend/`, `frontend/`, `red_neuronal/` e `infraestructura/`, y la documentación común en `docs/`.

## Consecuencias

- La especificación y la trazabilidad viven junto al código que las realiza.
- La integración continua se organiza en trabajos por carpeta.
- Los datos y modelos pesados de la red neuronal se excluyen de Git.
