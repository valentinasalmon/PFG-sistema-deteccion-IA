# ADR-0007: Español en código, commits y ramas

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RNF16, RNF20, RNF21

## Contexto

La autora requiere que todo el proyecto esté en español: especificación, código, comentarios, commits y ramas.

## Decisión

- Identificadores en español, sin tildes ni ñ (`anio`, `contrasenia`), para evitar problemas de codificación.
- Conventional Commits con **tipos traducidos** (`funcionalidad`, `correccion`, `documentacion`, etc.), validados con una configuración propia de commitlint.
- Ramas con prefijos en español (`funcionalidad/`, `correccion/`, `documentacion/`).
- Se exceptúan los nombres impuestos por bibliotecas y archivos convencionales (`README.md`, `requirements.txt`, `package.json`).

## Consecuencias

- Las herramientas que esperan tipos en inglés (por ejemplo, generadores de changelog) requieren configuración adicional.
- La configuración por defecto de commitlint no sirve: se escribe una propia.
