# 2026-10-09 — Fase 0: entorno de desarrollo instalado

## Qué se hizo

1. Se crearon las ramas `main` (por defecto) y `desarrollo` en GitHub a partir de la rama de trabajo del asistente, que era la única existente.
2. Se instaló WSL2 con Ubuntu 24.04, VS Code con sus extensiones y Docker Desktop.
3. Se escribió y probó el script `infraestructura/scripts/preparar_entorno_wsl.sh`, que automatiza los pasos 5 a 7 de la guía de instalación (paquetes, grupo `docker`, Node.js, Git y verificación). La autora lo ejecutó con éxito.
4. Se autenticó la CLI de GitHub (`gh auth login`) y se clonó el repositorio en `~/proyectos/PFG-sistema-deteccion-IA` dentro de Ubuntu.

## Versiones instaladas

| Herramienta | Versión |
|---|---|
| Ubuntu (WSL2) | 24.04 |
| Python | 3.12.3 |
| Node.js / npm | 24.21.0 / 11.19.0 |
| Git | 2.43.0 |
| ExifTool | 12.76 |
| Cliente PostgreSQL | 16.15 |
| GitHub CLI | 2.45.0 |
| Docker | 29.8.2 |

## Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| El repositorio clonado no mostraba archivos | VS Code no tenía ninguna carpeta abierta | Abrir la carpeta con `code .` |
| No existía la rama `main` | Solo existía la rama del asistente | `git switch -c main origin/claude/...` y `git push -u origin main` |
| `permission denied ... docker.sock` | Usuario fuera del grupo `docker` | `sudo usermod -aG docker $USER` (incluido luego en el script) |
| Caracteres `^[[200~` al pegar comandos | Pegado entre corchetes de la terminal | Pegar con clic derecho o `Ctrl+Shift+V` |
| Comandos de Ubuntu ejecutados en PowerShell | Confusión entre terminales | Identificar la terminal por el inicio de la línea (`PS C:\` frente a `usuario@equipo:~$`) |
| `execvpe(/bin/bash) failed` desde PowerShell | La distribución WSL por defecto era la interna de Docker | `wsl --set-default Ubuntu-24.04` |

Todos quedaron documentados en la tabla de problemas frecuentes de la [guía de instalación](../guias/instalacion-entorno-windows.md).

## Pendientes

- Funcionalidad 001: esqueleto caminante.
