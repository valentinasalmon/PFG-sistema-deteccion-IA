# Guía de identidad visual de evidentIA

Esta es la dirección elegida por la autora el 21/10/2026. Toda pantalla nueva la sigue, sin excepciones.

Se tomó:
- de la dirección «Visor», la base: correo, confirmaciones y avisos;
- de la dirección «Iris», los íconos de trazo redondeados;
- de la dirección «Expediente digital», el azul.

## Marca

- **Nombre**: evidentIA.
- **Eslogan**: «Tu primera línea de defensa contra el fraude visual».
- **Logos**: están en `frontend/public/marca/`. En el informe PDF se usa una copia liviana, `backend/app/plantillas/informes/logo.png`.
- **Elemento por el que se recuerda la plataforma**: las esquinas de visor en verde lima (clase `.visor`). Enmarcan lo que se examina: el logo en el acceso, la imagen elegida, el estado vacío.

## Color (tokens en `frontend/src/estilos/global.css`)

| Uso | Token | Valor |
|---|---|---|
| Texto y títulos | `--tinta` | #14201A |
| Texto secundario | `--tinta-2` | #4E5B54 |
| Acciones, enlaces y foco | `--azul` | #2F5DA8 |
| Fondo | `--fondo` | #F3F5F4 |
| Panel de marca | `--bosque` | #17291F |
| Marca y visor (nunca para texto) | `--lima` | #A4CB3E |

La escala de indicios usa siempre estas bandas, con el nombre escrito además del color. En la pantalla son las clases `.nivel--*`; en el PDF, las clases `nivel-*`.

- **Sin indicios**: gris.
- **Indicios débiles**: amarillo pálido.
- **Indicios moderados**: ámbar.
- **Indicios fuertes**: naranja oscuro.

El verde nunca representa «auténtica».

## Tipografía y medidas

- **Fuentes**: Sora 700/800 en los títulos y Figtree en los textos. Se sirven desde la propia aplicación, porque la política de seguridad no permite fuentes externas. El PDF usa DejaVu Sans.
- **Radio**: 10 px en cajas, botones y campos; 6 px en etiquetas.
- **Áreas táctiles**: botones y campos de 44 px o más (48 px en formularios).
- **Contenido**: hasta 75 rem de ancho. Las pantallas de trabajo usan dos columnas: el trabajo a la izquierda (`.dos-columnas__principal`) y los datos y la gestión a la derecha (`.dos-columnas__lateral`).
- **Aire**: 1,5 rem entre bloques y 2,5 rem arriba del contenido.

## Interacción

- **Botones**: un solo botón principal azul por zona. El secundario va con borde y el terciario como «fantasma». En formularios y confirmaciones: Cancelar a la izquierda, acción principal a la derecha.
- **Formularios**: etiqueta siempre visible, ayuda debajo y el error junto al campo con su ícono.
- **Avisos**: llevan ícono, de éxito, error o información. Los errores usan `role="alert"` y quedan junto a lo que los causó.
- **Avisos de éxito**: son flotantes, abajo a la derecha. Se cierran a los 6 segundos o con su botón. Si traen instrucciones o enlaces, se usa `<Aviso tipo="exito" flotante={false}>`.
- **Pantallas de trabajo**: cabecera (título, bajada y acción principal) y dos columnas: el trabajo a la izquierda, los datos y la gestión a la derecha. La zona de riesgo va siempre al final de la columna derecha.
- **Movimiento**:
  - las esquinas del visor se encuadran al aparecer;
  - una línea de escaneo recorre el progreso del análisis;
  - las pantallas entran con un desplazamiento leve;
  - todo se desactiva si el sistema pide movimiento reducido.
- **Íconos**: `componentes/Icono.jsx`, de trazo de 2 px, decorativos (`aria-hidden`) y siempre acompañados de texto. Nunca se usan emojis.
- **Textos de análisis**: indicios y recomendación de consultar a un perito. Nunca veredictos (RN27).
