# 038 · Acceso compacto: todo en una pantalla

**Estado**: implementada (2026-11-06). **Rama**: `funcionalidad/038-acceso-compacto`. **Pedido**: la autora, con capturas de su pantalla.

## Problema

En una notebook (1366 × 768), el inicio de sesión y el registro obligaban a desplazarse: la tarjeta de alto fijo de la 037 tenía desplazamiento interno, había espacios grandes en algunos lugares y elementos pegados en otros (el título del paso contra la barra de avance). El panel verde «Revisá cada foto…» ocupaba media tarjeta también en el registro y en la verificación del correo, y los textos legales quedaban angostos.

## Alcance

- El panel de marca queda **solo en «Iniciar sesión»**; registro, recuperación, verificación del correo e invitación usan la tarjeta entera.
- Tarjetas sin alto fijo ni desplazamiento interno; espacios verticales ajustados para que cada pantalla de cuenta entre entera en 1366 × 768, con el botón de Google visible.
- Registro: opciones con el ícono al lado del título (en computadora y en celular), título del paso separado de la barra, «¿Ya tenés cuenta?» en la fila de «Siguiente» en el primer paso, correo y contraseña lado a lado y reglas de la contraseña en dos columnas.
- Términos y Privacidad más anchos en computadora (76rem).

## Criterios de aceptación

- [x] **CA1**: En 1366 × 768, inicio de sesión, los tres pasos del registro, recuperación y verificación del correo entran enteros en la pantalla, sin desplazamiento interno (medido con el botón de Google habilitado).
- [x] **CA2**: El panel de marca aparece solo en `/iniciar-sesion`.
- [x] **CA3**: Términos y Privacidad miden 1216 px de ancho en computadora.
- [x] **CA4**: En el celular (390 px) las opciones del registro llevan el ícono al lado del título y nada queda cortado.
- [x] **CA5**: El sensor de diseño y los recorridos de punta a punta (aseguradora, abogado en pc y celular, y los pagos de aseguradora y estudio) terminan sin problemas de diseño.

Capturas del antes y el después en [`capturas/`](capturas/).
