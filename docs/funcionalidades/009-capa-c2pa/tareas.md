# Tareas: 009 — Capa 2 (credenciales de contenido C2PA)

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — Revisión de `c2pa_service.py`, `probar_c2pa_firma.py`, sus pruebas y sus resultados en el TIF; sonda con c2pa-python sobre las 10 imágenes de canales; especificación.
  - Commit: `documentacion(009): agregar especificacion de la capa de credenciales de contenido C2PA`
- [x] **T02** — Lista de confianza en `recursos/confianza_c2pa`, capa `CapaC2PA`, registro, configuración, textos del informe y cálculo de nivel común en `base.py`.
  - Verificación: `flake8`, `pylint`, `lint-imports`.
  - Commit: `funcionalidad(analisis): agregar la capa de credenciales de contenido C2PA`
- [x] **T03** — Pruebas con imágenes firmadas en la prueba, prueba de canales del TIF (opcional), integración e informe.
  - Commit: `pruebas(analisis): probar la capa de credenciales de contenido con imagenes firmadas`
- [x] **T04** — Pantalla: título, estado de la firma y tabla de la capa 2, con pruebas.
  - Commit: `funcionalidad(analisis): mostrar la capa de credenciales de contenido en la pantalla del caso`
- [x] **T05** — Recorrido en navegador con imágenes de ChatGPT, Gemini, ChatGPT por WhatsApp y una editada; revisión del PDF (el título de cada capa ya no queda separado de su contenido).
- [ ] **T06** — Revisión de la autora (severidades y "¿Qué significa?" con los tutores) y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora.
