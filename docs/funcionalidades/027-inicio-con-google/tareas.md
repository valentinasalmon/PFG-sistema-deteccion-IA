# Tareas: 027 — Inicio de sesión y registro con Google

- [x] **T01** — Cliente OpenID Connect (`integraciones/google.py`) con PKCE y validación del *ID token*.
- [x] **T02** — Columna `usuarios.google_sub` y migración `d1a7b3c5e027`.
- [x] **T03** — `ServicioGoogle`, `registrar_con_google`, `vincular_google`, `autenticar_con_google` y auditoría (`cuenta.vinculacion_google`).
- [x] **T04** — Rutas `/api/google/*` y esquema `SolicitudRegistroGoogle`.
- [x] **T05** — Cookie de sesión `SameSite=Lax` (ADR-0019).
- [x] **T06** — Pruebas del backend (31).
- [x] **T07** — Frontend: botón, avisos, pantalla "Completá tu registro" y componentes compartidos del registro.
- [x] **T08** — Pruebas del frontend (10).
- [x] **T09** — Terraform (`google_id_cliente`), `generar_entorno.sh`, `.env.ejemplo` y guía de despliegue.
- [ ] **T10 (autora)** — Crear el proyecto y el cliente OAuth en Google Cloud, y cargar a los usuarios de prueba (ver `docs/guias/despliegue-aws.md`).
- [ ] **T11 (autora)** — Probar en local y en producción: registro nuevo, entrada con una cuenta existente y cancelación.
