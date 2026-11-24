# 050 · Calidad visual de la portada y del registro

**Estado**: en curso (2026-11-23; animación pospuesta el 2026-11-24). **Rama**: `interfaz/calidad-visual`. **Pedido**: la autora (2026-11-18 y 2026-11-23): «en Qué miramos estaría bueno poner un video o alguna animación de todo lo que se hace», «cuando te registrás, el aceptar los términos está en otra página y eso no debería ser así» y «revisá los cambios de diseño que se debían aplicar y no se aplicaron».

## Problema

- «Qué miramos» explica las cuatro capas solo con texto: no se ve qué hace el sistema sobre una foto.
- En el registro con Google, la aceptación de los Términos era un paso aparte («Últimos detalles»), a diferencia del registro común, donde está junto al correo y la contraseña.

## Alcance

- **Animación de «Qué miramos»: pospuesta** (2026-11-24). Se probaron dos versiones, un plano con marcas y un «video» de 16:9 con capítulos. La autora no aprobó ninguna: «no me gusta ese video, no integres eso, después vemos cómo lo solucionamos». El código queda guardado en la rama `interfaz/video-miradas`, sin integrar, para retomarlo con una dirección nueva.
- **Registro con Google**: los Términos van en el último paso, junto a lo último que se completa (los datos o el plan). Ya no hay paso aparte.

## Criterios de aceptación

- [ ] **CA1**: (pospuesto) Animación de «Qué miramos» aprobada por la autora.
- [x] **CA3**: En el registro con Google, la casilla de los Términos está en la misma pantalla que los datos (o el plan) y no se puede crear la cuenta sin marcarla.
- [x] **CA4**: Sensor de diseño, sensor de accesibilidad, sensor de teclado y recorridos del abogado en computadora y celular sin problemas.
- [ ] **CA5**: La autora revisa la animación en producción.
