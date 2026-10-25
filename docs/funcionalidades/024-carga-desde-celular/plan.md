# 024 · Plan técnico (etapa 1: HEIC)

- **Formato HEIC**:
  - `FORMATO_HEIC` en el modelo, con su tipo MIME `image/heic`;
  - migración `f6b2a1d4c024`, que amplía `ck_imagenes_formato`;
  - `detectar_formato` reconoce la caja `ftyp` con marca HEIC, o una HEIF genérica (`mif1`/`msf1`) con HEIC entre las compatibles. AVIF queda afuera.
- **Lectura**: `pillow-heif` registra el lector de HEIF en Pillow, en `utilidades/imagenes.py` y en `analisis/ela.py`, que corre en el trabajador. ExifTool ya lee HEIC y C2PA recibe `image/heic`.
- **ELA**: la aclaración de validez limitada se generaliza a todo formato que no sea JPEG, con un texto específico para HEIC.
- **Frontend**:
  - el selector de `SeccionImagenes` lista HEIC/HEIF;
  - el texto de formatos menciona HEIC.
  
  Los botones de cámara para pantallas táctiles se quitaron por decisión de la autora; el ícono `camara` queda para la página de carga de la etapa 2.
- **Pruebas**:
  - detección de HEIC, AVIF y HEIF genérico;
  - vista previa JPEG de un HEIC;
  - carga de un HEIC por la API;
  - ELA en HEIC;
  - el selector acepta HEIC.
- **Corrección de paso**: la prueba del aviso de retención a 30 días fallaba si corría entre las 23 y las 24 UTC; el vencimiento de prueba ahora queda a las 23:59.
