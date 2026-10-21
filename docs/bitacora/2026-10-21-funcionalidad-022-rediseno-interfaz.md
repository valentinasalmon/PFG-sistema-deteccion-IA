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

## Tercera entrega: entrevista con Federico Miskinich (22/10/2026)

- **Entrevista**: documentada en [docs/investigacion/](../investigacion/2026-10-02-entrevista-federico-miskinich.md), con una tabla de qué se hizo con cada recomendación.
- **Marco normativo**: [ADR-0017](../arquitectura/decisiones/0017-marco-normativo-y-supervision-humana.md) toma como referencia el Reglamento europeo de IA y la ISO/IEC 42001, con la persona en el circuito.
- **Informe PDF**:
  - descargo de IA en el recuadro inicial;
  - tabla «Criterio / Referencia sin edición / Valor obtenido» en cada capa (la capa ELA ahora guarda su desvío máximo);
  - nueva sección «Uso previsto y supervisión humana».
- **Pantalla de resultados**: recuadro «Herramienta auxiliar».
- **Correos**: diseño de marca (logo, título, botón azul y pie con el eslogan) y remitente «evidentIA». El remitente en AWS cambia con `terraform apply` (guía de despliegue).
- **Especificación**: RNF23 suma CA4 y CA5. Quedan abiertas CP-22 (peritos), CP-23 (alternativas a ELA) y CP-24 (tipos de caso de aseguradoras).
- **Entorno local**: [guía para levantar el proyecto](../guias/levantar-en-local.md), con tareas y depuración de VS Code en `.vscode/`.

## Cuarta entrega (22/10/2026)

- **CP-22, CP-23 y CP-24**: descartadas por la autora. Se quitó a peritos y criminalistas de los destinatarios del informe.
- **Cuenta de prueba**: `flask --app wsgi administracion cuenta-de-prueba` crea o restablece `prueba@evidentia.local` / `Prueba12345`. La cuenta queda verificada y Administradora, con un estudio jurídico. Está rechazada en producción y tiene pruebas.
- **Avisos flotantes**: todo aviso de éxito aparece abajo a la derecha y se cierra a los 6 segundos o con su botón. Los que traen instrucciones o enlaces (cambio de contraseña, cambio de correo, copia de datos) siguen en su lugar.
- **Pantallas rediseñadas**:
  - Panel: acciones en la cabecera y dos columnas.
  - Perfil: tarjeta de la cuenta con el visor e índice de secciones.
  - Organizaciones: tarjetas en grilla con ícono y estado vacío.
  - Organización: cabecera, miembros e invitaciones a la izquierda, datos y salida a la derecha.
  - Administración: cabecera con bajada.
  - Botones de formulario a su ancho natural.
- **Guías**: paso a paso del remitente en AWS (Terraform, Session Manager, verificación) y cuenta de prueba en la guía local.

## Pendiente

- Cambios que pida la autora sobre las capturas.
- Plantillas de correo con el nuevo diseño.
