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
| `ADMINISTRADORES` | Correos, separados por comas, que pasan a Administrador al iniciar sesión | — |

Los correos de desarrollo se ven en Mailpit: `http://localhost:8025`.

El archivo `.env` **nunca** se sube al repositorio.

## Administradores

La interfaz nunca ofrece el rol de Administrador. Hay dos formas de darlo a una cuenta ya registrada y verificada:

1. Agregar su correo en `ADMINISTRADORES` dentro de `.env`, reiniciar el servidor y que esa persona inicie sesión.
2. Desde la terminal: `flask --app wsgi administracion promover <correo>`.

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
| `app/integraciones/` | Adaptadores a servicios externos (Redis, correo, almacenamiento S3 o local; luego BFA) |
| `migraciones/` | Migraciones de Alembic |
| `pruebas/` | Pruebas unitarias, de integración y de arquitectura |

## Imágenes de los casos

En desarrollo, las imágenes se guardan en `backend/almacenamiento_local/` (variable `ALMACENAMIENTO=local`). Esa carpeta está en `.gitignore`: **nunca** se sube al repositorio. Para probar, usá imágenes propias o generadas, nunca de casos reales.

En producción se usa un bucket privado de S3 con cifrado y versionado (`ALMACENAMIENTO=s3`, `S3_BUCKET`, `S3_REGION`). Las pruebas del adaptador de S3 usan `moto`, que lo simula sin conectarse a AWS.

## Análisis de imágenes

La capa de metadatos usa **ExifTool**, que se instala con el sistema (`sudo apt install libimage-exiftool-perl`; el script de entorno de WSL ya lo incluye). Si no está, la capa figura como "No disponible" y el resto del análisis sigue.

En desarrollo, los análisis corren en un hilo del mismo servidor (`COLA_ANALISIS=hilo`): no hace falta levantar nada más. Para probar la cola real de producción (ADR-0013):

```bash
# terminal 1: el servidor con COLA_ANALISIS=rq en el .env
flask --app wsgi run
# terminal 2: el trabajador
source .venv/bin/activate && python trabajador.py
```

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `/api/salud` responde 503 con `base_de_datos: error` | Verificar que PostgreSQL esté levantado: `docker compose ps` |
| `ErrorConfiguracion: Faltan variables de entorno` | Crear el archivo `.env` a partir de `.env.ejemplo` |
| La capa de metadatos aparece "No disponible: ExifTool no está instalado" | `sudo apt install libimage-exiftool-perl` |
| `ModuleNotFoundError` | Activar el entorno virtual: `source .venv/bin/activate` |
| `error: externally-managed-environment` al usar `pip`, o `flask: command not found` | El entorno virtual no está activo (el prompt no empieza con `(.venv)`): `source .venv/bin/activate` y repetir el comando |
