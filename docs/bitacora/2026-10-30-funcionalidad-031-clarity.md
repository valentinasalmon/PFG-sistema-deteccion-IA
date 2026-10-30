# 2026-10-30 — Funcionalidad 031: Microsoft Clarity instalado

## Qué se hizo

- La autora creó el proyecto de Clarity y pidió instalarlo. El identificador (`z5vsmarsef`) queda como constante en `frontend/src/utilidades/clarity.js`, sobre la carga condicional de la 034.
- Clarity se carga **solo en la compilación de producción**: en desarrollo y en las pruebas no se carga, para no mezclar sesiones de prueba con las reales.
- Se mantiene el enmascarado de toda la página (`data-clarity-mask` en el `body`) y la CSP de Nginx abierta solo a los dominios de Clarity. La CSP se instala sola en cada despliegue (`instalar_configuracion.sh`).
- Se quitó del workflow la variable `CLARITY_ID` de GitHub, que ya no hace falta.
- Guía de despliegue: cómo ver los datos y cómo apagarlo.

## Decisiones

- **El identificador va en el código y no en una variable de GitHub:** no es secreto, porque Clarity lo publica en cada página, y así no hace falta otro paso de configuración. Se descartó el fragmento HTML original (script en línea), que la CSP bloquearía (`script-src 'self'`). Además, cargarlo desde el código permite enmascarar antes de que arranque.

## Verificación

- Compilación de producción: el script `https://www.clarity.ms/tag/z5vsmarsef` se inyecta y el `body` queda con `data-clarity-mask="true"`.
- Pruebas de Clarity (5) y lint.

## Pendiente

- **CP-37:** mencionar Clarity en la política de privacidad. Decisión de la autora; el agente redacta el párrafo si lo aprueba.
- Elegir **Masking → Strict** en el panel de Clarity (refuerzo, la autora).
