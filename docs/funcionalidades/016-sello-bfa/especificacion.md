> **Reemplazada (2026-10-25):** la autora decidió usar Hedera en lugar de BFA ([ADR-0018](../../arquitectura/decisiones/0018-sello-de-tiempo-en-hedera.md)). La funcionalidad 023 reutiliza los estados, la pantalla y el reintento de esta funcionalidad, y cambia solo el sellador.

# 016 · Sello de tiempo en Blockchain Federal Argentina

**Requisitos**: RF37, RNF20 (CA1) · **Regla**: RN23

## Objetivo

Acreditar que cada imagen existía, con esa huella exacta, en una fecha determinada. Para eso se registra su huella SHA-256 en Blockchain Federal Argentina (BFA) sin enviar el archivo, y el resultado se muestra en la pantalla del caso y en el informe PDF.

## Criterios de aceptación

- [x] **CA1 (RF37 CA1)**: al cargar una imagen se pide el sello en segundo plano y queda su estado:
  - `pendiente`: todavía no se pudo pedir;
  - `enviado`: BFA entregó el recibo y falta que lo incluya en un bloque;
  - `sellado`: confirmado;
  - `fallido`: se agotaron los reintentos.
- [x] **CA2 (RF37 CA2)**: un sello confirmado guarda la referencia (bloque) y la fecha, y ambas aparecen en el informe PDF y en la tarjeta de la imagen.
- [x] **CA3 (RF37 CA3)**: si BFA no responde, la tarea programada reintenta cada 15 minutos durante unas 24 horas. Cargar o analizar nunca falla por el sello.
- [x] **CA4 (RF37 CA4)**: el sellador es intercambiable (Strategy):
  - `bfa`: el servicio real;
  - `simulado`: desarrollo y pruebas, siempre marcado como «Sello simulado, sin validez»;
  - `desactivado`.
- [x] **CA5**: en producción el sello nunca es simulado: la configuración solo admite `bfa` o `desactivado`.
