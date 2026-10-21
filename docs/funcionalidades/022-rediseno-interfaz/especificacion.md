# 022 · Rediseño de la interfaz y del informe PDF

**Requisitos**: RNF10 (usabilidad y accesibilidad), RF44 (informe PDF), RF43 y RN27 (indicios sin veredicto), RN29 (versiones).

## Objetivo

Dar a evidentIA una identidad visual única y quitar fricciones en todas las pantallas, sin cambiar ninguna funcionalidad. Que el informe PDF y la pantalla de resultados no admitan malentendidos.

## Criterios de aceptación

- **CA1**: todas las pantallas siguen la [guía de identidad visual](../../guias/identidad-visual.md).
- **CA2**: las pantallas de acceso muestran el panel de marca: logo dentro de las esquinas de visor y eslogan.
- **CA3**: la lista de casos tiene la búsqueda principal siempre visible y el resto de los filtros en «Más filtros». Cuando no hay resultados, muestra un mensaje con una acción.
- **CA4**: la pantalla del caso muestra arriba los pasos del flujo. El trabajo sobre la evidencia va a la izquierda; los datos y la gestión, a la derecha.
- **CA5**: los resultados del análisis usan la misma escala que el informe PDF:
  - Sin indicios: 0 %.
  - Indicios débiles: 1 % a 44 %.
  - Indicios moderados: 45 % a 69 %.
  - Indicios fuertes: 70 % a 100 %.
  - Cada imagen empieza con un resumen por capa y declara su integridad.
- **CA6**: el informe PDF sigue el orden de un informe técnico de evidencia digital:
  1. Resumen.
  2. Caso y solicitud.
  3. Evidencia analizada y cadena de custodia.
  4. Metodología y escala.
  5. Resultados.
  6. Cronología.
  7. Versiones.
  8. Limitaciones.
  9. Glosario.
- **CA7**: ningún texto emite veredictos (RN27) y las capas nunca se combinan en un puntaje.
- **CA8**: el informe, la pantalla de resultados y el correo de fin de análisis incluyen el descargo de IA y la supervisión humana (ADR-0017, RNF23 CA4).
- **CA9**: cada capa del informe muestra sus criterios, el valor de referencia sin edición y el valor obtenido (RNF23 CA5).
- **CA10**: los correos usan el diseño de marca y el remitente «evidentIA».
- **CA11**: los avisos de éxito son flotantes y se cierran solos; los errores quedan junto al campo o la sección.
- **CA12**: Panel, Perfil, Organizaciones, Organización y Administración siguen la misma estructura de cabecera y columnas.
- **CA13**: en desarrollo existe una cuenta de prueba que entra a todas las pantallas; nunca en producción.
