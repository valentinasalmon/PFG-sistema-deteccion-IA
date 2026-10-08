# Sistema de detección de imágenes manipuladas o generadas por IA

Proyecto final de grado de Ingeniería en Sistemas de Información.

Plataforma web de **apoyo a la decisión** para abogados y aseguradoras que realiza una evaluación preliminar de imágenes aportadas como prueba en siniestros automovilísticos y laborales. Cada imagen pasa por cuatro capas de análisis independientes y el resultado se entrega como un informe PDF explicativo. **El sistema no emite veredictos**: presenta indicios y recomienda siempre la consulta con un profesional especializado.

## Capas de análisis

| Capa | Técnica | Herramientas |
|---|---|---|
| 1 | Metadatos EXIF / XMP | ExifTool, Pillow |
| 2 | Credenciales de contenido C2PA | c2pa-python y lista de confianza del consorcio |
| 3 | Análisis de niveles de error (ELA) por bloques | Pillow, NumPy |
| 4 | Clasificador de redes neuronales convolucionales | PyTorch (entrenamiento), ONNX Runtime (producción) |

## Tecnologías

- **Backend**: Python, Flask 3.1, Flask-SQLAlchemy, PostgreSQL, Flask-Login, bcrypt, itsdangerous, RQ + Redis.
- **Frontend**: React con Vite.
- **Infraestructura**: AWS (región Irlanda): EC2, S3, SES; Nginx, Gunicorn, TLS; Terraform.
- **Calidad**: pytest, coverage.py, flake8, pylint, ESLint, Vitest, GitHub Actions, Conventional Commits en español.

## Estructura del repositorio

```
.
├── backend/          API REST en Flask (capas Rutas → Servicios → Repositorios → Modelos)
├── frontend/         Interfaz web en React
├── red_neuronal/     Entrenamiento y exportación del clasificador (capa 4)
├── infraestructura/  Terraform, Nginx, systemd y scripts de operación
├── docs/             Especificación, arquitectura, guías y bitácora
├── .github/          Integración continua
└── .claude/          Arnés para el trabajo asistido por IA (comandos y skills)
```

El detalle de cada carpeta está en [docs/arquitectura/estructura-del-repositorio.md](docs/arquitectura/estructura-del-repositorio.md).

## Documentación

| Documento | Para qué sirve |
|---|---|
| [docs/constitucion.md](docs/constitucion.md) | Principios no negociables del proyecto |
| [docs/especificacion/](docs/especificacion/) | Requisitos, reglas de negocio y casos de uso |
| [docs/funcionalidades/](docs/funcionalidades/) | Especificación, plan y tareas de cada funcionalidad |
| [docs/arquitectura/decisiones/](docs/arquitectura/decisiones/) | Registros de decisiones de arquitectura (ADR) |
| [docs/guias/flujo-de-trabajo.md](docs/guias/flujo-de-trabajo.md) | Ramas, commits, desarrollo guiado por especificaciones |
| [docs/bitacora/](docs/bitacora/) | Registro cronológico de lo realizado en cada etapa |

## Estado

En construcción. Ver la [bitácora](docs/bitacora/) para el avance.
