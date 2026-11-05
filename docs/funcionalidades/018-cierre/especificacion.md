# Especificación: 018 — Cierre: usabilidad, índice de calidad y documentación final

- **Rama**: `funcionalidad/018-cierre`
- **Estado**: En curso. Los materiales están listos; faltan la prueba con participantes y la validación del tutor (CP-04)
- **Requisitos que realiza**: RNF10 (CA1), RNF11, RNF19 (CA2)
- **Reglas de negocio aplicadas**: RN27 (ningún texto emite veredictos)
- **Casos de uso**: todos los del flujo principal (crear caso, cargar imágenes, analizar, descargar el informe)

## Problema

Para cerrar el proyecto hay que demostrar tres cosas con evidencia medible:

1. Que una persona del dominio, sin capacitación, usa la plataforma sola (RNF10 CA1: al menos 5 participantes y 80 % de éxito).
2. Que el software alcanza un Índice de Calidad (QI) de 0,75 o más (RNF19 CA2). La fórmula no estaba definida (CP-04).
3. Que hay documentación para quien usa la plataforma, no solo para quien la desarrolla.

## Alcance

### Incluido
- Protocolo de la prueba de usabilidad: perfil de participantes, tareas, métricas, consentimiento, planilla de registro y cuestionario SUS en español.
- Fórmula del QI con sus componentes y pesos, y un script que la mide con las herramientas que ya usa el proyecto.
- Guía de usuario para abogados y aseguradoras.

### Excluido
- Hacer la prueba con participantes: la coordina y la hace la autora con el protocolo.
- Revisión de accesibilidad con herramientas automáticas (RNF11 CA1): se suma cuando el sistema esté en su versión final.
- Informe final del proyecto: se arma con `docs/informe-final/insumos.md`.

## Criterios de aceptación

- [x] **CA1**: Dado el protocolo, cuando la autora lo sigue, entonces puede hacer la prueba sin preparar nada más: tareas, guion, consentimiento, planilla y SUS.
- [x] **CA2**: Dado el script del QI, cuando se corre con las coberturas, entonces informa cada componente, su peso y si se cumple el umbral de 0,75.
- [x] **CA3**: Dado que todavía no hay prueba de usabilidad, cuando se calcula el QI, entonces se informa como provisorio con los pesos reescalados.
- [x] **CA4**: Dada la guía de usuario, cuando una persona la lee, entonces encuentra cómo registrarse, crear un caso, cargar imágenes, analizar, descargar y verificar el informe, sin lenguaje técnico.
- [ ] **CA5**: Dada la prueba con al menos 5 participantes, cuando se registran los resultados, entonces la tasa de éxito es de 80 % o más y el SUS promedio queda cargado en el QI.
- [ ] **CA6**: Dado el tutor, cuando revisa la fórmula, entonces la valida o pide cambios (CP-04).

## Preguntas abiertas

- CP-04: validar con el tutor los componentes y pesos del QI.
- Quiénes participan de la prueba y en qué fechas (lo define la autora).
