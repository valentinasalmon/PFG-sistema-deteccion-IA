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

## Segunda tanda: capturas de la autora del sistema por dentro

**Hecho** (commits en `funcionalidad/038-acceso-compacto`):

- Corrección pedida por la autora: las tarjetas se habían agrandado sin reacomodar su contenido. Páginas legales con índice de secciones y texto de largo cómodo; tarjetas de un formulario en dos columnas; títulos a la izquierda.
- Planes lado a lado al crear el estudio.
- **Decisión de la autora: los estudios también esperan la aprobación del Administrador.** Se aplica igual que con las aseguradoras, sin verificación de identidad; si se rechaza, se devuelve el pago y la cuenta sigue activa. RN38 actualizada. Las cuentas de prueba y de demostración (terminal) quedan aprobadas al crearse.
- Invitaciones: quien se registra desde el enlace queda dentro al verificar el correo (antes solo en aseguradoras). Se marca la invitación usada para no sumar a la persona a otras organizaciones sin que lo elija. Probado de punta a punta con el correo real del entorno local.
- Mi perfil, la organización y Nuevo caso aprovechan el ancho; las pestañas no muestran flechas.
- **Error encontrado**: el QR del análisis detallado perdía `?etapa=analisis` al pasar por el inicio de sesión y terminaba en el informe. Corregido (también con Google).
- **QR del celular de un solo uso con «Terminar»**: atado al celular que sube la primera foto (no al abrir la página: en la prueba, una consulta repetida dejaba afuera al propio celular). La computadora nota el fin, cierra el QR y avisa.
- Detalles: enlace para la persona afectada alineado, imágenes elegidas sin borde grueso, casos recientes en dos líneas, celular sin elementos solos en una fila.

**Verificación**: backend 574 pruebas (97,5 %), flake8 y pylint 10/10; frontend ESLint y 283 pruebas; sensor de diseño y recorridos (aseguradora, abogado en pc y celular) sin problemas; QR y vuelta al análisis probados de punta a punta.

**Pendiente**: correos con «siniestro» para las aseguradoras; Safari y Firefox reales (autora).

