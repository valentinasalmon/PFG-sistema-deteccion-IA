# Tareas: 021 — Organizaciones de aseguradoras

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request.

- [x] **T01** — Catálogo de la SSN filtrado y documentado (`backend/recursos/catalogos/`).
- [x] **T02** — Modelos, migración, servicios, rutas, comando de terminal y correos.
  - Verificación: `flake8 app/ && pylint app/ && lint-imports`; migración con `upgrade`, `check` y `downgrade` en PostgreSQL.
  - Commit: `funcionalidad(aseguradoras): registrar aseguradoras del catalogo con aprobacion`
- [x] **T03** — Pruebas del backend (`pruebas/integracion/test_aseguradoras.py` y ajustes de pruebas anteriores).
  - Commit: `pruebas(aseguradoras): probar los criterios de aceptacion de la 021`
- [x] **T04** — Pantallas y pruebas del frontend.
  - Verificación: `npm run lint && npm run test:cobertura && npm run build`.
  - Commit: `funcionalidad(aseguradoras): agregar el registro de aseguradoras y la administracion`
- [x] **T05** — Recorrido en navegador: Administrador promovido por terminal, registro de Seguros Galicia, aprobación, invitación, registro de una empleada en celular, abandono con cuenta desactivada e inicio de sesión rechazado.
- [ ] **T06** — Revisión de la autora y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, análisis estático, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación verificados.
- [x] Entrada en la bitácora y especificación general actualizada (RN35 a RN40, CP-17, CP-18).
