# 051 · reCAPTCHA de Google en los formularios públicos

**Estado**: implementada, falta probarla con las claves reales (2026-11-26). **Rama**: `integraciones/recaptcha`. **Pedido**: la autora (2026-11-18 y 2026-11-24): «agregá reCAPTCHA de Google» y «que las variables no estén en el frontend».

## Problema

El registro, el inicio de sesión, la recuperación de la contraseña y el reenvío de la verificación se pueden enviar sin una sesión. Un programa automático podría usarlos para crear cuentas falsas, probar contraseñas o mandar correos a terceros desde la plataforma.

## Alcance

- **reCAPTCHA invisible por puntaje** (Google Cloud Fraud Defense, API v1 de evaluaciones). La persona no tiene que tildar nada: el navegador pide un token al enviar el formulario y el backend lo evalúa con Google.
- **Formularios protegidos**: registro, inicio de sesión, pedido de recuperación y reenvío del correo de verificación.
  - **No se protege la carga desde el celular**: el enlace ya es un secreto de un solo uso, atado al dispositivo, y cada foto sería una evaluación más.
  - **No se protege el registro con Google**: Google ya autenticó a la persona.
- **Regla**: se rechaza si falta el token, si no es válido, si es de otra acción o si su puntaje es menor que `RECAPTCHA_UMBRAL` (0,5 por defecto, lo que recomienda Google).
- **Si Google no responde, se deja pasar**, y queda registrado en el log. Una caída de Google no puede impedir registrarse o entrar; el inicio de sesión sigue protegido por el bloqueo tras intentos fallidos.
- **Nada en el frontend**:
  - la clave del sitio, que es pública, se pide al backend (`GET /api/recaptcha/configuracion`), no se compila en la interfaz;
  - la clave de API vive solo en Parameter Store, como SecureString;
  - sin las tres claves queda desactivada y todo funciona igual.
- El script de Google se carga recién al enviar uno de esos formularios: la portada y el resto de la plataforma no lo descargan.
- **Estado en `/estado`**: «Activo» o «Sin configurar».
- **Privacidad**: la Política de Privacidad informa el uso de reCAPTCHA y enlaza las condiciones de Google (Ley 25.326). La política de seguridad de contenido de Nginx permite los scripts y marcos de `www.google.com/recaptcha/` y `www.gstatic.com/recaptcha/`.

## Criterios de aceptación

- [x] **CA1**: Con reCAPTCHA activo, los cuatro formularios rechazan sin token, con un token inválido, de otra acción o con puntaje bajo (400, `verificacion_humana`, mensaje en español), y aceptan con un token bueno.
- [x] **CA2**: Si Google no responde, el formulario sigue y queda registrado en el log.
- [x] **CA3**: Sin configurar, no se carga el script de Google, no se manda cabecera y todo funciona como antes.
- [x] **CA4**: `/estado` muestra si está activo; la Política de Privacidad lo informa.
- [ ] **CA5**: Probado con las claves reales en producción (la autora, con la [guía](../../guias/configurar-recaptcha.md)): el registro y el inicio de sesión funcionan y en la consola de Google aparecen las evaluaciones. **No verificado todavía.**
- [ ] **CA6**: Decisión sobre la facturación de Google Cloud (CP-44).
