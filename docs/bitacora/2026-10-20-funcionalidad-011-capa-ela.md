# 2026-10-20 — Funcionalidad 011: capa 3, análisis de niveles de error (ELA)

## Qué se hizo

Se agregó la **capa 3** del análisis.
- Recomprime la imagen en JPEG.
- Compara, bloque por bloque, cuánto cambia cada zona respecto de las de textura parecida.
- Señala las regiones que se apartan del resto.

El resultado incluye un **mapa ELA** con esas regiones recuadradas:
- se ve en la pantalla del análisis;
- va incrustado en el informe PDF;
- se borra junto con el caso.

Documentos: [especificación](../funcionalidades/011-capa-ela/especificacion.md), [plan](../funcionalidades/011-capa-ela/plan.md) y [tareas](../funcionalidades/011-capa-ela/tareas.md). La rama `funcionalidad/011-capa-ela` parte de `desarrollo` con la 017 integrada.

- **Método documentado** (ver el plan):
  - recompresión al 90 % y bloques de 16 × 16 píxeles;
  - corrección por textura en 10 clases;
  - desvíos robustos, con 4 desvíos para marcar un bloque y 10 para un indicio moderado;
  - regiones de al menos 6 bloques, uniendo los que están a 2 bloques o menos;
  - hasta 3 regiones informadas.
- **Nunca más que indicios moderados**: ELA es una señal complementaria. En PNG, como mucho indicios débiles, con la aclaración de su validez limitada.
- **Calidad JPEG estimada** a partir de las tablas de cuantización.
- **El motor ahora admite imágenes en los resultados**:
  - la columna `clave_imagen` (migración `b3e1c0a7d911`);
  - el guardado en el almacenamiento;
  - los enlaces firmados de 5 minutos;
  - la inclusión en el informe y el borrado con el caso.

  Sirve también para capas futuras.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 Región pegada | Empalme sintético: una región moderada en la ubicación donde se pegó; nivel mayor que el original | Cumplido |
| CA2 Sin edición | Original sintético e imágenes de Gemini del TIF: 0 % | Cumplido |
| CA3 PNG | Indicios solo débiles, con la aclaración | Cumplido |
| CA4 Mapa | Prueba del mapa con recuadro rojo; enlace en el detalle; PDF con el mapa incrustado | Cumplido |
| CA5 Borrado | Al eliminar el caso se borra el archivo del mapa | Cumplido |
| CA6 Textos y versiones | Sin términos de veredicto; versión con Pillow, NumPy y la calidad de recompresión | Cumplido |
| CA7 Falla | Imagen ilegible: "No disponible"; si no se puede guardar el mapa, el resultado sigue sin él | Cumplido |

**Cifras:**
- Backend: 408 pruebas, más 2 que solo corren con las imágenes del TIF; cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 188 pruebas, ESLint sin errores y compilación correcta.
- Migración `b3e1c0a7d911`: aplicada sobre PostgreSQL, y `flask db check` sin diferencias.

**Recorrido en navegador real** con tres imágenes: la foto sintética original, la misma con un empalme y la de ChatGPT.
- La capa ELA dio 0 %, 45 % y 20 %.
- En el PDF de 11 páginas, el mapa del empalme tiene un único recuadro sobre la zona pegada.
- En celular no hay desborde, y no hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Corrección por textura**: sin ella, los bordes y los detalles quedan marcados como si fueran ediciones.
- **Tope en indicio moderado**: con las imágenes del TIF, ELA también marca zonas débiles en imágenes generadas o reenviadas. Un nivel más alto confundiría.
- **Unión de bloques cercanos**: ELA marca los bordes de una zona pegada por separado; unidos, se informa una sola región, más fácil de leer.
- **El mapa como archivo aparte**, con su enlace firmado, en lugar de guardarlo dentro del resultado: así no pesa en la base de datos y se borra junto con las demás imágenes del caso.
- **PNG con paleta de 64 colores**: el mapa de una foto con mucho detalle pasó de 1 MB a unos 400 KB dentro del PDF.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| El empalme aparecía como tres regiones, una por cada borde | Se unen los bloques marcados a 2 bloques o menos |
| Un mapa pesaba 1 MB dentro del PDF | PNG con paleta de 64 colores |
| Las pruebas del informe usan objetos simples sin `id` | El informe busca la imagen del resultado solo si tiene `id` |

## Pendientes

- **Autora**:
  - Revisar e integrar el Pull Request de la 011. Al integrarlo en `main`, se despliega solo.
  - Revisar con los tutores los umbrales de ELA y su "¿Qué significa?".
- **Siguiente**: 013 (panel y notificaciones).
