# Backend

API REST del sistema, escrita en Python con Flask 3.1. Organizada en capas según la [constitución](../docs/constitucion.md): `rutas → servicios → repositorios → modelos`, con componentes transversales para configuración, integraciones y pruebas de arquitectura.

## Requisitos previos

- Ubuntu en WSL2 con Python 3.12 (ver [guía de instalación](../docs/guias/instalacion-entorno-windows.md)).
- Docker Desktop con los servicios de desarrollo levantados (`docker compose up -d` desde la raíz del repositorio).

## Instalación (una sola vez)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.ejemplo .env
```

Instalar también los ganchos de Git, desde la raíz del repositorio:

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## Ejecución

```bash
cd backend
source .venv/bin/activate
flask --app wsgi run --debug
```

La API queda disponible en `http://localhost:5000`. Para comprobarla: `http://localhost:5000/api/salud`.

## Variables de entorno (archivo `.env`)

| Variable | Descripción | Obligatoria en |
|---|---|---|
| `ENTORNO` | `desarrollo`, `pruebas` o `produccion` | — (por defecto `desarrollo`) |
| `CLAVE_SECRETA` | Clave para firmar sesiones y tokens | producción |
| `URL_BASE_DATOS` | Conexión a PostgreSQL | desarrollo y producción |
| `URL_REDIS` | Conexión a Redis (sesiones y cola de tareas) | producción |
| `URL_FRONTEND` | Dirección de la interfaz web, para los enlaces de los correos | producción |
| `SERVIDOR_CORREO` | Servidor SMTP (Mailpit en desarrollo) | producción |
| `PUERTO_CORREO` | Puerto SMTP | — (por defecto `1025`) |
| `USUARIO_CORREO`, `CONTRASENIA_CORREO` | Credenciales SMTP (vacías con Mailpit) | — |
| `USAR_TLS_CORREO` | `si` para cifrar la conexión SMTP | — (por defecto `no`; `si` en producción) |
| `REMITENTE_CORREO` | Remitente de los correos | producción |

Los correos de desarrollo se ven en Mailpit: `http://localhost:8025`.

El archivo `.env` **nunca** se sube al repositorio.

## Migraciones de la base de datos

```bash
flask --app wsgi db migrate -m "descripcion del cambio"   # generar una migración
flask --app wsgi db upgrade                               # aplicarla
flask --app wsgi db current                               # ver la versión actual
```

## Calidad

| Comando | Qué verifica | Mínimo exigido |
|---|---|---|
| `python -m pytest` | Pruebas, arquitectura en capas y cobertura | Cobertura ≥ 80 % |
| `flake8 app pruebas wsgi.py` | Estilo PEP 8 | Sin errores |
| `pylint app pruebas wsgi.py` | Análisis estático y docstrings | Puntuación ≥ 8,5 |
| `lint-imports` | Contratos de capas | Todos cumplidos |

Los mismos controles se ejecutan en la integración continua en cada Pull Request.

## Estructura

| Carpeta | Contenido |
|---|---|
| `app/configuracion/` | Configuración por entorno (Factory + Strategy) |
| `app/rutas/` | Endpoints de la API (controladores delgados) |
| `app/servicios/` | Lógica de negocio, sin dependencias de Flask |
| `app/repositorios/` | Acceso a la base de datos |
| `app/modelos/` | Entidades de SQLAlchemy |
| `app/integraciones/` | Adaptadores a servicios externos (Redis, y luego S3, SES y BFA) |
| `migraciones/` | Migraciones de Alembic |
| `pruebas/` | Pruebas unitarias, de integración y de arquitectura |

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `/api/salud` responde 503 con `base_de_datos: error` | Verificar que PostgreSQL esté levantado: `docker compose ps` |
| `ErrorConfiguracion: Faltan variables de entorno` | Crear el archivo `.env` a partir de `.env.ejemplo` |
| `ModuleNotFoundError` | Activar el entorno virtual: `source .venv/bin/activate` |
