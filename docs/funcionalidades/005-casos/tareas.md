# Tareas: 005 — Casos y permisos

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — Modelos, repositorios y migración.
  - Archivos: `app/modelos/caso.py`, `app/modelos/__init__.py`, `app/repositorios/base.py`, `repositorio_casos.py`, `repositorio_organizaciones.py`, `migraciones/versions/057c1b5b72d9_crear_tablas_de_casos.py`
  - Verificación: con PostgreSQL, `db upgrade`, `db check` y `db downgrade` sin errores.
- [x] **T02** — Servicio de casos, reglas pendientes de la 004, correos y acciones de auditoría.
  - Archivos: `app/servicios/servicio_casos.py`, `servicio_organizaciones.py`, `auditoria.py`, `servicio_correos.py`, `fabrica.py`; 5 correos en `app/plantillas/correos/`
- [x] **T03** — Esquemas y rutas.
  - Archivos: `app/esquemas/casos.py`, `app/esquemas/__init__.py`, `app/rutas/casos.py`, `app/rutas/__init__.py`, `app/esquemas/organizaciones.py`
  - Verificación: `flake8 app/ && pylint app/ && lint-imports`.
  - Commit de T01 a T03: `funcionalidad(casos): agregar casos, permisos, estados, accesos y transferencias`
- [x] **T04** — Pruebas del backend.
  - Archivos: `pruebas/integracion/test_rutas_casos.py` y los ajustes de `test_rutas_organizaciones.py`
  - Verificación: `pytest --cov=app --cov-fail-under=80`.
  - Commit: `pruebas(casos): probar los criterios de aceptacion de la 005`
- [x] **T05** — Pantallas, cliente de la API, componentes y pruebas del frontend.
  - Archivos: `src/api/casos.js`, `src/componentes/CampoAreaTexto.jsx`, `CampoSeleccion.jsx`, `Encabezado.jsx`, `src/utilidades/casos.js`, `fechas.js`, `src/paginas/PaginaCasos.jsx`, `PaginaNuevoCaso.jsx`, `PaginaCaso.jsx`, `PaginaInicio.jsx`, `App.jsx`, `global.css`, `casos.test.jsx`
  - Verificación: `npm run lint && npm run test:cobertura && npm run build`.
  - Commit: `funcionalidad(casos): agregar las pantallas de casos`
- [x] **T06** — Recorrido en navegador con dos cuentas. Pasos:
  - Crear el estudio, invitar y aceptar.
  - Crear un caso de organización, compartirlo en Lectura y verlo en solo lectura desde el celular.
  - Cerrarlo y ver la retención.
  - Crear un caso personal, transferirlo por correo, aceptarlo, buscar por expediente y eliminar.
- [ ] **T07** — Revisión de la autora y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora.
