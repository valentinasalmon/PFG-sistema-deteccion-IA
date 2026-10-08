# 2026-10-08 — Hoja de ruta y entorno de desarrollo

## Qué se hizo

1. Se definió la estrategia de desarrollo y la hoja de ruta completa hasta la versión final ([hoja de ruta](../guias/hoja-de-ruta.md)).
2. Se redactó la guía de instalación del entorno en Windows ([guía](../guias/instalacion-entorno-windows.md)).
3. Se reordenaron las funcionalidades para obtener antes un flujo completo y se agregó la funcionalidad 018 de cierre.
4. Se detectó que el repositorio remoto no tenía rama `main` (solo existía la rama de trabajo del asistente); se incluyeron los pasos para crearla.

## Decisiones tomadas

- **Desarrollo por funcionalidades verticales** sobre un esqueleto caminante, en lugar de desarrollar todo el backend y luego todo el frontend. Motivo: siempre hay una versión demostrable y los errores de integración aparecen temprano.
- **Red neuronal en pista paralela**, por ser un trabajo independiente y de larga duración.
- **Desarrollo en WSL2 con Ubuntu** ([ADR-0009](../arquitectura/decisiones/0009-desarrollo-en-wsl2.md)): Gunicorn, RQ y WeasyPrint no funcionan de forma nativa en Windows y producción es Linux.
- **Cuatro hitos**: v0.1 (primer flujo completo), v0.2 (cuatro capas y colaboración), v0.3 (publicado en AWS) y v1.0 (entrega final).

## Tecnologías incorporadas

| Herramienta | Para qué |
|---|---|
| WSL2 + Ubuntu 24.04 | Sistema operativo de desarrollo, igual al de producción |
| Docker Desktop | Servicios de desarrollo en contenedores |
| nvm + Node.js LTS | Herramientas del frontend |
| GitHub CLI (`gh`) | Autenticación y Pull Requests desde la terminal |
| ExifTool (paquete de Ubuntu) | Reemplaza al `exiftool.exe` versionado en TIF |

## Pendientes

- Fase 0: que la autora instale el entorno y cree las ramas `main` y `desarrollo`.
- Fase 1: funcionalidad 001, esqueleto caminante.
