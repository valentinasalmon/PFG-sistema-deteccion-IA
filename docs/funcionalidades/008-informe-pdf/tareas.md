# Tareas: 008 — Informe PDF e historial

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — Especificación.
  - Commit: `documentacion(008): agregar especificacion del informe PDF e historial`
- [x] **T02** — Modelo, migración, plantillas comunes, contenido del informe, servicio, generación al finalizar, rutas y borrado de los PDF.
  - Verificación: `flake8`, `pylint`, `lint-imports` y migración con `upgrade`, `check` y `downgrade` en PostgreSQL.
  - Commit: `funcionalidad(informes): generar el informe PDF de cada analisis`
- [x] **T03** — Pruebas del backend.
  - Commit: `pruebas(informes): probar la generacion, el contenido y la descarga del informe`
- [x] **T04** — Descarga y regeneración en cada análisis, sección "Informes" y pruebas del frontend.
  - Commit: `funcionalidad(informes): agregar la descarga y el historial de informes en la pantalla del caso`
- [x] **T05** — Recorrido en navegador: tres imágenes, análisis, descarga del PDF (5 páginas) y revisión visual, imagen del informe sin eliminar.
- [ ] **T06** — Revisión de la autora (textos de "¿Qué significa?" y de la advertencia legal, con los tutores), Pull Request hacia `desarrollo` y, con el hito v0.1, Pull Request de `desarrollo` hacia `main` y etiqueta.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora.
