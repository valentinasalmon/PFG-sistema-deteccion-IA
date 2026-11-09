# 038 · Acceso compacto, pantallas a lo ancho y detalles de flujo

**Estado**: implementada (2026-11-06). **Rama**: `funcionalidad/038-acceso-compacto`. **Pedido**: la autora, con capturas de su pantalla.

## Problema

En una notebook (1366 × 768), el inicio de sesión y el registro obligaban a desplazarse: la tarjeta de alto fijo de la 037 tenía desplazamiento interno, había espacios grandes en algunos lugares y elementos pegados en otros (el título del paso contra la barra de avance). El panel verde «Revisá cada foto…» ocupaba media tarjeta también en el registro y en la verificación del correo, y los textos legales quedaban angostos.

## Alcance

- El panel de marca queda **solo en «Iniciar sesión»**; registro, recuperación, verificación del correo e invitación usan la tarjeta entera.
- Tarjetas sin alto fijo ni desplazamiento interno; espacios verticales ajustados para que cada pantalla de cuenta entre entera en 1366 × 768, con el botón de Google visible.
- Registro: opciones con el ícono al lado del título (en computadora y en celular), título del paso separado de la barra, «¿Ya tenés cuenta?» en la fila de «Siguiente» en el primer paso, correo y contraseña lado a lado y reglas de la contraseña en dos columnas.
- Términos y Privacidad más anchos en computadora (76rem), con índice de secciones y texto de largo cómodo.
- Tarjetas de un solo formulario (recuperar, restablecer, verificar y confirmar el correo) en dos columnas en computadora; títulos alineados a la izquierda.

### Segunda tanda (capturas de la autora, 2026-11-06)

- Crear el estudio desde el sistema: planes uno al lado del otro.
- **Los estudios también esperan la aprobación del Administrador** (decisión de la autora; RN38 ampliada). Rechazado un estudio, se devuelve el pago y la cuenta del abogado sigue activa.
- Invitar miembros a todo el ancho; quien crea su cuenta desde el enlace de una invitación queda dentro de esa organización al verificar el correo, también en un estudio.
- Mi perfil, la organización y Nuevo caso aprovechan el ancho en computadora (formularios en dos columnas); diseño propio en el celular.
- El QR del análisis detallado del PDF vuelve al análisis después de iniciar sesión (también con Google).
- QR del celular de un solo uso, con botón «Terminar»; otro dispositivo ve que ya se usó y la computadora se entera.
- Enlace para la persona afectada alineado; imágenes elegidas sin borde grueso y las excluidas atenuadas; casos recientes sin textos amontonados; nada solo en una fila en el celular.

## Criterios de aceptación

- [x] **CA1**: En 1366 × 768, inicio de sesión, los tres pasos del registro, recuperación y verificación del correo entran enteros en la pantalla, sin desplazamiento interno (medido con el botón de Google habilitado).
- [x] **CA2**: El panel de marca aparece solo en `/iniciar-sesion`.
- [x] **CA3**: Términos y Privacidad miden 1216 px de ancho en computadora.
- [x] **CA4**: En el celular (390 px) las opciones del registro llevan el ícono al lado del título y nada queda cortado.
- [x] **CA5**: El sensor de diseño y los recorridos de punta a punta (aseguradora, abogado en pc y celular, y los pagos de aseguradora y estudio) terminan sin problemas de diseño.

- [x] **CA6**: Al pagar, un estudio queda pendiente; el Administrador lo aprueba sin verificación de identidad o lo rechaza (se devuelve el pago y la cuenta sigue activa).
- [x] **CA7**: Quien se registra desde el enlace de una invitación queda dentro de esa organización al verificar el correo, y no de otras que lo hayan invitado.
- [x] **CA8**: Abrir `/casos/ID?etapa=analisis` sin sesión e iniciar sesión lleva al análisis (probado con contraseña; con Google, por el mismo mecanismo guardado en el navegador).
- [x] **CA9**: El QR del celular sirve para un solo dispositivo; «Terminar» lo cierra; la computadora avisa y permite mostrar uno nuevo.
- [x] **CA10**: Sensor de diseño y recorridos de punta a punta (aseguradora, abogado en pc y celular) sin problemas.

Capturas del antes y el después en [`capturas/`](capturas/).
