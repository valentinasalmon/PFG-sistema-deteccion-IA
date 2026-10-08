# ADR-0009: Entorno de desarrollo en WSL2 con Ubuntu

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RNF22

## Contexto

La autora desarrolla en Windows. Varias herramientas del sistema no funcionan o funcionan con dificultad en Windows:

- **Gunicorn** no corre en Windows.
- **RQ** necesita `fork()`, que Windows no ofrece; su trabajador estándar no funciona.
- **WeasyPrint** requiere las bibliotecas Pango y HarfBuzz, de instalación compleja en Windows.
- **ExifTool** en Windows obligaba a versionar un ejecutable `.exe` en el repositorio (como en TIF).

Además, producción es Linux (Ubuntu en EC2).

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Desarrollar directamente en Windows | Sin capa adicional | Gunicorn, RQ y WeasyPrint no funcionan o requieren alternativas distintas a producción |
| Todo dentro de contenedores Docker | Entorno idéntico a producción | Depuración y recarga más complejas para quien recién empieza |
| **WSL2 con Ubuntu + Docker para servicios** | Mismo sistema operativo que producción; herramientas nativas; VS Code integrado | Requiere instalar WSL2 |

## Decisión

El código se desarrolla y ejecuta dentro de **Ubuntu 24.04 en WSL2**, abierto desde VS Code con la extensión WSL. Los servicios de apoyo (PostgreSQL, Redis, almacenamiento compatible con S3 y servidor de correo de prueba) se ejecutan con Docker Desktop integrado a WSL2.

## Consecuencias

- El entorno de desarrollo es equivalente al de producción, lo que reduce errores de "en mi máquina funciona".
- ExifTool se instala como paquete del sistema; no se versiona ningún ejecutable.
- El repositorio se clona dentro del disco de Ubuntu para obtener buen rendimiento.
- La guía de instalación queda en [docs/guias/instalacion-entorno-windows.md](../../guias/instalacion-entorno-windows.md).
