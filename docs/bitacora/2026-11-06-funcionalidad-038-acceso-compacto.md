# 2026-11-06 · 038: acceso compacto

## Contexto

La autora integró la 037 en `desarrollo`. El PR de `desarrollo` a `main` (#83) estaba abierto con la integración continua en verde pero sin fusionar; por eso los cambios no llegaban a producción (el despliegue solo corre al entrar en `main`). Se le explicó cómo fusionarlo.

Después mandó capturas de su notebook: el inicio de sesión y el registro obligaban a desplazarse dentro de la tarjeta, había espacios grandes y elementos pegados, y el panel verde aparecía también en el registro y en la verificación del correo.

## Hecho

- Panel de marca solo en «Iniciar sesión»; el resto de las pantallas de cuenta usan la tarjeta entera.
- Sin alto fijo ni desplazamiento interno; espacios verticales ajustados. Medido en 1366 × 768 con el botón de Google habilitado: inicio de sesión 615 px, registro paso 1 685 px, pasos 2 y 3 ~610 px, verificación 505 px (todas entran).
- Registro más compacto: ícono al lado del título en cada opción (también en el celular, donde el paso 1 pasó de 1271 a 1073 px), título del paso separado de la barra, «¿Ya tenés cuenta?» en la fila de «Siguiente», correo y contraseña lado a lado.
- Términos y Privacidad a 76rem en computadora.

## Decisiones

- **Se abandona el «mismo alto para todas las tarjetas» de la 037** (60 × 42 rem con desplazamiento interno): en una notebook obligaba a desplazarse, que es justo lo que la autora quiere evitar. Se mantiene el mismo ancho (60rem) y cada tarjeta toma el alto de su contenido.

## Verificación

ESLint y 280 pruebas de Vitest; sensor de diseño sin problemas; recorridos de la aseguradora y del abogado (pc y celular) y de los pagos de aseguradora y estudio (pc y celular) con «Sin problemas de diseño».

## Pendiente

Que la autora fusione el PR #83 a `main` para desplegar la 037, y después esta rama.
