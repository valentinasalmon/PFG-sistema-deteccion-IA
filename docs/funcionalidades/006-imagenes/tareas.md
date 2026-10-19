# Tareas: 006 — Carga de imágenes, huella y almacenamiento

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — Dependencias: Pillow, boto3 y moto.
  - Commit: `construccion(backend): agregar Pillow, boto3 y moto para las imagenes`
- [x] **T02** — Almacenamiento, modelo, migración, servicio, rutas y borrado de archivos de los casos eliminados.
  - Verificación: `flake8`, `pylint`, `lint-imports` y migración con `upgrade`, `check` y `downgrade` en PostgreSQL.
  - Commit: `funcionalidad(imagenes): agregar carga, consulta y eliminacion de imagenes`
- [x] **T03** — Pruebas del backend: integración, utilidades y adaptadores.
  - Commit: `pruebas(imagenes): probar la carga, los enlaces y la eliminacion de imagenes`
- [x] **T04** — Galería en la pantalla del caso y pruebas del frontend.
  - Commit: `funcionalidad(imagenes): agregar la galeria de imagenes en la pantalla del caso`
- [x] **T05** — Recorrido en navegador con imágenes generadas:
  - Carga múltiple con un archivo falso y un duplicado.
  - Descarga idéntica al original.
  - Eliminación.
  - Celular a 375 px.
  - Caso cerrado sin la opción de cargar.
- [ ] **T06** — Revisión de la autora y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora y ADR-0012.
