# 2026-10-22 — Funcionalidad 016: sello de tiempo en Blockchain Federal Argentina

**Rama**: `funcionalidad/016-sello-bfa`, desde `desarrollo` con la 015 integrada.

## Qué se hizo

- Cliente del servicio de sello de tiempo de BFA, un sellador simulado y su elección por configuración (Strategy).
- Estados del sello por imagen, primer intento al cargar y una tarea cada 15 minutos que reintenta y confirma.
- El sello aparece en la tarjeta de la imagen y en el informe PDF: en la sección de evidencia y cadena de custodia, en lugar de «todavía no disponible».

## Decisiones

- Solo se envía la huella SHA-256, nunca la imagen (RF37).
- El simulado se marca siempre como tal, para que un informe nunca muestre un sello falso como real. En producción la configuración no admite el modo simulado.
- El modo real queda desactivado hasta comprobar la conexión: desde el entorno del agente no se llega a `tsa.bfa.ar`.

## Pendiente (con la autora)

1. Probar la conexión con BFA desde su computadora y desde el servidor (Session Manager).
2. Si responde, activar `sello_tiempo = "bfa"` en `terraform.tfvars`, aplicar y regenerar el entorno del servidor.
3. Si el formato de respuesta de BFA no coincide con el esperado, ajustar `SelladorBFA` con la salida real.
