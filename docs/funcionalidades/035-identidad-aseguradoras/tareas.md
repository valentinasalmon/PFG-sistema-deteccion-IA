# Tareas: 035 — Verificación de identidad del Referente de una aseguradora

- [x] T01 — Especificación y plan (RN41, CA1 a CA7).
- [x] T02 — Modelo `VerificacionIdentidad` y migración `a3c5e7f9b035`.
- [x] T03 — Proveedor intercambiable con versión simulada (`app/integraciones/identidad.py`).
- [x] T04 — Repositorio, `ServicioIdentidad` y exigencia al aprobar en `ServicioOrganizaciones` (RN41).
- [x] T05 — Rutas: estado e inicio en la organización, página pública por token, simulación y estado en las aseguradoras pendientes.
- [x] T06 — Pruebas del backend (11, `pruebas/integracion/test_identidad.py`).
- [x] T07 — Frontend: sección del Referente, página `/identidad/:token` y «Aprobar» bloqueado en Administración.
- [x] T08 — Pruebas del frontend (12, `paginas/identidad.test.jsx`).
- [x] T09 — Terraform (`verificacion_identidad`) y `generar_entorno.sh`.
- [x] T10 — RN41, CP-35, CP-39, CP-40, bitácora, insumos y Trello.
- [ ] T11 — Conectar Identik en el sandbox (llamada a su API y aviso firmado), después de la reunión técnica y de resolver CP-39.
- [ ] T12 — Prueba contra el servicio real y estado de Identik en `/estado`.
