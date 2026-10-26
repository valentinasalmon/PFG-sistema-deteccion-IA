# Tareas: 017 — Infraestructura y despliegue en AWS

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

- [x] **T01** — `ProxyFix` y región de Irlanda en la configuración, gunicorn y pruebas.
- [x] **T02** — Terraform: bucket del estado e infraestructura principal; validados con el proveedor AWS 6.66.
- [x] **T03** — Scripts del servidor, Nginx y systemd; shellcheck y `nginx -t`.
- [x] **T04** — Despliegue automático e integración continua de la infraestructura.
- [x] **T05** — Guía paso a paso, ADR-0016, especificación, plan y bitácora.
- [x] **T06** — Autora: pasos 1 a 7 de la [guía](../../guias/despliegue-aws.md) (cuenta, herramientas, `terraform apply`, verificación de SES y variables de GitHub).
- [x] **T07** — Autora: integrar `desarrollo` en `main` (hito v0.1) y comprobar el primer despliegue y el acceso por HTTPS.
- [ ] **T08** — Asistente y autora: revisar el primer despliegue, probar un respaldo y su restauración (RNF15 CA3).
- [ ] **T09** — Al final: dominio propio y, opcionalmente, salida del modo de prueba de SES.
