# ADR-0017: Marco normativo de referencia y supervisión humana

- **Estado**: aceptada
- **Fecha**: 2026-10-22
- **Origen**: [entrevista a Federico Miskinich](../../investigacion/2026-10-02-entrevista-federico-miskinich.md) (02/10/2026)

## Contexto

evidentIA produce indicios sobre imágenes que pueden terminar en un reclamo o en un proceso judicial. Si la herramienta parece reemplazar al perito, peritos y criminalistas la van a cuestionar. Además, sin un marco reconocido, su auditabilidad puede ponerse en duda.

## Decisión

1. **Marco de referencia**: se toman como guía de auditabilidad y gobernanza:
   - el Reglamento (UE) 2024/1689 de Inteligencia Artificial, en especial la supervisión humana y la transparencia;
   - la norma ISO/IEC 42001, sistema de gestión de IA.

   No se declara certificación ni cumplimiento formal: son el marco con el que se diseñan los controles.
2. **Persona en el circuito**:
   - la plataforma es una herramienta auxiliar;
   - ninguna salida es un veredicto (RN27);
   - la decisión final la toma una persona.
3. **Descargo obligatorio**: el informe, la pantalla de resultados y el correo de fin de análisis aclaran que el resultado es parcial, automatizado (con técnicas de IA) y que no reemplaza el criterio de un perito.
4. **Transparencia sin revelar los algoritmos**: cada capa publica en el informe sus umbrales y los valores obtenidos. El algoritmo interno no se describe.
5. **Trazabilidad determinista**:
   - huella SHA-256 al cargar cada archivo y verificación antes de analizarlo;
   - auditoría de cada acción;
   - versiones de cada componente en el informe (RN29);
   - más adelante, el sello de tiempo en la Blockchain Federal Argentina (016).

## Consecuencias

- RNF23 suma los criterios CA4 (descargo) y CA5 (umbrales y valores obtenidos).
- Toda funcionalidad nueva que muestre resultados tiene que respetar los puntos 2 a 4.
- Una capa nueva (por ejemplo, la red neuronal de la 012) tiene que definir su fila de «referencia sin edición / valor obtenido» en `_criterios()` del informe.
