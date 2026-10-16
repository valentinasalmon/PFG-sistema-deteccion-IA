# Tareas: 003 — Auditoría

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Desde esta funcionalidad, el asistente escribe y sube todas las tareas y la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)). Los comandos del backend se ejecutan en `backend/` con el entorno virtual activado; los del frontend, en `frontend/`.

- [x] **T01** — Modelo `EntradaAuditoria`, repositorio de solo inserción y migración.
  - Archivos: `app/modelos/entrada_auditoria.py`, `app/modelos/__init__.py`, `app/repositorios/repositorio_auditoria.py`, `app/repositorios/repositorio_usuarios.py` (`preparar`), `migraciones/versions/3d740a09a480_crear_tabla_de_auditoria.py`
  - Verificación: con PostgreSQL, `flask --app wsgi db upgrade` crea la tabla, `flask --app wsgi db check` no detecta cambios y `db downgrade` la elimina.
  - Commit: `funcionalidad(auditoria): agregar el registro de auditoria y su migracion`
- [x] **T02** — `ServicioAuditoria` y registro de las acciones de cuenta y sesión.
  - Archivos: `app/servicios/auditoria.py`, `servicio_cuentas.py`, `servicio_sesion.py`, `servicio_perfil.py`, `fabrica.py`, `errores.py`, `tokens.py`, `app/seguridad/origen.py`, `app/seguridad/autenticacion.py`, `app/rutas/cuentas.py`, `sesion.py`, `perfil.py`, `errores.py`
  - Verificación: `flake8 app/ && pylint app/ && lint-imports` sin errores y las 94 pruebas de la 002 siguen pasando.
  - Commit: `funcionalidad(auditoria): registrar las acciones de cuenta y sesion`
- [x] **T03** — Pruebas de la auditoría.
  - Archivos: `pruebas/conftest.py` (`entradas_auditoria`), `pruebas/integracion/test_auditoria.py`, `pruebas/unitarias/test_auditoria.py`
  - Verificación: `pytest --cov=app --cov-fail-under=80` en verde.
  - Commit: `pruebas(auditoria): probar el registro de cada accion de cuenta y sesion`
- [x] **T04** — La Política de Privacidad informa el registro de actividad.
  - Archivos: `frontend/src/paginas/PaginaPrivacidad.jsx`, `frontend/src/paginas/legales.test.jsx`
  - Verificación: `npm run lint && npm run test:cobertura`.
  - Commit: `funcionalidad(legales): informar el registro de actividad en la politica de privacidad`
- [x] **T05** — Recorrido con PostgreSQL, Redis y correo reales: registro por pasos, verificación, inicio fallido y exitoso, edición del perfil y cierre; revisión de la tabla `auditoria` y de que las entradas se conservan anonimizadas al borrar la cuenta.
- [ ] **T06** — Revisión de la autora y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora y ADR-0011.
