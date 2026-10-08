# ADR-0002: Interfaz en React y backend como API REST

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RNF10, RNF12, RNF17, RF46

## Contexto

La propuesta original servía la interfaz con plantillas Jinja2 desde Flask. Luego se decidió usar React. El sistema necesita mostrar el progreso de los análisis sin recargar la página (RF46) y una interfaz utilizable por personas no técnicas (RNF10).

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Plantillas Jinja2 | Simple, sin compilación | Interacciones dinámicas limitadas; mezcla presentación y backend |
| **React + API REST** | Interfaz dinámica; separación clara entre presentación y lógica; la API queda reutilizable | Dos proyectos para compilar; requiere cuidar CSRF y CORS |

## Decisión

El frontend es una aplicación React (Vite) servida por Nginx como archivos estáticos. Flask expone una API REST bajo `/api`, en el mismo dominio. Jinja2 se conserva **solo** para las plantillas de correos y del informe PDF.

## Consecuencias

- Las rutas de Flask devuelven JSON, nunca HTML.
- El mismo dominio para interfaz y API evita CORS en producción.
- Ninguna tecnología de la propuesta original queda sin uso: Jinja2 sigue presente.
