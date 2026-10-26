# 024 · Carga de imágenes desde el celular

**Requisitos**: RF53 (CA1 a CA4), RF34 · **Reglas**: RN22, RN23 · **Investigación**: [carga desde el celular](../../investigacion/2026-10-25-carga-desde-el-celular.md)

## Objetivo

Permitir subir las fotos desde el celular (Android e iOS) directamente al caso, sin pasar por WhatsApp ni por el correo, que comprimen las fotos y les borran los metadatos, y sin instalar una aplicación.

## Etapas

El 2026-10-26 la autora decidió que la plataforma **no** se adapte para usarse en el celular: las fotos se suben desde el celular hacia un caso abierto en la computadora. La propuesta de cómo hacerlo se consultó con el tutor (ver la investigación): código de carga con QR y 6 dígitos, y "compartir desde la galería" con Web Share Target (PWA) en Android y un Atajo de Apple en iPhone. La etapa 1 no depende de esa respuesta.

### Etapa 1 — Fotos HEIC del iPhone

- [x] **CA3 (RF53 CA3)**: se aceptan fotos HEIC/HEIF, el formato del iPhone:
  - se detectan por la caja `ftyp` y no por la extensión;
  - el original se guarda sin convertir;
  - la vista previa se genera en JPEG.
  
  El selector lista HEIC explícitamente para que el navegador entregue el original sin convertirlo.
- [x] **CA5**: el análisis ELA aclara que en HEIC tiene validez limitada (comprime distinto que JPEG) e informa solo indicios débiles, igual que en PNG. Las capas de metadatos (ExifTool) y C2PA leen HEIC.
- [x] Se descartaron los botones "Sacar foto" y "Elegir de la galería" en la pantalla del caso: la autora no quiere una plataforma móvil.

### Etapa 2 — QR desde la computadora hacia la galería del celular (aprobada por el tutor el 2026-10-26)

- [x] **CA2 (RF53 CA2)**: en la pantalla del caso, "Cargar desde el celular" muestra un código QR de un enlace de un solo uso. El enlace:
  - vence a los 15 minutos y se cancela al cerrar el panel o al generar otro;
  - solo permite subir fotos a ese caso (no ver, bajar ni borrar);
  - carga a nombre de quien lo generó, con sus permisos vigentes;
  - admite hasta 30 fotos;
  - en la base guarda solo la huella SHA-256 del token.
- [x] **CA2b**: la página del celular abre sin iniciar sesión y ofrece "Elegir de la galería" (varias fotos) y "Sacar una foto". Cada foto pasa por las mismas validaciones, huella, sello en Hedera y auditoría de la carga normal; la auditoría marca el origen `celular`.
- [x] **CA2c**: mientras el panel está abierto, la lista de imágenes de la computadora se actualiza sola cada 4 segundos.
- [x] **CA4 (RF53 CA4)**: la página del celular avisa que sacar la foto en el momento conserva más datos.
- [ ] **CA6**: prueba en un celular real, Android e iPhone (autora).
- [ ] *(Ampliación opcional)* Código de 6 dígitos y "compartir desde la galería" (Web Share Target en Android, Atajo de Apple en iPhone): quedan como mejora futura.
