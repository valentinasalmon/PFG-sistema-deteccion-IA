# Especificación: 034 — Pulido de UX/UI de todo el sistema

- **Rama**: `funcionalidad/034-pulido-ux`
- **Estado**: Aprobada (mockups v3 validados por la autora el 2026-10-29; el detalle se pule pantalla por pantalla)
- **Requisitos que realiza**: RNF10 (usabilidad y accesibilidad), RF19, RF20
- **Reglas de negocio aplicadas**: RN27; ADR-0017
- **Casos de uso**: todos los de la interfaz

## Problema

La autora pidió un sistema limpio, sin fricciones, orientado a la usuaria principal (la abogada que lleva el caso) y digno de presentar. El relevamiento de las 15 rutas en computadora y celular (2026-10-29) encontró:

- pantallas sin salida (por ejemplo, la carga de fotos desde el celular sin botón para terminar, o el caso sin un paso siguiente claro);
- textos redundantes: el panel de marca y el descargo largo repetidos en todas las pantallas;
- el caso dividido en cajas y pestañas en lugar de un recorrido;
- botones, campos y avisos con tamaños y lugares distintos;
- en el celular, partes que se superponen (la barra de selección sobre el título) o que ocupan media pantalla.

## Alcance

### Incluido
- **Sistema de componentes**: jerarquía de botones con estados, campos de 40 px de alto y ancho acotado, avisos flotantes arriba a la derecha (arriba al centro en el celular) con X, diálogos centrados con X, Esc y clic afuera, esqueletos de carga, vacíos con ilustración y acción, colores e íconos con significado.
- **Acceso y registro a pantalla completa**, con el logo y el nombre arriba de una tarjeta centrada.
- **El caso como flujo vertical continuo**: Imágenes → Análisis → Informe unidos por una línea; el paso actual abierto, los terminados plegados con su resumen y los pendientes con cuándo se habilitan.
- **Cada pantalla con una acción principal y una salida** (mapa de salidas de los mockups).
- **Inicio** con «Seguí donde lo dejaste» y contadores con ícono y color; **Casos** con búsqueda instantánea y filtros; **organización** en pestañas; **perfil** con filas de una acción; **administración** con tablero y aprobaciones juntas.
- **Novedades**: buscador «Buscar o ir a…» con Ctrl K y comparador deslizable entre la foto y su mapa de error.
- **Portada** con ilustraciones propias y animaciones que se apagan con «reducir movimiento».
- **Microsoft Clarity** para que la autora revise el uso antes del lanzamiento: se activa solo si se configura su identificador, con enmascarado estricto. No muestra nada a los usuarios.

### Excluido
- Cambios del modelo de datos o de las reglas de negocio.
- Precios de los planes (a confirmar por la autora).

## Criterios de aceptación

- [ ] **CA1**: Toda pantalla tiene una acción principal visible y una forma de volver o seguir, en computadora y en celular.
- [ ] **CA2**: Ninguna pantalla se desborda ni recorta contenido a 390 px de ancho.
- [ ] **CA3**: Los avisos flotantes aparecen arriba, se cierran con X y se van solos; los diálogos aparecen centrados y se cierran con X, Esc o clic afuera.
- [ ] **CA4**: En el caso, Imágenes, Análisis e Informe se ven como un flujo vertical con el estado de cada paso.
- [ ] **CA5**: Acceso y registro se muestran a pantalla completa, con la tarjeta centrada y solo el logo con el nombre.
- [ ] **CA6**: Los resultados siguen diciendo que son indicios y no veredictos (RN27) y el pie del sistema lo recuerda en una línea.
- [ ] **CA7**: Ctrl K abre el buscador desde cualquier pantalla interna; Esc lo cierra.
- [ ] **CA8**: Clarity se carga solo con el identificador configurado y con enmascarado estricto.
- [ ] **CA9**: Las animaciones se apagan con «reducir movimiento» y todo se puede usar con el teclado (RNF10).

## Preguntas abiertas

- Detalle fino pantalla por pantalla, a revisar con la autora después de esta tanda.
- Identificador del proyecto de Clarity (lo crea la autora).
