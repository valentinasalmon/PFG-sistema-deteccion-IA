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

# Etapa 2 — QR

- **`EnlaceCarga`**:
  - campos `huella_token` (único), `id_caso`, `id_usuario`, `creado_en`, `vence_en`, `revocado_en` y `cargas`;
  - se borra con el caso (relación con cascada);
  - el token es `secrets.token_urlsafe(24)` (192 bits) y solo se guarda su huella.
- **`ServicioEnlacesCarga`**:
  - `crear` usa `ServicioImagenes.caso_para_cargar` (mismos permisos y estados que la carga), cancela los enlaces anteriores del mismo usuario en el caso y audita `imagen.enlace_carga`;
  - `cargar` delega en `ServicioImagenes.cargar(..., origen="celular")` y suma la carga al enlace. No hay tope por enlace: la página del celular muestra el lugar libre del plan (`ServicioImagenes.lugar_disponible`).
- **Rutas**: las públicas (`carga_celular_bp`) quedan exentas de CSRF, porque no usan cookies de sesión y el token es la credencial. Solo devuelven el nombre y la huella de la foto subida.
- **QR**: `segno` genera un SVG como `data:` URI, que la CSP ya admite (`img-src data:`). No hace falta ninguna biblioteca en el frontend.
- **Frontend**:
  - `CargaDesdeCelular`: botón, panel con QR, pasos, cuenta regresiva y actualización de la lista cada 4 s; al cerrarlo, `DELETE`;
  - `PaginaCargaCelular`: ruta pública `/cargar/:token` dentro de la disposición de acceso, con galería (varias fotos, HEIC) y cámara (`capture="environment"`).
