# 024 · Carga de imágenes desde el celular

**Requisitos**: RF53 (CA1 a CA4), RF34 · **Reglas**: RN22, RN23 · **Investigación**: [carga desde el celular](../../investigacion/2026-10-25-carga-desde-el-celular.md)

## Objetivo

Permitir subir las fotos desde el celular (Android e iOS) directamente al caso, sin pasar por WhatsApp ni por el correo, que comprimen las fotos y les borran los metadatos, y sin instalar una aplicación.

## Etapas

La propuesta enviada al tutor tiene dos partes:
- **A:** web en el celular.
- **B:** QR desde la computadora.

La etapa 1 no depende de su respuesta. La etapa 2 se hace cuando el tutor conteste.

### Etapa 1 — Web en el celular y HEIC

- [x] **CA1 (RF53 CA1)**: en un celular o una tableta, la sección de imágenes ofrece dos botones:
  - "Sacar foto", que abre la cámara trasera (`capture="environment"`);
  - "Elegir de la galería".
  
  En la computadora sigue el botón "Elegir imágenes". Las validaciones son las de RF34.
- [x] **CA3 (RF53 CA3)**: se aceptan fotos HEIC/HEIF, el formato del iPhone:
  - se detectan por la caja `ftyp` y no por la extensión;
  - el original se guarda sin convertir;
  - la vista previa se genera en JPEG.
  
  El selector lista HEIC explícitamente para que Safari entregue el original sin convertirlo.
- [x] **CA4 (RF53 CA4)**: en el celular se avisa que sacar la foto en el momento conserva más datos, y que algunos celulares quitan la ubicación al elegir la foto de la galería.
- [x] **CA5**: el análisis ELA aclara que en HEIC tiene validez limitada (comprime distinto que JPEG) e informa solo indicios débiles, igual que en PNG. Las capas de metadatos (ExifTool) y C2PA leen HEIC.
- [ ] **CA6**: prueba en un celular real, Android e iPhone (autora).

### Etapa 2 — QR desde la computadora (espera la respuesta del tutor)

- [ ] **CA2 (RF53 CA2)**: "Cargar desde el celular" muestra un QR de un solo uso. El QR:
  - vence a los 15 minutos y se puede cancelar;
  - solo permite cargar fotos en ese caso;
  - queda auditado a nombre de quien lo generó.
- [ ] Huella calculada en el celular y comparada con la del servidor (complemento propuesto).
