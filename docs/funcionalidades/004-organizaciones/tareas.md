# Tareas: 004 — Organizaciones e invitaciones

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — Modelos, repositorio y migración.
  - Archivos: `app/modelos/organizacion.py`, `app/modelos/__init__.py`, `app/repositorios/repositorio_organizaciones.py`, `migraciones/versions/cf00ca279723_crear_tablas_de_organizaciones.py`
  - Verificación: con PostgreSQL, `db upgrade`, `db check` y `db downgrade` sin errores.
- [x] **T02** — Servicio, errores, configuración de planes, correos y acciones de auditoría.
  - Archivos: `app/servicios/servicio_organizaciones.py`, `errores.py`, `auditoria.py`, `servicio_correos.py`, `tokens.py`, `fabrica.py`; `app/configuracion/entornos.py`; 12 plantillas en `app/plantillas/correos/`
- [x] **T03** — Esquemas y rutas.
  - Archivos: `app/esquemas/organizaciones.py`, `app/rutas/organizaciones.py`, `app/rutas/invitaciones.py`, `app/rutas/errores.py`, `app/rutas/__init__.py`
  - Verificación: `flake8 app/ && pylint app/ && lint-imports`.
  - Commit de T01 a T03: `funcionalidad(organizaciones): agregar organizaciones, invitaciones y membresias`
- [x] **T04** — Pruebas del backend.
  - Archivos: `pruebas/integracion/test_rutas_organizaciones.py`, `pruebas/unitarias/test_correo.py`
  - Verificación: `pytest --cov=app --cov-fail-under=80`.
  - Commit: `pruebas(organizaciones): probar cada criterio de aceptacion de la 004`
- [x] **T05** — Pantallas, cliente de la API, componentes y pruebas del frontend.
  - Archivos: `src/api/organizaciones.js`, `src/hooks/useDatos.js`, `src/utilidades/fechas.js`, `src/componentes/BotonConfirmar.jsx`, `Etiqueta.jsx`, `Encabezado.jsx`, `src/paginas/PaginaOrganizaciones.jsx`, `PaginaNuevaOrganizacion.jsx`, `PaginaOrganizacion.jsx`, `PaginaInvitacion.jsx`, `PaginaRegistro.jsx` (correo precargado), `App.jsx`, `global.css` y sus pruebas
  - Verificación: `npm run lint && npm run test:cobertura && npm run build`.
  - Commit: `funcionalidad(organizaciones): agregar las pantallas de organizaciones e invitaciones`
- [x] **T06** — Recorrido en navegador con dos cuentas y correo real: crear, invitar a un correo sin cuenta, abrir el enlace en celular, registrarse con el correo precargado, aceptar desde la lista, designar Referente, abandonar y eliminar.
- [ ] **T07** — Revisión de la autora y Pull Request hacia `desarrollo` (después de integrar la 003).

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora.
