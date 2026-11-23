# 050 · Calidad visual de la portada y del registro

**Estado**: en curso (2026-11-23). **Rama**: `interfaz/calidad-visual`. **Pedido**: la autora (2026-11-18 y 2026-11-23): «en Qué miramos estaría bueno poner un video o alguna animación de todo lo que se hace», «cuando te registrás, el aceptar los términos está en otra página y eso no debería ser así» y «revisá los cambios de diseño que se debían aplicar y no se aplicaron».

## Problema

- «Qué miramos» explica las cuatro capas solo con texto: no se ve qué hace el sistema sobre una foto.
- En el registro con Google, la aceptación de los Términos era un paso aparte («Últimos detalles»), a diferencia del registro común, donde está junto al correo y la contraseña.

## Alcance

- **Un «video» propio en «Qué miramos»** (segunda versión, pedido de la autora del 2026-11-23: «armá un video, bien copado»), de 16:9 y unos 21 segundos en bucle:
  - una cámara recorre la foto de un choque, dibujada en línea dentro de las esquinas de visor del logo, y se acerca a lo que examina cada mirada;
  - **01** muestra la ficha EXIF, línea por línea; **02**, el sello C2PA que «estampa»; **03**, el mapa de calor del ELA sobre la abolladura; **04**, la red que se teje sobre toda la imagen;
  - termina con la tarjeta del informe: «Indicios, no veredictos» (RN27).
- Tiene subtítulos, botón de pausa y una barra de avance por escena. La lista de miradas funciona como capítulos: cada tarjeta lleva el video a su escena, y la escena que se muestra queda resaltada.
- Es decorativo (la lista dice lo mismo): el lienzo queda oculto para los lectores de pantalla y el botón de pausa sí se anuncia. No usa archivos de video ni bibliotecas (SVG y CSS), corre solo mientras se ve y, si la persona pidió «reducir movimiento», queda quieto en el informe.
- **Registro con Google**: los Términos van en el último paso, junto a lo último que se completa (los datos o el plan). Ya no hay paso aparte.

## Criterios de aceptación

- [x] **CA1**: El video se ve en computadora (título a la izquierda, video a la derecha, capítulos debajo), en tableta y en celular, sin rótulos cortados ni superpuestos.
- [x] **CA2**: Con «reducir movimiento», no hay movimiento; sin estar a la vista, no avanza; se puede pausar (WCAG 2.2.2) y la pausa conserva lo que faltaba de la escena.
- [x] **CA3**: En el registro con Google, la casilla de los Términos está en la misma pantalla que los datos (o el plan) y no se puede crear la cuenta sin marcarla.
- [x] **CA4**: Sensor de diseño, sensor de accesibilidad, sensor de teclado y recorridos del abogado en computadora y celular sin problemas.
- [ ] **CA5**: La autora revisa la animación en producción.
