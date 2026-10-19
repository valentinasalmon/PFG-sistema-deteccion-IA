# 2026-10-10 — Funcionalidad 001: esqueleto caminante

## Qué se hizo

Se construyó la versión mínima del sistema que conecta todas sus piezas de punta a punta: interfaz en React, API en Flask, PostgreSQL y Redis, con la integración continua y los controles de calidad automatizados. Documentos: [especificación](../funcionalidades/001-esqueleto-caminante/especificacion.md), [plan](../funcionalidades/001-esqueleto-caminante/plan.md) y [tareas](../funcionalidades/001-esqueleto-caminante/tareas.md).

- **Backend**: fábrica de la aplicación, configuración por entorno, endpoint `GET /api/salud` recorriendo las capas ruta → servicio → repositorio e integración, y migraciones con Alembic.
- **Frontend**: página que consulta la API y muestra el estado de cada servicio.
- **Servicios de desarrollo**: PostgreSQL, Redis y Mailpit con Docker Compose.
- **Calidad**: pytest, coverage.py, flake8, pylint, import-linter, ESLint y Vitest.
- **Proceso**: ganchos de Git con pre-commit y commitlint; integración continua en GitHub Actions con tres trabajos.
- **Editor**: configuración compartida de VS Code en `.vscode/`.

## Verificación de los criterios de aceptación

| Criterio | Cómo se verificó | Resultado |
|---|---|---|
| CA1 Servicios | `docker compose ps` | 3 servicios `healthy` |
| CA2 Salud de la API | `curl` y navegador a `/api/salud` | 200 |
| CA3 Servicio caído | `docker compose stop postgres` | 503 indicando `base_de_datos` |
| CA4 Interfaz conectada | Navegador, con todo funcionando y con Redis detenido | Estado correcto en ambos casos |
| CA5 Interfaz sin API | Navegador con el backend apagado | "No se pudo conectar con la API." |
| CA6 Configuración segura | Prueba automática | La producción sin clave no arranca |
| CA7 Pruebas y cobertura | `pytest` y Vitest | 15 + 4 pruebas; cobertura 100 % |
| CA8 Análisis estático | flake8, pylint y ESLint | Sin errores; pylint 10/10 |
| CA9 Arquitectura | Violación provocada en una ruta | La prueba falla y lo informa |
| CA10 Commits | `feat: algo` frente a `funcionalidad(...)` | Rechazado y aceptado |
| CA11 Integración continua | Pull Request hacia `desarrollo` | Tres trabajos en verde |

## Decisiones tomadas

- **commitlint también en local**, en lugar de `conventional-pre-commit`, que siempre admite `feat` y `fix`. Así hay una única lista de tipos, en `commitlint.config.mjs`.
- **import-linter con importaciones indirectas permitidas**: se prohíbe que una ruta importe un repositorio, pero no el recorrido correcto ruta → servicio → repositorio.
- **`pool_pre_ping` en SQLAlchemy**: cada conexión se verifica antes de usarse, para recuperarse de un reinicio de la base sin errores (RNF16).
- **MinIO quitado de los servicios** y traslado del almacenamiento S3 a la funcionalidad 006 (ver el registro de cambios de la especificación).
- **Configuración compartida de VS Code** versionada en el repositorio, como parte del arnés.

## Tecnologías incorporadas

| Tecnología | Versión | Para qué |
|---|---|---|
| Flask / Flask-SQLAlchemy / Flask-Migrate | 3.1.3 / 3.1.1 / 4.1.0 | API, ORM y migraciones |
| SQLAlchemy / psycopg | 2.0.54 / 3.3.6 | Acceso a PostgreSQL |
| redis | 6.4.0 | Cliente de Redis |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | Pruebas y cobertura |
| flake8 / pylint / import-linter | 7.4.1 / 4.1.2 / 2.15 | Estilo, análisis estático y arquitectura |
| pre-commit / commitlint | 4.6.2 / 21.2.3 | Ganchos de Git y mensajes de commit |
| React / Vite / Vitest | 19.3.0 / 7.3.7 / 4.1.11 | Interfaz, servidor de desarrollo y pruebas |
| ESLint | 10.12.0 | Análisis estático del frontend |
| PostgreSQL / Redis / Mailpit (Docker) | 16 / 7 / última | Servicios de desarrollo |
| GitHub Actions | — | Integración continua |

## Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| Error 500 de Docker Hub al descargar imágenes | Falla temporal del servicio de Docker Hub | Reintentar más tarde |
| `pull access denied for minio/minio` | MinIO dejó de publicar su imagen en Docker Hub | Quitar MinIO y resolver S3 en la funcionalidad 006 |
| 21 avisos `W292 no newline at end of file` | Al pegar el código se perdía el salto de línea final | Corrección automática con `sed` y `files.insertFinalNewline` en VS Code |
| La primera consulta tras reiniciar PostgreSQL informaba la base como caída | Conexiones viejas en el pool de SQLAlchemy | `pool_pre_ping: True` |
| `flask db init` rechazaba la carpeta de migraciones | La carpeta contenía un `.gitkeep` | Borrarlo antes de inicializar y crear `versions/.gitkeep` después |
| El comando "Seleccionar intérprete" no aparecía en VS Code | La extensión de Python no estaba instalada del lado de WSL | Instalar las extensiones en WSL |

## Pendientes

- Funcionalidad 002: cuentas y sesión.
- Elegir y verificar un reemplazo de MinIO en la funcionalidad 006.
