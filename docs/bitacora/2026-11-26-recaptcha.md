# 2026-11-26 · reCAPTCHA de Google en los formularios públicos (051)

## Qué se hizo

- reCAPTCHA invisible, por puntaje, en el registro, el inicio de sesión, el pedido de recuperación y el reenvío de la verificación.
- El backend evalúa cada token con la API v1 de evaluaciones de Google Cloud.
- La clave del sitio llega al navegador desde el backend; la clave de API queda solo en Parameter Store.
- Fila en `/estado`, párrafo en la Política de Privacidad y permisos de la política de seguridad de contenido de Nginx.
- Guía para la autora: [configurar-recaptcha.md](../guias/configurar-recaptcha.md).

## Decisiones tomadas

- **API de evaluaciones (Google Cloud) y no `siteverify`.** Google marcó como obsoleta la documentación de reCAPTCHA clásico. Hoy reCAPTCHA es parte de Google Cloud Fraud Defense y las claves nuevas se crean en un proyecto de Google Cloud; se usa el mismo proyecto del inicio con Google.
- **Por puntaje (invisible) y no la casilla «No soy un robot».** No agrega pasos al registro, que la autora pidió acortar.
- **Si Google no responde, se deja pasar** (con registro en el log). La disponibilidad del registro y del inicio de sesión pesa más; el inicio de sesión ya tiene el bloqueo por intentos.
- **El token va en una cabecera** (`X-Recaptcha`), así no cambian los esquemas de los formularios.
- **No se protegen la carga desde el celular ni el registro con Google**: el primero ya usa un enlace secreto de un solo uso y el segundo ya pasó por Google.
- **El script de Google se carga solo al enviar** uno de esos formularios: no pesa en la portada ni manda datos a Google de quien solo mira.

## Problemas encontrados y cómo se resolvieron

- El entorno del agente no podía abrir la documentación de Google: la autora había aprobado los dominios, pero faltaba `docs.cloud.google.com`, al que redirige `cloud.google.com`. Se agregó y se leyó la documentación vigente antes de escribir el código.
- Las páginas de Google se contradicen sobre si hace falta un medio de pago: quedó como CP-44.

## Pendientes

- La autora crea las claves y prueba en producción (051 CA5), y decide sobre la facturación (CP-44).
