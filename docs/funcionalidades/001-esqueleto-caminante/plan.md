# Plan técnico: 001 — Esqueleto caminante

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Se construye la versión mínima del sistema que recorre todas sus piezas de punta a punta:

```
Navegador ──▶ Vite (React, :5173) ──proxy /api──▶ Flask (:5000)
                                                   │
                        ruta /api/salud ──▶ ServicioSalud ──┬──▶ RepositorioSalud ──▶ PostgreSQL
                                                            └──▶ ClienteRedis ─────▶ Redis
```

El endpoint `GET /api/salud` es el primer recorrido real de la arquitectura en capas: la ruta no conoce la base de datos, solo el servicio; el servicio arma sus dependencias y no conoce Flask. Los servicios de apoyo (PostgreSQL, Redis, almacenamiento S3 y correo) se levantan con Docker Compose.

La calidad queda automatizada en tres niveles: el editor (extensiones de VS Code), los ganchos de Git (pre-commit) y la integración continua (GitHub Actions).

## Capas afectadas

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Fábrica | `backend/app/__init__.py` | `crear_app()`: construye la aplicación (Application Factory) |
| Extensiones | `backend/app/extensiones.py` | Instancias de SQLAlchemy y Migrate sin aplicación asociada |
| Configuración | `backend/app/configuracion/entornos.py` | Una clase por entorno (Strategy) y validación de variables |
| Configuración | `backend/app/configuracion/fabrica.py` | `obtener_configuracion()`: elige la clase según `ENTORNO` (Factory) |
| Rutas | `backend/app/rutas/salud.py` | `GET /api/salud` |
| Servicios | `backend/app/servicios/servicio_salud.py` | Ejecuta las verificaciones y arma el estado |
| Repositorios | `backend/app/repositorios/repositorio_salud.py` | `SELECT 1` contra la base de datos |
| Integraciones | `backend/app/integraciones/cliente_redis.py` | `PING` a Redis |
| Entrada WSGI | `backend/wsgi.py` | Punto de entrada para Flask y Gunicorn; carga `.env` |
| Frontend | `frontend/src/api/salud.js` | Único lugar que conoce la URL de la API |
| Frontend | `frontend/src/paginas/PaginaInicio.jsx` | Muestra el estado de cada servicio |

## Patrones aplicados

- **Application Factory**: la aplicación se crea en `crear_app()`, lo que permite una instancia aislada por prueba.
- **Factory + Strategy**: `obtener_configuracion()` elige entre `ConfiguracionDesarrollo`, `ConfiguracionPruebas` y `ConfiguracionProduccion`.
- **Repository**: `RepositorioSalud` encapsula el acceso a la base de datos.
- **Service Layer**: `ServicioSalud` contiene la lógica y recibe sus verificaciones por **inyección de dependencias**, de modo que se prueba sin base de datos ni Redis reales.
- **Adaptador** (base para el Strategy de integraciones): `ClienteRedis` aísla la biblioteca `redis`.

## Contratos

### API

`GET /api/salud`

| Código | Cuándo | Cuerpo |
|---|---|---|
| 200 | Todos los componentes responden | `{"estado": "ok", "componentes": {"api": "ok", "base_de_datos": "ok", "redis": "ok"}, "entorno": "desarrollo", "version": "0.1.0"}` |
| 503 | Algún componente no responde | Igual, con `"estado": "degradado"` y `"error"` en el componente que falla |

### Backend

| Elemento | Firma | Excepciones |
|---|---|---|
| `crear_app` | `crear_app(nombre_entorno=None) -> Flask` | `ErrorConfiguracion` |
| `obtener_configuracion` | `obtener_configuracion(nombre_entorno=None) -> ConfiguracionBase` | `ErrorConfiguracion` |
| `ServicioSalud` | `ServicioSalud(verificaciones: dict[str, Callable[[], bool]])`, `.obtener_estado() -> EstadoSalud` | Ninguna: una verificación que falla se informa como `"error"` |
| `crear_servicio_salud` | `crear_servicio_salud(url_redis) -> ServicioSalud` | — |
| `RepositorioSalud` | `.verificar_conexion() -> bool` | — |
| `ClienteRedis` | `ClienteRedis(url)`, `.verificar_conexion() -> bool` | — |

### Variables de entorno

| Variable | Obligatoria en | Ejemplo |
|---|---|---|
| `ENTORNO` | — (por defecto `desarrollo`) | `desarrollo` |
| `CLAVE_SECRETA` | producción | valor aleatorio de 64 caracteres |
| `URL_BASE_DATOS` | desarrollo y producción | `postgresql+psycopg://sistema:sistema@localhost:5432/sistema_deteccion` |
| `URL_REDIS` | producción | `redis://localhost:6379/0` |

## Cambios en datos

No se crean tablas. Se inicializa la carpeta de migraciones (`backend/migraciones/`) con `flask db init`, para que desde la funcionalidad 002 cada modelo nuevo genere su migración.

## Servicios de desarrollo (Docker Compose)

