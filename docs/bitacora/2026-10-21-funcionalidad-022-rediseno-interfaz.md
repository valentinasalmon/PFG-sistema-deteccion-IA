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

## Segunda entrega (pedido de la autora)

- **Acceso**: panel verde bosque con el logo blanco centrado dentro de las esquinas de visor y el eslogan. El formulario va en una tarjeta sobre fondo gris claro, para que no quede todo blanco.
- **Casos**: búsqueda principal en una sola fila, «Más filtros» desplegable, filas en las que se puede tocar toda la fila y estado vacío con acción.
- **Nuevo caso**: tipos de caso en dos tarjetas y una columna lateral «Qué sigue» con los cuatro pasos del flujo.
- **Caso**: cabecera con número, lugar y pasos del flujo (cargar imágenes, analizar, descargar el informe). La evidencia va a la izquierda; los datos, el estado, los accesos, la transferencia y la eliminación, a la derecha. Los datos se editan con «Editar los datos».
- **Resultados del análisis**: integridad verificada, resumen por capa en palabras y porcentaje, «Cómo leer los niveles» y «¿Qué significa?» en cada capa. Usan la misma escala que el PDF.
- **Informe PDF**: reescrito con el orden de un informe técnico de evidencia digital:
  - resumen;
  - caso y solicitud;
  - evidencia y cadena de custodia (formato, tamaño, quién cargó cada imagen y cuándo, SHA-256 y su verificación);
  - metodología y escala;
  - resultados;
  - cronología;
  - versiones;
  - limitaciones;
  - glosario.
- **Guía de identidad visual**: [docs/guias/identidad-visual.md](../guias/identidad-visual.md), referida desde CLAUDE.md.

## Pendiente

- Cambios que pida la autora sobre las capturas.
- Plantillas de correo con el nuevo diseño.
- Contrastar el informe con las recomendaciones de Federico Miskinich: no están registradas en el repositorio. Hay que pedírselas a la autora.
- Avisos breves flotantes.
