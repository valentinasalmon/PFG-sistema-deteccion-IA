# ADR-0006: Capas de análisis como Strategy, sin puntaje global

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RF39 – RF43, RN26, RN27, RNF18

## Contexto

Existen cuatro técnicas de análisis heterogéneas y puede sumarse otra en el futuro. En el repositorio anterior las capas escribían directamente en la base de datos y existía una conclusión final que combinaba las capas.

## Decisión

- Todas las capas implementan una interfaz común: reciben la ruta de la imagen y su contexto, y devuelven un `ResultadoCapa` con nivel de indicio (0–100), anomalías, conclusión, detalle y versión.
- Las capas no acceden a la base de datos: el servicio de análisis las ejecuta y persiste los resultados.
- Una capa nueva se agrega registrándola, sin modificar las existentes.
- **No se calcula un puntaje global**: se descarta la tabla `conclusiones_finales` del repositorio anterior.

## Consecuencias

- Cada capa se prueba de forma aislada.
- La falla de una capa se captura en el servicio y se informa como "No disponible".
