# evidentIA · Detección de imágenes manipuladas o generadas por IA

Proyecto final de grado de Ingeniería en Sistemas de Información.

Plataforma web de **apoyo a la decisión** para abogados y aseguradoras. Hace una evaluación preliminar de las fotos que se aportan como prueba en siniestros automovilísticos y laborales: cada imagen pasa por capas de análisis independientes y el resultado se entrega en un informe PDF explicativo y verificable.

> **El sistema no emite veredictos.** Presenta indicios técnicos y recomienda siempre consultar a un profesional especializado (RN27, [ADR-0017](docs/arquitectura/decisiones/0017-marco-normativo-y-supervision-humana.md)).

## Qué hace

- **Casos y organizaciones**: estudios jurídicos y aseguradoras con sus miembros, roles, permisos y auditoría de cada acción.
- **Carga de imágenes**: desde la computadora o desde el celular con un código QR de un solo uso (también fotos HEIC del iPhone). Se guarda el original sin modificar, con su huella SHA-256.
- **Análisis en capas independientes**, que nunca se combinan en un puntaje único:

  | Capa | Técnica | Herramientas | Estado |
  |---|---|---|---|
  | 1 | Metadatos EXIF y XMP | ExifTool, Pillow | En producción |
  | 2 | Credenciales de contenido C2PA | c2pa-python | En producción |
  | 3 | Análisis de niveles de error (ELA) por bloques | Pillow, NumPy | En producción |
  | 4 | Clasificador de redes neuronales (EfficientNet-B0) | PyTorch para entrenar, ONNX Runtime en producción | Prueba de concepto lista; falta el entrenamiento completo ([docs/red-neuronal/](docs/red-neuronal/README.md)) |

- **Informe PDF por rubro**, con su huella publicada en **Hedera** (red pública) y una página de verificación para comprobar que nadie lo alteró.
- **Planes y pago** en el registro, **inicio de sesión con Google** y **retención y destrucción** de datos según la Ley 25.326.
- **Página `/estado`**, que muestra si la API, la base de datos, la cola de análisis y el sello en Hedera están funcionando.

## Estado

Desplegada en AWS (región Irlanda) con despliegue automático desde `main`. El sello en Hedera funciona en la red de prueba (*testnet*). El avance de cada funcionalidad está en [docs/funcionalidades/](docs/funcionalidades/README.md) y los números del proceso, que se calculan solos, en el [mapa del arnés](docs/arnes/README.md) (sección «Números del proceso»).

## Tecnologías

| Parte | Tecnologías |
|---|---|
| Backend | Python, Flask, SQLAlchemy y Alembic, PostgreSQL, Redis y RQ, Pydantic, WeasyPrint |
| Frontend | React con Vite y React Router |
| Red neuronal | PyTorch, timm, ONNX y ONNX Runtime, MLflow, Google Colab |
| Servicios externos | Hedera (sello de tiempo), Google (inicio de sesión), Amazon SES (correo) |
| Infraestructura | AWS (EC2, S3, SES, Systems Manager), Terraform, Nginx, Gunicorn, Docker Compose para desarrollo |
| Calidad | pytest con cobertura mínima del 80 %, flake8, pylint, import-linter, ESLint, Vitest, GitHub Actions, Conventional Commits en español |

## Levantarlo en local

Paso a paso en [docs/guias/levantar-en-local.md](docs/guias/levantar-en-local.md) (en Windows, primero [instalacion-entorno-windows.md](docs/guias/instalacion-entorno-windows.md)). Para producción: [docs/guias/despliegue-aws.md](docs/guias/despliegue-aws.md).

## Estructura del repositorio

```
.
├── backend/          API REST en Flask (capas Rutas → Servicios → Repositorios → Modelos)
├── frontend/         Interfaz web en React
├── red_neuronal/     Entrenamiento, evaluación y exportación del clasificador (capa 4)
├── infraestructura/  Terraform, Nginx, systemd y scripts de operación
├── docs/             Especificación, arquitectura, funcionalidades, guías, bitácora y arnés
├── .github/          Integración continua y despliegue
├── .claude/          Arnés para el trabajo asistido por IA: comandos, ganchos y skills
└── CLAUDE.md         Reglas para cualquier agente de IA que trabaje en el repositorio
```

El detalle de cada carpeta está en [docs/arquitectura/estructura-del-repositorio.md](docs/arquitectura/estructura-del-repositorio.md).

## Documentación

| Documento | Para qué sirve |
|---|---|
| [docs/constitucion.md](docs/constitucion.md) | Principios no negociables del proyecto |
| [docs/especificacion/](docs/especificacion/README.md) | Requisitos, reglas de negocio, casos de uso y cuestiones abiertas |
| [docs/funcionalidades/](docs/funcionalidades/README.md) | Especificación, plan y tareas de cada funcionalidad, con su estado |
| [docs/arquitectura/decisiones/](docs/arquitectura/decisiones/README.md) | Decisiones de arquitectura (ADR) |
| [docs/red-neuronal/](docs/red-neuronal/README.md) | La red neuronal de punta a punta |
| [docs/guias/guia-de-usuario.md](docs/guias/guia-de-usuario.md) | Cómo se usa la plataforma |
| [docs/guias/flujo-de-trabajo.md](docs/guias/flujo-de-trabajo.md) | Ramas, commits, Pull Requests y versiones |
| [docs/arnes/](docs/arnes/README.md) | Cómo se trabaja con el agente de IA: guías, sensores, memoria y persona en el circuito |
| [docs/bitacora/](docs/bitacora/README.md) | Registro cronológico de lo realizado, decidido y pendiente |
| [docs/calidad/indice-de-calidad.md](docs/calidad/indice-de-calidad.md) | Índice de calidad del software |
| [docs/informe-final/insumos.md](docs/informe-final/insumos.md) | Hallazgos y decisiones para el informe final |

## Trabajo asistido por IA

Gran parte del código lo escribe un agente de IA (Claude Code) dentro de un **arnés**: reglas escritas en [CLAUDE.md](CLAUDE.md), controles automáticos que lo frenan o le avisan, memoria del proyecto en el repositorio y una persona que revisa, integra y decide. Cada commit del agente queda firmado con `Co-Authored-By`. Detalle en [docs/arnes/README.md](docs/arnes/README.md).
