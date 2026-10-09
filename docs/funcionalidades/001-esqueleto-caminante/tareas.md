# Tareas: 001 — Esqueleto caminante

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Cada tarea termina con una verificación y un commit. Al empezar a usar una carpeta vacía se borra su `.gitkeep`.

## Repositorio y servicios

- [ ] **T01** — Archivos de configuración del repositorio.
  - Archivos: `.gitignore`, `.gitattributes`, `.editorconfig`
  - Verificación: `git status` no muestra archivos temporales.
  - Commit: `tarea(repositorio): agregar configuracion de git y del editor`
- [ ] **T02** — Servicios de desarrollo con Docker Compose.
  - Archivos: `docker-compose.yml`
  - Verificación (CA1): `docker compose ps` muestra los 4 servicios `healthy`.
  - Commit: `construccion(entorno): agregar servicios de desarrollo con docker compose`

## Backend

- [ ] **T03** — Dependencias, herramientas de calidad y entorno virtual.
  - Archivos: `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/pyproject.toml`, `backend/.flake8`, `backend/.env.ejemplo`
  - Verificación: `pip list` muestra Flask 3.1.3.
  - Commit: `construccion(backend): agregar dependencias y configuracion de calidad`
- [ ] **T04** — Configuración por entorno (Factory + Strategy).
  - Archivos: `backend/app/configuracion/__init__.py`, `entornos.py`, `fabrica.py`, `backend/pruebas/__init__.py`, `backend/pruebas/unitarias/__init__.py`, `backend/pruebas/unitarias/test_configuracion.py`
  - Verificación (CA6): las 6 pruebas de configuración pasan.
  - Commit: `funcionalidad(configuracion): agregar configuracion por entorno`
- [ ] **T05** — Capas de servicio, repositorio e integración.
  - Archivos: `backend/app/extensiones.py`, `modelos/__init__.py`, `repositorios/__init__.py`, `repositorios/repositorio_salud.py`, `integraciones/__init__.py`, `integraciones/cliente_redis.py`, `servicios/__init__.py`, `servicios/servicio_salud.py`, `pruebas/unitarias/test_servicio_salud.py`, `pruebas/unitarias/test_cliente_redis.py`
  - Verificación: las pruebas del servicio y de Redis pasan.
  - Commit: `funcionalidad(salud): agregar servicio de salud con sus dependencias`
- [ ] **T06** — Ruta de salud, fábrica de la aplicación y punto de entrada.
  - Archivos: `backend/app/rutas/__init__.py`, `rutas/salud.py`, `backend/app/__init__.py`, `backend/wsgi.py`, `pruebas/conftest.py`, `pruebas/integracion/__init__.py`, `pruebas/integracion/test_ruta_salud.py`, `pruebas/integracion/test_repositorio_salud.py`
  - Verificación (CA2, CA3): las pruebas de integración pasan.
  - Commit: `funcionalidad(salud): agregar endpoint de salud de la api`
- [ ] **T07** — Prueba de arquitectura y control de calidad completo.
  - Archivos: `pruebas/arquitectura/__init__.py`, `pruebas/arquitectura/test_capas.py`
  - Verificación (CA7, CA8, CA9): 15 pruebas, cobertura ≥ 80 %, flake8 sin errores, pylint ≥ 8,5; una violación provocada hace fallar la prueba.
  - Commit: `pruebas(arquitectura): verificar contratos de capas con import-linter`
- [ ] **T08** — Migraciones y prueba manual de la API.
  - Archivos: `backend/migraciones/` (generados por `flask db init`)
  - Verificación (CA2, CA3): `curl` a `/api/salud` devuelve 200, y 503 con PostgreSQL detenido.
  - Commit: `construccion(backend): inicializar migraciones con alembic`

## Frontend

- [ ] **T09** — Proyecto React con Vite, ESLint y Vitest.
  - Archivos: `frontend/package.json`, `vite.config.js`, `eslint.config.js`, `index.html`, `src/main.jsx`, `src/pruebas/configuracion.js`, `package-lock.json` (generado)
  - Verificación: `npm install` termina sin errores.
  - Commit: `construccion(frontend): crear proyecto react con vite`
- [ ] **T10** — Página de estado del sistema.
  - Archivos: `frontend/src/api/salud.js`, `src/paginas/PaginaInicio.jsx`, `src/paginas/PaginaInicio.test.jsx`, `src/estilos/global.css`
  - Verificación (CA4, CA5): 4 pruebas pasan, ESLint sin errores, la página se ve en el navegador con y sin backend.
  - Commit: `funcionalidad(frontend): agregar pagina de estado del sistema`

## Proceso y cierre

- [ ] **T11** — Validación local de commits.
  - Archivos: `.pre-commit-config.yaml`, `commitlint.config.mjs`
  - Verificación (CA10): `feat: algo` se rechaza y `funcionalidad(...): algo` se acepta.
  - Commit: `integracion(commits): validar mensajes de commit en espanol`
- [ ] **T12** — Integración continua.
  - Archivos: `.github/workflows/integracion-continua.yml`
  - Commit: `integracion(ci): agregar integracion continua en github actions`
- [ ] **T13** — Documentación de uso.
  - Archivos: `backend/README.md`, `frontend/README.md`
  - Commit: `documentacion(001): agregar instrucciones de ejecucion`
- [ ] **T14** — Cierre: bitácora, Pull Request e integración continua en verde.
  - Verificación (CA11): los tres trabajos de GitHub Actions en verde.
  - Commit: `documentacion(bitacora): registrar funcionalidad 001`

## Cierre

- [ ] Criterios CA1 a CA11 verificados.
- [ ] Pull Request integrado en `desarrollo`.