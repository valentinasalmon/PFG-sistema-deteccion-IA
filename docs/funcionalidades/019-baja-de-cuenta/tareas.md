# Tareas: 019 — Eliminación de cuenta y copia de datos personales

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Todas las tareas las escribe y sube el asistente; la autora revisa e integra el Pull Request (ver [CLAUDE.md](../../../CLAUDE.md)).

- [x] **T01** — WeasyPrint y bibliotecas del sistema en la integración continua.
  - Commit: `construccion(backend): agregar WeasyPrint y sus bibliotecas en la integracion continua`
- [x] **T02** — Repositorios, servicio, documento de la copia (JSON y PDF), correos, esquemas y rutas.
  - Verificación: `flake8 app/ && pylint app/ && lint-imports`.
  - Commit: `funcionalidad(cuenta): agregar copia de datos personales y eliminacion de la cuenta`
- [x] **T03** — Pruebas del backend.
  - Archivos: `test_datos_personales.py` y `test_copia_de_datos.py`; accesorio `cuenta` común en `conftest.py`.
  - Commit: `pruebas(cuenta): probar la copia de datos y la eliminacion de la cuenta`
- [x] **T04** — Secciones de "Mi perfil", aviso al salir, Política de Privacidad y pruebas del frontend.
  - Commit: `funcionalidad(cuenta): agregar copia de datos y eliminacion de la cuenta en Mi perfil`
- [x] **T05** — Recorrido en navegador con PostgreSQL. Pasos:
  - Copia en PDF y JSON.
  - Resolver los pendientes (eliminar un caso, transferir otro y designar Referente).
  - Eliminar la cuenta y comprobar el correo y la auditoría anonimizada.
- [ ] **T06** — Revisión de la autora (incluida CP-20) y Pull Request hacia `desarrollo`.

## Cierre

- [x] Pruebas, flake8, pylint, contratos de capas y cobertura en verde.
- [x] Criterios de aceptación de la especificación verificados.
- [x] Entrada en la bitácora.
