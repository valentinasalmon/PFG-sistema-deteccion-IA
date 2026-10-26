# 025 · Informe breve y por rubro

**Requisitos**: RF44 (CA1, CA2), RF54 · **Reglas**: RN27, RN29 · **Decisiones**: ADR-0017

## Objetivo

Los usuarios analizan imágenes todo el tiempo: un informe de 8 o 9 páginas no es sostenible. El PDF tiene que ser breve, autosuficiente y hablar el idioma de quien lo pide (abogado o aseguradora). Además, tiene que distinguir los resultados deterministas de los probabilísticos.

## Criterios de aceptación (aprobados por la autora el 2026-10-26)

- [x] **CA1 (orden)**: el informe tiene estas secciones, en este orden:
  1. caso y solicitud;
  2. evidencia y cadena de custodia, en una sola tabla (imagen, huella, integridad y sello), con la cronología en una línea;
  3. escala de lectura (solo la tabla);
  4. resultados deterministas y probabilísticos;
  5. resultados por imagen;
  6. qué hacer ahora;
  7. verificación del informe (026);
  8. al final, el recuadro con el aviso de alcance y el descargo.

  *(El 2026-10-27 se quitaron los puntos 4 y 6; ver los ajustes al final.)*
- [x] **CA2 (sin lo que sobraba)**: se quitaron el resumen inicial, la metodología, el uso previsto, las limitaciones y el glosario. Las versiones de los componentes (RN29) quedan como una línea dentro del recuadro final.
- [x] **CA3 (resultados breves)**: por cada técnica, una fila con:
  - su nombre y si es **determinista** o **probabilística**;
  - el nivel de indicio;
  - lo que encontró en una oración, más hasta dos hallazgos relevantes.
  
  El mapa ELA aparece chico y solo si encontró algo.
- [x] **CA4 (deterministas y probabilísticos)**: una sección explica la diferencia:
  - **Determinista**: comprueba hechos verificables; con el mismo archivo da siempre lo mismo y un tercero puede comprobarlo. Son la integridad, los metadatos y C2PA.
  - **Probabilístico**: es una estimación con umbrales o modelos; puede señalar una imagen sin ediciones o no detectar una edición. Son ELA y la red neuronal.
  
  Se aclara que un indicio determinista pesa más.
- [x] **CA5 (por rubro, RF54)**: el título, la intro, la etiqueta de la referencia (Expediente o N.° de siniestro) y los pasos de "qué hacer ahora" cambian según el perfil de quien pidió el análisis.
- [x] **CA6 (diseño)**: no tiene números de sección ni saltos de página forzados (todo corre de seguido), y tiene más espacio entre líneas, párrafos y filas.
- [x] **CA7 (RN27)**: ningún texto fijo emite veredictos.

## Ajustes del 2026-10-27 (pedido de la autora, después de probarlo)

- [x] **CA8 (sin cortes)**: ningún bloque se corta entre páginas. Si una sección, la cabecera de una imagen, una técnica o el recuadro final no entran, pasan enteros a la hoja siguiente. Sigue sin haber saltos forzados.
- [x] **CA9 (resultados más descriptivos)**: por cada técnica se muestra:
  - **qué revisó**;
  - **qué encontró**: la conclusión completa, sin la recomendación genérica, que se dice una vez al final;
  - hasta 3 hallazgos que la conclusión no mencione;
  - hasta 4 datos técnicos relevantes (por ejemplo, fabricante, modelo y software, o firmante y herramienta, o calidad JPEG estimada);
  - el mapa ELA si encontró algo.
  
  La versión breve queda en la plataforma; el PDF es más detallado, pero no técnico.
- [x] **CA10**: se quitaron la sección "Resultados deterministas y probabilísticos" y "Qué hacer ahora". Cada técnica conserva su etiqueta de tipo, explicada en una línea al empezar los resultados.
- [x] **CA11**: las versiones de los componentes ya no aparecen en el PDF. Se siguen guardando con cada análisis (RN29), y la versión de la plataforma se ve en la página pública de verificación (029).