| Servicio | Imagen | Puertos | Para qué |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | 5432 | Base de datos |
| `redis` | `redis:7-alpine` | 6379 | Cola de tareas (desde la 007) |
| `mailpit` | `axllent/mailpit` | 1025, bandeja web 8025 | Captura los correos sin enviarlos (desde la 002) |

## Bibliotecas nuevas

### Backend (`requirements.txt` y `requirements-dev.txt`)

| Biblioteca | Versión | Para qué se usa |
|---|---|---|
| Flask | 3.1.3 | Framework web de la API |
| Flask-SQLAlchemy | 3.1.1 | Integra el ORM SQLAlchemy con Flask |
| SQLAlchemy | 2.0.54 | ORM y acceso a datos |
| Flask-Migrate | 4.1.0 | Migraciones con Alembic (ADR-0008) |
| psycopg[binary] | 3.3.6 | Controlador de PostgreSQL (versión 3, la actual) |
| redis | 6.4.0 | Cliente de Redis |
| python-dotenv | 1.2.4 | Lee el archivo `.env` en desarrollo |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | Pruebas y cobertura (coverage.py) |
| flake8 | 7.4.1 | Estilo PEP 8 |
| pylint | 4.1.2 | Análisis estático; exige docstrings |
| import-linter | 2.15 | Verifica automáticamente la arquitectura en capas |
| pre-commit | 4.6.2 | Ganchos de Git |

### Frontend (`package.json`)

| Biblioteca | Versión | Para qué se usa |
|---|---|---|
| react / react-dom | 19.3.0 | Biblioteca de interfaz |
| vite / @vitejs/plugin-react | 7.3.7 / 5.2.0 | Servidor de desarrollo, proxy hacia la API y compilación |
| vitest / @vitest/coverage-v8 | 4.1.11 | Pruebas y cobertura |
| @testing-library/react, dom y jest-dom | 16.3.3, 10.4.2, 6.9.1 | Probar componentes como los usa una persona |
| jsdom | 30.1.2 | Navegador simulado para las pruebas |
| eslint y complementos | 10.12.0 | Análisis estático |

### Herramientas de proceso

| Herramienta | Para qué |
|---|---|
| commitlint 21.2.3 | Valida los mensajes de commit con los tipos en español. Única lista de tipos en `commitlint.config.mjs`, usada en local y en la integración continua |
| pre-commit-hooks 6.0.0 | Espacios sobrantes, fin de archivo, YAML válido, archivos grandes, claves privadas |
| GitHub Actions | Tres trabajos: backend, frontend y commits |

## Estrategia de pruebas

| Tipo | Archivo | Qué verifica | Criterio |
|---|---|---|---|
| Unitaria | `pruebas/unitarias/test_configuracion.py` (6 pruebas) | Entornos, valores por defecto, producción sin clave | CA6 |
| Unitaria | `pruebas/unitarias/test_servicio_salud.py` (3) | Estado ok, componente caído, excepción aislada | CA2, CA3 |
| Unitaria | `pruebas/unitarias/test_cliente_redis.py` (1) | Redis inaccesible devuelve `False` | CA3 |
| Integración | `pruebas/integracion/test_ruta_salud.py` (2) | Respuestas 200 y 503 de la API | CA2, CA3 |
| Integración | `pruebas/integracion/test_repositorio_salud.py` (2) | Base disponible y caída | CA3 |
| Arquitectura | `pruebas/arquitectura/test_capas.py` (1) | Contratos de import-linter | CA9 |
| Frontend | `src/paginas/PaginaInicio.test.jsx` (4) | Conectada, degradada, sin API, respuesta inesperada | CA4, CA5 |
| Manual | Navegador y terminal | Docker Compose, página real, commit inválido | CA1, CA10, CA11 |

Las pruebas del backend usan SQLite en memoria y simulan Redis: nunca tocan la base de desarrollo (constitución, principio 5).

## Excepciones a la constitución

- Los atributos de configuración `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `DEBUG` y `TESTING` quedan en inglés porque los exigen Flask y sus extensiones (excepción prevista en RNF21, CA2). Las variables de entorno que los alimentan están en español.
- Los archivos que genera Alembic en `migraciones/` quedan en inglés por ser generados automáticamente.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Puertos 5432, 6379, 5000 o 5173 ocupados por otro programa | Detener el programa o cambiar el puerto en `docker-compose.yml` o en el `.env` |
| Finales de línea de Windows (CRLF) que rompen scripts | `.gitattributes` normaliza a LF y `core.autocrlf=input` |
| Límite de descargas de Docker Hub | Reintentar más tarde o iniciar sesión con `docker login` |
| Versiones de bibliotecas que dejan de tener soporte | Versiones fijadas exactas; revisión al inicio de cada fase |


## Registro de cambios

| 2026-10-10 | Se quita MinIO de los servicios de desarrollo (imagen discontinuada en Docker Hub); el almacenamiento S3 se resuelve en la funcionalidad 006. |
