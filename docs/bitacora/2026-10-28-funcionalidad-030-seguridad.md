# 2026-10-28 — Revisión y refuerzo de la seguridad (030)

## Qué se hizo

- **Límites de pedidos por IP en Nginx**, con respuesta 429 en JSON que la interfaz muestra como cualquier error:
  - acceso: 20 por minuto, solo envíos;
  - Google: 20 por minuto;
  - páginas públicas: 60 por minuto;
  - resto de la API: 20 por segundo.
- **Cabeceras nuevas**: `Permissions-Policy` y `Cross-Origin-Opener-Policy`.
- **Trabajo `seguridad` en la integración continua**: `pip-audit`, `npm audit` y `nginx -t` de las dos plantillas. Corre en cada Pull Request y cada lunes, y el despliegue depende de él.
- **Dependencias**: sin vulnerabilidades en producción. En desarrollo se actualizaron vitest (4.1.12), undici y zod.
- **PDF**: WeasyPrint solo incrusta recursos `data:` (defensa contra SSRF).
- **Revisión según OWASP Top 10** en `docs/arquitectura/seguridad.md`, y búsqueda de secretos en todo el historial: sin hallazgos reales.
- **Calidad**:
  - backend: 520 pruebas, cobertura del 97,6 %, pylint 10/10;
  - frontend: 213 pruebas.

## Decisiones

- **Límites en Nginx y no en Flask**: frenan el pedido antes de ocupar Gunicorn, no suman dependencias y viajan con el despliegue. En desarrollo no hay límite; el bloqueo de cuenta sigue siendo la protección de la aplicación.
- **El límite de acceso cuenta solo los POST**: `GET /api/sesion` se consulta en cada pantalla.
- **Se audita solo lo que llega a producción** para frenar el despliegue. Las herramientas de desarrollo se revisaron y actualizaron a mano.
- **Sin WAF ni doble factor**: quedan como riesgos aceptados y trabajo futuro, documentados.

## Pendiente

- Se activa en el próximo despliegue (PR de `desarrollo` a `main`). Después, comprobar la nota en securityheaders.com (T09).
- Probado con Nginx 1.24 local y un backend falso; falta la prueba en el servidor real.
