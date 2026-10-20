# Especificación: 011 — Capa 3 (análisis de niveles de error, ELA)

- **Rama**: `funcionalidad/011-capa-ela`
- **Estado**: Completada (pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF41; RF43 (CA1 a CA4, para esta capa); RNF23 (CA1)
- **Reglas de negocio aplicadas**: RN21, RN26, RN27, RN29
- **Casos de uso**: la parte de CU28 que ejecuta la capa 3

## Problema

Cuando se edita una parte de una foto y se vuelve a guardar en JPEG, esa parte suele tener otro "historial de compresión" que el resto. El análisis de niveles de error (ELA, *Error Level Analysis*) lo hace visible:
1. Vuelve a comprimir la imagen con una calidad conocida.
2. Mide cuánto cambia cada zona.

Las zonas que cambian mucho más o mucho menos que el resto pueden haber sido pegadas, retocadas o generadas aparte.

Es una técnica conocida y fácil de explicar, pero **débil por sí sola**: los bordes marcados, los textos, las zonas muy lisas y la recompresión de las aplicaciones de mensajería también producen diferencias. Por eso el resultado es una señal complementaria, nunca un indicio fuerte.

## Alcance

### Incluido

**Análisis (RF41)**
- La capa recomprime la imagen en JPEG con una calidad fija y mide la diferencia en bloques de la imagen.
- Compara cada bloque con los de textura parecida de la misma imagen, para no confundir bordes y detalles con ediciones.
- Señala las **regiones** cuyo nivel de error se aparta del comportamiento general, según un umbral documentado en el plan. Informa hasta tres, con su ubicación y su tamaño aproximados.
- Informa la calidad JPEG estimada del archivo, a partir de sus tablas de cuantización.

**Nivel de indicio**
- Una región que se aparta poco es un indicio **débil**; una que se aparta mucho, **moderado**. La capa nunca informa indicios fuertes ni directos.
- El nivel se calcula con el mismo método que las capas 1 y 2 y llega como máximo a 90 %. En la práctica, ELA no pasa de indicios moderados.
- Sin regiones señaladas, el nivel es 0, y la conclusión aclara que eso no descarta ediciones.

**PNG y otros casos (RF41 CA2)**
- En una imagen PNG, el resultado aclara que ELA tiene validez limitada en formatos sin pérdida, y las regiones se informan como mucho como indicios débiles.
- Una imagen demasiado chica para dividirla en bloques se informa sin nivel de indicio, con el motivo.

**Mapa ELA (RF41 CA3)**
- El resultado incluye una imagen del mapa ELA con las regiones señaladas recuadradas.
- La imagen va acompañada de la aclaración de que se trata de una señal complementaria.
- El mapa se muestra en la pantalla del análisis, con un enlace firmado que vence a los 5 minutos, y se incluye en el informe PDF.
- El mapa se guarda en el almacenamiento y se borra junto con el caso, la organización o la cuenta (RN21).

**Versiones (RN29)**: la versión de la capa, de Pillow y de NumPy, y la calidad de recompresión usada.

### Excluido

- Otras técnicas de análisis de compresión, como la doble cuantización o los fantasmas JPEG: quedan como trabajo futuro.
- Ajuste de los umbrales con un conjunto de datos etiquetado: los umbrales actuales son una propuesta para revisar con los tutores.

## Criterios de aceptación

- [x] **CA1**: Dada una imagen JPEG con una región pegada desde otra imagen, entonces la capa la señala con su ubicación, y el nivel es mayor que el de la misma imagen sin editar (RF41 CA1).
- [x] **CA2**: Dada una imagen JPEG sin editar, entonces no se señalan regiones y el nivel es 0, con la aclaración de que no descarta ediciones.
- [x] **CA3**: Dada una imagen PNG, entonces el resultado aclara la validez limitada de ELA y no pasa de indicios débiles (RF41 CA2).
- [x] **CA4**: El resultado incluye el mapa ELA con las regiones recuadradas y la aclaración de que es una señal complementaria; se ve en la pantalla y en el informe PDF (RF41 CA3).
- [x] **CA5**: El mapa se borra del almacenamiento al eliminar el caso (RN21).
- [x] **CA6**: La conclusión es un indicio con la recomendación de consultar a un profesional, sin términos de veredicto (RN27), y el resultado registra las versiones (RN29).
- [x] **CA7**: Si la imagen no se puede leer, la capa queda "No disponible" con el motivo y las demás capas siguen (RN26).

## Preguntas abiertas

- Ninguna que bloquee. Los umbrales y el texto de "¿Qué significa?" son una propuesta para revisar con los tutores.
