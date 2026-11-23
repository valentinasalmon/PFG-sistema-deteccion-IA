# 048 · Verificación independiente en Hedera

**Estado**: en curso (2026-11-23). **Rama**: `hedera/verificacion-independiente`. **Pedido**: la autora: «debemos poner en alguna parte para que una persona revise desde Hedera si eso es real; siempre verificamos desde evidentIA nomás y eso no sirve».

## Problema

La huella de cada imagen y de cada informe se sella en Hedera, una red pública, pero hoy la única forma práctica de comprobarlo es la página de verificación de evidentIA. Para una prueba, eso exige confiar en la misma plataforma que emitió el informe: si evidentIA no estuviera o la página se equivocara, nadie podría comprobar nada por su cuenta.

## Alcance

- **En el PDF**, un recuadro «Verificar sin evidentIA» con la red y el tema público de Hedera, el enlace al tema en HashScan (el explorador público de Hedera, que no depende de evidentIA) y los pasos: calcular la huella SHA-256 del PDF con la computadora y buscar ese valor entre los mensajes del tema de la fecha del informe. Las imágenes ya muestran su referencia de sello.
- **Una guía pública** (`/verificar/sin-evidentia`) con los comandos para calcular la huella en Windows, Mac y Linux, cómo abrir el tema en HashScan y cómo leer el mensaje (`{"v":1,"tipo":…,"sha256":…}`).
- **En la página de verificación**, un recuadro que invita a comprobarlo en Hedera sin depender de evidentIA, con el enlace a la guía y al tema.
- La red y el tema se publican: ya son públicos por naturaleza (cualquiera los ve en HashScan) y son la base de la verificación independiente. La cuenta y su clave siguen sin mostrarse.
- **Decisión de la autora (2026-11-23)**: la plataforma se queda en la red de prueba de Hedera (*testnet*), también para la defensa. Se actualizan la especificación, los pendientes y las versiones.

## Criterios de aceptación

- [ ] **CA1**: Con el sello activo, el PDF muestra la red, el tema, el enlace a HashScan y los pasos; con el sello simulado o desactivado, no los muestra.
- [ ] **CA2**: La guía pública explica cómo calcular la huella en Windows, Mac y Linux y cómo encontrarla en HashScan, sin iniciar sesión.
- [ ] **CA3**: Siguiendo la guía con un informe real del entorno de producción, la huella calculada en la computadora coincide con la del mensaje de Hedera (prueba de la autora).
- [ ] **CA4**: La página de verificación enlaza la guía y el tema.
- [ ] **CA5**: Pruebas automáticas, sensores de diseño, accesibilidad y teclado, y recorridos en computadora y celular.
