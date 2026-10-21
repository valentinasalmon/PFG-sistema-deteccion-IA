# 2026-10-21 — Funcionalidad 022: rediseño de la interfaz (primera entrega)

## Qué se hizo

- Se aplicó a todas las pantallas la dirección visual elegida por la autora: base «Visor» (correo, confirmaciones y avisos), íconos de trazo redondeados de la dirección «Iris» y azul `#2F5DA8` de la dirección «Expediente digital» para acciones, enlaces y foco.
- Nueva pantalla de acceso (ingreso, registro por perfil, recuperación): panel de marca con el logo, el isotipo dentro de las esquinas de visor y el eslogan «Tu primera línea de defensa contra el fraude visual».
- Encabezado con el logo, menú con íconos, iniciales del usuario y botón para cerrar sesión.
- Hoja de estilos reescrita sin cambiar los nombres de las clases: tipografías Sora y Figtree servidas por la propia aplicación (la política de seguridad de contenidos no permite fuentes externas), radio de 10 px, áreas táctiles de 44 px, avisos con ícono, error junto al campo, línea de escaneo durante el análisis y movimiento reducido si el sistema lo pide.
- No se cambió ninguna funcionalidad: las 191 pruebas del frontend pasan sin modificaciones.

## Decisiones

- El verde lima del logo se usa solo para la marca y el visor, porque sobre fondo claro no llega al contraste mínimo para texto ni para el foco.
- En el celular el menú muestra solo los íconos y el texto queda disponible para los lectores de pantalla.

## Pendiente

- Cambios que pida la autora sobre las capturas.
- Plantillas de correo con el nuevo diseño.
- Reordenar la pantalla del caso (hoy es una columna larga) y sumar avisos breves flotantes.
