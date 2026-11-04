# 2026-11-04 — Funcionalidad 035: verificación de identidad de aseguradoras

## Qué se hizo

- **Backend**: modelo `VerificacionIdentidad` (sin datos biométricos), migración, proveedor intercambiable con versión simulada, `ServicioIdentidad`, rutas y exigencia al aprobar una aseguradora (RN41).
- **Frontend**: sección «Verificación de identidad» en la organización (el Referente la inicia; los miembros ven el estado), página pública `/identidad/:token` que aclara que es una simulación y permite elegir el resultado, y en Administración el estado de cada aseguradora pendiente con «Aprobar» deshabilitado hasta que la identidad esté aprobada.
- **Infraestructura**: variable `verificacion_identidad` (`desactivado` por defecto, o `simulado`).
- **Identik**: la autora envió el caso el 2026-11-03 y respondieron el 2026-11-04 con un sandbox de firma electrónica, precios y respuestas técnicas. Se preparó un documento para revisar con el tutor.

## Decisiones

- **Mismo patrón que el cobro con Cresium (ADR-0020)**: el proveedor es intercambiable; pasar a Identik cambia solo la integración y suma la ruta del aviso (*webhook*).
- **Solo el resultado**: la tabla no tiene dónde guardar imágenes ni biometría; el enlace se guarda como huella SHA-256.
- **Desactivada por defecto en producción**: la aprobación sigue como antes hasta que la autora decida activarla.
- **Tras un rechazo se puede reintentar**; una verificación aprobada no se repite.

## Pruebas

- Backend: 560 pruebas, cobertura 97,5 %, pylint 10/10, flake8 sin errores.
- Frontend: 273 pruebas, ESLint sin errores, compilación correcta.

## Pendiente

- Revisar con el tutor CP-39 (con qué servicio de Identik) y CP-40 (firma del informe).
- Reunión técnica con Identik: firma de los webhooks, reintentos, datos que conservan (Ley 25.326).
- Conectar el sandbox (T11) y probar contra el servicio real (T12). El token de API lo genera y lo carga la autora en AWS; nunca pasa por el chat ni el repositorio.
