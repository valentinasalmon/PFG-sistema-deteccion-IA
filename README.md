# evidentIA · Detección de imágenes manipuladas o generadas por IA

[![Integración continua](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/actions/workflows/integracion-continua.yml/badge.svg?branch=main)](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/actions/workflows/integracion-continua.yml)

Proyecto Final de Grado de Ingeniería en Sistemas de Información.

Plataforma web de **apoyo a la decisión** para abogados y aseguradoras que hace una evaluación preliminar de las fotos aportadas como prueba en siniestros automovilísticos y laborales. Cada imagen pasa por cuatro capas de análisis independientes y el resultado se entrega en un informe PDF breve, con su huella registrada en la red pública Hedera para que cualquiera compruebe que no fue alterado. **El sistema no emite veredictos**: presenta indicios y recomienda consultar a un profesional (RN27).

- **Producción**: [evidentiaa.com.ar](https://evidentiaa.com.ar) (estado de los servicios en [`/estado`](https://evidentiaa.com.ar/estado)).
- **Guía de usuario**: [docs/guias/guia-de-usuario.md](docs/guias/guia-de-usuario.md).

## Qué hace

- Cuentas para abogados (individuales o con estudio) y aseguradoras (del catálogo de la SSN, con aprobación del Administrador y verificación de identidad del Referente).
- Casos o siniestros con carga de fotos desde la computadora, desde el celular por QR de un solo uso o por un enlace para la persona afectada.
- Análisis en cuatro capas, informe PDF por rubro con dos QR (análisis detallado y verificación) y verificación pública del PDF.
- Organizaciones con invitaciones, roles y planes; correos transaccionales; retención y baja de cuenta conforme a la Ley 25.326.

## Capas de análisis

| Capa | Técnica | Herramientas |
|---|---|---|
| 1 | Metadatos EXIF / XMP | ExifTool, Pillow |
| 2 | Credenciales de contenido C2PA | c2pa-python y lista de confianza del consorcio |
| 3 | Análisis de niveles de error (ELA) por bloques | Pillow, NumPy |
| 4 | Clasificador de redes neuronales convolucionales | PyTorch (entrenamiento), ONNX Runtime (producción) |

## Tecnologías

- **Backend**: Python 3.12, Flask, SQLAlchemy, PostgreSQL, Alembic, RQ con Redis, WeasyPrint.
- **Frontend**: React con Vite.
- **Infraestructura**: AWS (Irlanda): EC2, S3, SES, Route 53, Systems Manager; Nginx, Gunicorn, Let's Encrypt; Terraform. Sello de tiempo en Hedera Consensus Service.
- **Calidad**: pytest y coverage.py, flake8, pylint, import-linter, ESLint, Vitest, Playwright (recorridos de punta a punta), axe-core (accesibilidad), GitHub Actions.

## Ejecutarlo en la computadora

Requisitos: Python 3.12, Node 22, Docker (para PostgreSQL y Redis) y ExifTool. El paso a paso completo, también para Windows con WSL, está en [docs/guias/levantar-en-local.md](docs/guias/levantar-en-local.md). En resumen:

1. Levantar PostgreSQL y Redis con `docker compose up -d`.
2. En `backend/`: crear el entorno virtual, instalar `requirements-dev.txt`, copiar la configuración de ejemplo del backend (la guía indica cómo), ejecutar `flask --app wsgi db upgrade` y crear la cuenta de prueba con `flask --app wsgi administracion cuenta-de-prueba` (`prueba@evidentia.local` / `Prueba12345`). Iniciar con `flask --app wsgi run --port 5000`.
3. En `frontend/`: `npm install` y `npm run dev`; la plataforma queda en `http://localhost:5173`.

## Verificar la calidad

```bash
# Backend (desde backend/)
flake8 app/ && pylint app/ && pytest --cov=app --cov-fail-under=80
# Frontend (desde frontend/)
npm run lint && npm run test
# Interfaz, con el entorno levantado (ver frontend/e2e/README.md)
node frontend/e2e/sensor-diseno.cjs
node frontend/e2e/accesibilidad.cjs
```

La integración continua corre todo esto en cada Pull Request, más la validación de Terraform, `shellcheck`, `pip-audit`, `npm audit` y el recorrido del abogado en computadora y celular. Cada fusión en `main` se despliega sola en AWS. Índice de Calidad del Software: [docs/calidad/indice-de-calidad.md](docs/calidad/indice-de-calidad.md).

## Estructura del repositorio

```
.
├── backend/          API REST en Flask (capas Rutas → Servicios → Repositorios → Modelos)
├── frontend/         Interfaz web en React y recorridos de punta a punta (e2e/)
├── red_neuronal/     Entrenamiento y exportación del clasificador (capa 4)
├── infraestructura/  Terraform, Nginx, systemd y scripts de operación
├── docs/             Especificación, arquitectura, guías, calidad y bitácora
├── .github/          Integración continua y despliegue
└── .claude/          Arnés para el trabajo asistido por IA (reglas, comandos y ganchos)
```

El detalle de cada carpeta está en [docs/arquitectura/estructura-del-repositorio.md](docs/arquitectura/estructura-del-repositorio.md).

## Documentación

| Documento | Para qué sirve |
|---|---|
| [docs/constitucion.md](docs/constitucion.md) | Principios no negociables del proyecto |
| [docs/especificacion/](docs/especificacion/) | Requisitos, reglas de negocio, casos de uso y cuestiones abiertas |
| [docs/funcionalidades/](docs/funcionalidades/) | Especificación, plan y tareas de cada funcionalidad |
| [docs/arquitectura/decisiones/](docs/arquitectura/decisiones/) | Registros de decisiones de arquitectura (ADR) |
| [docs/red-neuronal/](docs/red-neuronal/README.md) | La red neuronal de la capa 4, de punta a punta |
| [docs/guias/despliegue-aws.md](docs/guias/despliegue-aws.md) | Infraestructura, despliegue y dominio |
| [docs/guias/flujo-de-trabajo.md](docs/guias/flujo-de-trabajo.md) | Ramas, commits y desarrollo guiado por especificaciones |
| [docs/arnes/README.md](docs/arnes/README.md) | Cómo se trabaja con el agente de IA (guías, sensores y memoria) |
| [docs/versiones.md](docs/versiones.md) | Qué trae cada versión etiquetada |
| [docs/bitacora/](docs/bitacora/) | Registro cronológico de lo realizado |

## Uso de inteligencia artificial

El desarrollo se hizo con la asistencia de un agente de IA (Claude Code) bajo las reglas del arnés de [CLAUDE.md](CLAUDE.md): cada commit asistido lleva la línea `Co-Authored-By`, y la autora revisa e integra cada Pull Request.

## Estado

Versión **v1.0** en preparación (ver [docs/versiones.md](docs/versiones.md)). Avance día a día en la [bitácora](docs/bitacora/).
