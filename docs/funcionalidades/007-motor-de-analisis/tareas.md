# Tareas: 007 — Motor de análisis y capa 1 (metadatos)

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — Revisión de `metadatos_service.py` y sus pruebas en el repositorio TIF. Resultado registrado en el plan.
- [x] **T02** — Especificación, plan y ADR-0013 (cola intercambiable).
  - Commit: `documentacion(007): agregar especificacion, plan con la revision del TIF y ADR-0013`
- [x] **T03** — Dependencias: RQ, y ExifTool en la integración continua.
  - Commit: `construccion(backend): agregar RQ y ExifTool en la integracion continua`
- [x] **T04** — Capas (`app/analisis/`), cola, modelos, migración, servicio, rutas, tarea, trabajador y correos.
  - Verificación: `flake8`, `pylint`, `lint-imports` y migración con `upgrade`, `check` y `downgrade` en PostgreSQL.
  - Commit: `funcionalidad(analisis): agregar el motor de analisis y la capa de metadatos`
- [x] **T05** — Pruebas de la capa, de la cola y de integración.
  - Commit: `pruebas(analisis): probar la capa de metadatos, la cola y el motor de analisis`
- [x] **T06** — Selección de imágenes, botón "Analizar", progreso, historial y resultados, con pruebas.
  - Commit: `funcionalidad(analisis): agregar el pedido de analisis, el progreso y los resultados por capa`
- [x] **T07** — Recorrido en navegador:
  - Tres imágenes: un JPEG con Photoshop y un iPhone 15 Pro "en 2021", un PNG sin metadatos y una imagen de ChatGPT.
  - Cola en hilo, progreso visible, resultados, correo y celular.
- [ ] **T08** — Revisión de la autora (severidades y cálculo del nivel, para validar con los tutores) y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora y ADR-0013.
