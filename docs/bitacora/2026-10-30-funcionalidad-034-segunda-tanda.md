# 2026-10-30 — Funcionalidad 034: pulido de UX/UI, segunda tanda

Rama `funcionalidad/034-pulido-ux-segunda-tanda`, desde `desarrollo` después de integrar la primera tanda (#53) y de desplegar en AWS (#57).

## Qué se hizo

- **Inicio:**
  - «Seguí donde lo dejaste» abre el caso activo actualizado más recientemente con su próximo paso (seguir con las fotos, ver el avance o ver los resultados);
  - contadores con ícono y color por estado;
  - sin casos, «Tu primer caso» con los tres pasos y la ilustración de la carpeta; las invitaciones pendientes se siguen mostrando.
- **Casos:** los filtros se aplican al instante (la búsqueda, 400 ms después de dejar de escribir), sin botón «Buscar». La lista vacía dice por qué («Ningún caso coincide con «…»») y ofrece quitar los filtros o crear un caso.
- **Nuevo caso:** fecha y lugar en la misma fila; expediente y descripción a un clic («Agregar expediente y descripción»); el botón «Crear y cargar las fotos» lleva directo a la etapa de imágenes.
- **Buscador «Buscar o ir a…»** (Ctrl K o ⌘ K, y botón en el menú): atajos según el rol y búsqueda de casos por número, expediente o lugar. Se maneja con flechas, Enter y Esc.
- **Comparador** deslizable entre la foto y su mapa de niveles de error en la etapa Análisis. Se usa con mouse, dedo o teclado.
- **Vacíos y errores con ilustración y salida** (`EstadoVacio`): Casos, Inicio, Organizaciones, invitación vencida, enlace de fotos inválido y página no encontrada («Volver» e «Ir al inicio»).
- **Microsoft Clarity configurable** (`utilidades/clarity.js`):
  - se carga solo si la compilación trae `VITE_CLARITY_ID` (variable `CLARITY_ID` de GitHub en el despliegue);
  - enmascara toda la página;
  - la CSP de Nginx permite solo sus dominios;
  - la guía de despliegue tiene los pasos para activarlo y apagarlo.

## Decisiones

- **Clarity se configura al compilar, no con Terraform:** la interfaz se compila en GitHub Actions, así que el identificador es una variable de GitHub. No es secreto, porque queda a la vista en la página. Se descartó sumarlo a Terraform: no aportaba nada y agregaba un paso.
- **Enmascarado de toda la página** (`data-clarity-mask` en el `body`), además del modo estricto del panel de Clarity: los casos tienen datos personales y fotos de terceros (Ley 25.326).
- **CSP abierta a Clarity de forma fija:** se permite `*.clarity.ms` y `c.bing.com` aunque Clarity no esté activo. Es más simple que generar la cabecera según la variable y el riesgo es bajo, porque solo se habilitan dominios de Microsoft para ese fin.
- **Se mantiene un solo «Nuevo caso» en el menú** (decisión de la 028). El de «Tu primer caso» y el de los vacíos son la acción de esa pantalla, no un acceso duplicado.
- **El buscador Ctrl K no busca casos para la administradora**, que no ve casos (028); a ella le ofrece solo sus atajos.

## Cuestiones abiertas

- **CP-37:** antes de cargar `CLARITY_ID`, sumar Clarity a la política de privacidad. Decisión de la autora.

## Calidad

- Frontend: 255 pruebas (12 nuevas), eslint sin observaciones y compilación correcta.
- Revisión en el navegador de Inicio (con casos y vacío), Casos sin resultados, Nuevo caso, el buscador y la página no encontrada, en computadora (1280 px) y celular (390 px), sin desbordes. Se corrigieron en el momento los contadores del celular, que partían el texto, y los botones del formulario, que se salían de la tarjeta.

## Pendiente

- Organización en pestañas, perfil y administración (T06).
- Resto de las páginas públicas (verificar informe, estado) (T07).
- Pulido fino pantalla por pantalla con la autora.
