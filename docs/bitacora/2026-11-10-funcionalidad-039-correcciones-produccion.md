# 2026-11-10 · 039: correcciones de producción

## Contexto

La autora integró la 038 en `main` y la probó en producción. Informó dos problemas: al escanear el QR «Análisis detallado» e iniciar sesión «solo muestra el análisis», y al crear y pagar un estudio no le llegó el correo al Administrador ni lo vio en el panel. Además avisó que compra el dominio y pidió los pasos, y que avance con los pendientes propuestos (correos con «siniestro», sensor en la integración continua, guía de usuario).

## Hecho

- **QR del análisis detallado**: el enlace del PDF agrega `detalle=completo` y la pantalla del análisis abre desplegados los resultados y el «Qué significa y datos técnicos» de cada técnica. Los PDF ya generados conservan el enlace anterior (llevan al análisis, plegado).
- **Correos con «siniestro»** para las personas de aseguradoras en los ocho correos de casos (asunto, texto y botón).
- **Trabajo «Interfaz» en la integración continua**: sensor de diseño y recorrido del abogado en computadora y celular contra un entorno levantado en GitHub Actions, con imágenes sintéticas y la cuenta de demostración. No bloquea el despliegue (no está en sus `needs`) para no frenar una corrección urgente por un problema visual; sí se ve en rojo en el Pull Request.
- **Guía de usuario** al día con la 037 y la 038, y nueva sección de administración.
- **Guía de despliegue**: pasos completos del dominio (compra en NIC Argentina o un registrador con DNS, delegación a Cloudflare, registros A, certificado, Google, DKIM y DMARC en SES, salida del modo de prueba con un texto listo para copiar).

## Diagnóstico de la aprobación de estudios

Se reprodujo en el entorno local con el código de producción, por los dos caminos (crear el estudio desde Organizaciones y desde el registro «Abogado con estudio»): al acreditarse el pago, la abogada ve «Pago recibido: falta la aprobación», el estudio aparece en Administración (debajo del tablero) y el correo al Administrador sale. Causas probables en producción:

1. **SES en modo de prueba**: solo entrega a direcciones verificadas. Si la dirección del Administrador no está en `correos_verificados` (o no confirmó el enlace de AWS), el correo no llega.
2. El listado de pendientes quedó **debajo del tablero** de Administración: hay que bajar.
3. Que el pago no se haya acreditado (el estudio queda «esperando el pago» y no aparece como pendiente).

Se le pidió a la autora confirmar qué vio la abogada después de pagar.

## Decisiones

- `detalle=completo` como parámetro y no como comportamiento por defecto: desde la plataforma, el análisis sigue plegado para no abrumar; el QR del PDF, en cambio, promete el detalle.
- La palabra se decide por el perfil de la **persona destinataria**, no por el del caso: el correo se lee con el vocabulario de quien lo recibe.

## Verificación

Pruebas del backend (correos, informes) y del frontend (análisis desplegado y plegado); flake8; ESLint; sensor de diseño y recorrido del abogado en computadora y celular contra el entorno local.

## Pendiente

- Autora: confirmar el QR con un PDF nuevo; revisar SES y Administración por la aprobación del estudio; comprar el dominio y seguir la guía.
- Ver el trabajo «Interfaz» en verde en el Pull Request de la 039.
