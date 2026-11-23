# 2026-11-23 · Calidad visual: animación de «Qué miramos» y Términos en el registro con Google (050)

## Qué se hizo

- **Animación de «Qué miramos»**: un plano propio en SVG, con la foto de un choque dentro de las esquinas de visor del logo, una línea que la recorre y la marca rotulada de cada mirada por turnos. La mirada activa se resalta en la lista y se puede elegir pasando el puntero.
- **Registro con Google**: los Términos dejan de ser un paso aparte y van en el último paso, como en el registro común.
- Rama `interfaz/calidad-visual` llevada al día con `main` (no tenía trabajo propio).

## Decisiones tomadas

- **SVG y CSS en lugar de un video.** Pesa unos pocos kilobytes, se ve nítido en cualquier pantalla, toma los colores de la identidad visual y se puede quedar quieto con «reducir movimiento». Un video sumaba peso a la portada y no se adapta al modo de movimiento reducido.
- **Diseño propio.** La página que pasó la autora se tomó como referencia de estilo (plano con marcas rotuladas), no se copió nada.
- **Decorativa para lectores de pantalla.** La lista de al lado dice lo mismo; repetirlo sería ruido.
- **Solo avanza a la vista.** Con `IntersectionObserver`, el reloj se detiene cuando la sección no se ve, para no gastar batería.

## Problemas encontrados y cómo se resolvieron

- Los rótulos de metadatos y C2PA quedaban encima de las esquinas del visor, y el de ELA sobre la línea de la red: se movieron por fuera del visor y al costado del poste.
- El recorrido del abogado falla con la cuenta por defecto en el entorno local del agente, porque esa cuenta es Administradora; se corrió con la cuenta de demostración (`RECORRIDO_CORREO`).

## Pendientes

- Revisión de la autora en producción (050 CA5).
- Cobro con Mercado Pago (049): la documentación oficial sigue sin abrirse desde el entorno del agente.
