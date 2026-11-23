# 2026-11-23 · Calidad visual: animación de «Qué miramos» y Términos en el registro con Google (050)

## Qué se hizo

- **Video de «Qué miramos»**: la primera versión era un plano con marcas. La autora pidió algo «bien copado», como un video, y se rehízo como un video de 16:9 en SVG y CSS:
  - una cámara se acerca a la ficha EXIF, al sello C2PA, al mapa de calor del ELA y a la red sobre toda la imagen, y termina con la tarjeta del informe;
  - tiene subtítulos, botón de pausa y barra de avance;
  - las cuatro tarjetas de la lista son capítulos.
- **Registro con Google**: los Términos dejan de ser un paso aparte y van en el último paso, como en el registro común.
- Rama `interfaz/calidad-visual` llevada al día con `main` (no tenía trabajo propio).

## Decisiones tomadas

- **SVG y CSS en lugar de un video.** Pesa unos pocos kilobytes, se ve nítido en cualquier pantalla, toma los colores de la identidad visual y se puede quedar quieto con «reducir movimiento». Un video sumaba peso a la portada y no se adapta al modo de movimiento reducido.
- **Diseño propio.** La página que pasó la autora se tomó como referencia de estilo (plano con marcas rotuladas), no se copió nada.
- **Decorativa para lectores de pantalla.** La lista de al lado dice lo mismo; repetirlo sería ruido.
- **Pausa obligatoria (WCAG 2.2.2).** Todo movimiento automático de más de 5 segundos tiene que poder pausarse; la pausa guarda lo que faltaba de la escena, así la barra y la escena siguen juntas.
- **Solo avanza a la vista.** Con `IntersectionObserver`, el reloj se detiene cuando la sección no se ve, para no gastar batería.

## Problemas encontrados y cómo se resolvieron

- En las capturas por escena se vieron cuatro problemas y se corrigieron:
  - el barrido del escáner tapaba la foto: se lo hizo más angosto y más tenue;
  - en los acercamientos se veían restos de las otras escenas: las marcas inactivas quedan ocultas;
  - el rótulo del ELA quedaba cortado: se cambió el encuadre de la cámara;
  - en el informe, los rótulos quedaban debajo de la tarjeta: en esa escena se ocultan, porque la tarjeta ya los dice.
- Los sensores marcaron tres problemas y se corrigieron:
  - los capítulos medían menos de 44 px de alto para tocar;
  - el foco de los capítulos no se veía;
  - la tarjeta del informe, al estar oculta, se salía 13 px del video en el celular.
- No se pudo abrir la página de referencia (fox-tienda) desde el entorno del agente: el estilo se tomó de la descripción de la autora y de su archivo de skills (movimiento con «reducir movimiento», celular primero, sin trabas).
- El recorrido del abogado falla con la cuenta por defecto en el entorno local del agente, porque esa cuenta es Administradora; se corrió con la cuenta de demostración (`RECORRIDO_CORREO`).

## Pendientes

- Revisión de la autora en producción (050 CA5).
- Cobro con Mercado Pago (049): la documentación oficial sigue sin abrirse desde el entorno del agente.
