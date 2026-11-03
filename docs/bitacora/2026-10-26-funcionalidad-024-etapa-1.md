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

## Cambio de rumbo (mismo día)

- **La autora no quiere una plataforma móvil**: se quitaron los botones "Sacar foto" y "Elegir de la galería" de la pantalla del caso. La etapa 1 queda solo con el soporte de HEIC. El ícono `camara` se conserva para la etapa 2.
- **Propuesta final enviada al tutor:**
  - código de carga (QR y 6 dígitos);
  - "compartir desde la galería": Web Share Target (PWA) en Android y Atajo de Apple en iPhone.
  
  Quedó registrada en la investigación y en los insumos del informe final.

## Etapa 2: QR hacia la galería del celular (aprobada por el tutor)

- **Panel "Cargar desde el celular"** en la pantalla del caso:
  - QR de un enlace de un solo uso (15 minutos, solo carga en ese caso). A pedido de la autora no tiene tope de fotos: rige solo el límite de imágenes por caso del plan;
  - cuenta regresiva;
  - la lista de imágenes se actualiza sola mientras está abierto;
  - al cerrarlo, el enlace se cancela.
- **Página del celular `/cargar/:token`**: sin iniciar sesión, con "Elegir de la galería" (varias fotos, acepta HEIC) y "Sacar una foto". Usa las mismas validaciones, huella, sello en Hedera y auditoría que la carga normal (origen `celular`).
- **Seguridad**:
  - token aleatorio de 192 bits, del que solo se guarda la huella SHA-256;
  - carga a nombre de quien generó el QR, con sus permisos vigentes;
  - rutas públicas sin CSRF, porque no hay cookie de sesión;
  - la respuesta no expone datos del caso más allá del número.
- **QR en SVG** generado en el servidor con `segno`, sin bibliotecas nuevas en el frontend.
- **Calidad**:
  - backend: 476 pruebas;
  - frontend: 199 pruebas.
- **Pendiente:** prueba en un celular real (Android e iPhone).
