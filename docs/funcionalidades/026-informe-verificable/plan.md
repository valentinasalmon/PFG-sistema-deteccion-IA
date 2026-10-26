# 026 · Plan técnico

- **Modelo `Informe`**: `codigo_verificacion` (único) y las columnas `sello_*` iguales a las de `Imagen`. `TIPO_SELLO = "informe"`. Migración `b8d4f1e2c026`.
- **`ServicioInformes.generar`**:
  - crea el código (`secrets`, alfabeto sin 0/O/1/I/L, 12 caracteres);
  - agrega a los datos del PDF el QR (`utilidades/qr.py`), el código legible y la URL;
  - calcula la huella del PDF final, con el QR incluido, y deja el sello `pendiente`.
- **Sellado**: `ServicioInformes.sellar` se llama después de confirmar, tanto en `ServicioAnalisis._finalizar` como en `regenerar`. `ServicioSellos` sella cualquier objeto con `huella` y `sello_*`, y su tarea procesa también los informes (`RepositorioInformes.con_sello_en_curso`).
- **API pública**: `GET /api/verificacion?codigo=` o `?huella=`, sin sesión. `esquemas/verificacion.py` solo devuelve la fecha, la huella y el sello.
- **Frontend**:
  - `PaginaVerificarInforme` (ruta pública);
  - `utilidades/verificacion.js` calcula el SHA-256 con Web Crypto;
  - enlace "Verificar un informe" en el pie;
  - código y sello en `SeccionInformes`.
- **Pruebas**:
  - backend: código y sello del informe; verificación por código, con y sin guiones, y por huella; 404 sin datos del caso; bloque de verificación en el PDF;
  - frontend: coincide, no coincide, búsqueda por huella y PDF desconocido.
