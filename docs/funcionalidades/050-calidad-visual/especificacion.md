# 050 · Calidad visual de la portada y del registro

**Estado**: en curso (2026-11-23). **Rama**: `interfaz/calidad-visual`. **Pedido**: la autora (2026-11-18 y 2026-11-23): «en Qué miramos estaría bueno poner un video o alguna animación de todo lo que se hace», «cuando te registrás, el aceptar los términos está en otra página y eso no debería ser así» y «revisá los cambios de diseño que se debían aplicar y no se aplicaron».

## Problema

- «Qué miramos» explica las cuatro capas solo con texto: no se ve qué hace el sistema sobre una foto.
- En el registro con Google, la aceptación de los Términos era un paso aparte («Últimos detalles»), a diferencia del registro común, donde está junto al correo y la contraseña.

## Alcance

- **Animación propia** en «Qué miramos», con forma de plano: una foto de un choque dentro de las esquinas de visor del logo, una línea que la recorre y, por turnos, la marca rotulada de cada mirada sobre lo que examina (01 metadatos, 02 C2PA, 03 ELA, 04 red neuronal). La mirada que se muestra se resalta en la lista; al pasar el puntero por una de la lista, la animación la muestra y se pausa.
- Es decorativa (la lista dice lo mismo): oculta para lectores de pantalla, sin videos ni bibliotecas nuevas (SVG y CSS), avanza solo mientras se ve y queda quieta, con todas las marcas, si la persona pidió «reducir movimiento».
- **Registro con Google**: los Términos van en el último paso, junto a lo último que se completa (los datos o el plan). Ya no hay paso aparte.

## Criterios de aceptación

- [x] **CA1**: La animación se ve en computadora (a la izquierda, fija mientras se recorre la lista) y en celular (entre el título y la lista), sin superponer rótulos.
- [x] **CA2**: Con «reducir movimiento», no hay movimiento; sin estar a la vista, no avanza.
- [x] **CA3**: En el registro con Google, la casilla de los Términos está en la misma pantalla que los datos (o el plan) y no se puede crear la cuenta sin marcarla.
- [x] **CA4**: Sensor de diseño, sensor de accesibilidad, sensor de teclado y recorridos del abogado en computadora y celular sin problemas.
- [ ] **CA5**: La autora revisa la animación en producción.
