# 024 · Tareas

## Etapa 1 — HEIC
- [x] Especificación y plan.
- [x] Modelo, migración y detección de HEIC; vista previa JPEG.
- [x] ELA con la aclaración para HEIC; C2PA con `image/heic`.
- [x] Selector de archivos con HEIC.
- [x] Pruebas de backend y de frontend.

## Etapa 2 — QR (aprobada por el tutor)
- [x] Modelo `EnlaceCarga`, migración `a7c3e9d2b024` y repositorio.
- [x] `ServicioEnlacesCarga`: crear, cancelar, consultar y cargar; `ServicioImagenes.cargar` con `origen`.
- [x] Rutas: `POST/DELETE /api/casos/<id>/enlace-carga` (con sesión) y `GET/POST /api/carga/<token>` (públicas, sin CSRF).
- [x] QR en SVG generado en el servidor con `segno`.
- [x] Panel "Cargar desde el celular" con QR, pasos, cuenta regresiva y actualización automática.
- [x] Página del celular `/cargar/:token` con galería y cámara.
- [x] Pruebas de backend y de frontend.
- [ ] Prueba en un celular real, Android e iPhone (autora).
- [ ] *(Opcional)* Código de 6 dígitos y "compartir desde la galería".
