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

### Etapa 2 — Carga desde el celular (espera la respuesta del tutor)

- [ ] **CA2 (RF53 CA2)**: código de carga de un solo uso, con QR y 6 dígitos. El código:
  - vence a los 15 minutos y se puede cancelar;
  - solo permite subir fotos a ese caso;
  - queda auditado a nombre de quien lo generó;
  - tiene un límite de intentos fallidos.
- [ ] Página de carga para el celular, sin iniciar sesión.
- [ ] Android: "Compartir con evidentIA" con Web Share Target API (PWA: manifest con `share_target` y service worker).
- [ ] iPhone: Atajo de Apple "Enviar a evidentIA" en la hoja para compartir (acción "Obtener contenido de URL"). Hay que verificar que suba el original.
- [ ] Página de ayuda "Compartir desde la galería".
