# 2026-10-22 — Funcionalidad 015: retención y destrucción de datos

**Rama**: `funcionalidad/015-retencion`, desde `desarrollo` con la 013, la 022 y la 014 integradas.

## Qué se hizo

- **Tarea diaria** (`flask retencion procesar` y `plataforma-retencion.timer`):
  - destruye los casos vencidos y lo audita con las huellas de los archivos;
  - avisa por correo al Responsable cuando faltan 30 días.
- **Prórroga de 1 año**: con motivo obligatorio, renovable y auditada.
- **Pantalla del caso**: muestra la fecha de eliminación y ofrece la prórroga.

## Decisiones

- **La prórroga corre el inicio del plazo un año** en lugar de guardar las prórrogas en una tabla. Evita una migración, y el historial completo queda en la auditoría.
- **El aviso sale el día exacto en que faltan 30 días.** Con una tarea diaria basta para no repetirlo, sin guardar un indicador. Si un día la tarea no corre, `Persistent=true` la ejecuta al arrancar el servidor. Si aun así se pierde el día exacto, el caso igual aparece en el panel como «Por vencer».

## Pendiente (de la autora)

- **Foto del remitente en los correos**: hoy Gmail muestra la foto de la cuenta remitente. Cuando haya dominio propio, enviar desde una dirección del dominio con el isotipo como imagen; la otra opción es BIMI, que requiere un certificado pago.
