# Plan técnico: 030 — Revisión y refuerzo de la seguridad

| Parte | Archivos | Detalle |
|---|---|---|
| Límites de pedidos | `infraestructura/nginx/limites.conf` (en `conf.d`), `infraestructura/nginx/api.conf` (en `snippets`), `instalar_configuracion.sh` | Zonas `acceso` (20/min, solo POST), `google` (20/min), `publica` (60/min) y `api` (20/s), con ráfagas. Además, 30 conexiones simultáneas por IP. Las dos configuraciones del sitio incluyen el mismo `api.conf` |
| Respuesta 429 | `api.conf` | `error_page 429` devuelve JSON `{mensaje, codigo: "demasiados_pedidos"}`, que el cliente muestra sin cambios |
| Cabeceras | `infraestructura/nginx/plataforma.conf` | `Permissions-Policy` y `Cross-Origin-Opener-Policy`, con `always` |
| Dependencias | `.github/workflows/integracion-continua.yml`, `frontend/package.json` | Trabajo `seguridad`: `pip-audit -r backend/requirements.txt` y `npm audit --omit=dev --audit-level=high`. Ejecución semanal (lunes). Vitest pasa a 4.1.12, undici a 8.12.3 y zod a 4.6.7 |
| Nginx en la integración continua | mismo *workflow* | Instala Nginx, genera un certificado autofirmado y ejecuta `nginx -t` con las dos plantillas |
| PDF | `backend/app/informes/plantillas.py` | `URLFetcher(allowed_protocols={"data"}, allow_redirects=False)` |

## Por qué en Nginx y no en Flask

- El límite se aplica antes de que el pedido ocupe un proceso de Gunicorn.
- No hace falta otra dependencia (Flask-Limiter).
- La configuración viaja con el código y se instala en cada despliegue.

En desarrollo no hay límite, y el bloqueo de cuenta tras 5 contraseñas incorrectas (RNF01 CA3) sigue siendo la protección de la aplicación.

## Verificación

- Nginx 1.24 local con un backend falso:
  - 429 después de la ráfaga en `POST /api/sesion`;
  - `GET /api/sesion` sin límite;
  - 41 cargas seguidas aceptadas;
  - cuerpo JSON y cabeceras presentes en el 429.
- Pruebas automáticas:
  - `pruebas/unitarias/test_seguridad_pdf.py` (5);
  - prueba de interfaz del 429 en `acceso.test.jsx`.
