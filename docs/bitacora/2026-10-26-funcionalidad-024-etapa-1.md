# 2026-10-26 — Funcionalidad 024, etapa 1: carga desde el celular y HEIC

## Qué se hizo

- **Fotos HEIC/HEIF del iPhone** (`pillow-heif`):
  - se aceptan y se detectan por la caja `ftyp`, aunque vengan con extensión `.jpg`;
  - el original se guarda sin convertir y la vista previa se genera en JPEG;
  - una migración amplía el formato permitido en la base.
- **En pantallas táctiles**, botones "Sacar foto" (abre la cámara trasera) y "Elegir de la galería", más un aviso sobre la ubicación de las fotos.
- **ELA** aclara su validez limitada en HEIC y solo informa indicios débiles.
- **Se corrigió una prueba de retención** que fallaba solo entre las 23 y las 24 UTC.
- **Calidad**:
  - backend: 472 pruebas y cobertura del 97,6 %;
  - frontend: 197 pruebas.

## Decisiones

- **El selector de archivos lista HEIC explícitamente**: así Safari entrega el original y no una conversión que podría perder metadatos.
- **El botón de cámara aparece solo en dispositivos táctiles** (`pointer: coarse`). En la computadora, `capture` no tiene efecto.
- **La etapa 2 (QR) espera la respuesta del tutor**, como se acordó con la autora.

## Pendiente

- Prueba en un celular real, Android e iPhone.
- Etapa 2: QR de un solo uso y huella calculada en el celular.
