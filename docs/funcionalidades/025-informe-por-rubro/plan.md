# 025 · Plan técnico

- **`app/informes/informe_analisis.py`**:
  - `TEXTOS_RUBRO` (abogado y aseguradora) y `TIPO_DE_RESULTADO` por capa (integridad, metadatos y C2PA son deterministas; ELA y la red neuronal, probabilísticas);
  - `QUE_MIRA` (una línea por técnica) y `EXPLICACION_TIPOS`;
  - `_primera_oracion` y `_hallazgos_principales` arman la versión breve;
  - `_tipos()` agrupa las técnicas del informe por tipo;
  - se quitaron los textos y los datos que ya no se usan (criterios, tablas técnicas, metodología, glosario, limitaciones y uso previsto);
  - versión de la plantilla: 2.0.
- **`plantillas/informes/informe_analisis.html`**: reescrita con el orden aprobado, sin numeración ni reglas de salto de página, y con interlineado de 1,6 y celdas de 6 pt.
- **Vista previa**: se generaron PDF de ejemplo para los dos rubros con las capas reales sobre imágenes sintéticas.
- **Pruebas**: orden de las secciones, ausencia de las secciones quitadas, resultado breve, etiquetas de tipo, lenguaje por rubro, mapa ELA condicional y textos sin veredictos.
