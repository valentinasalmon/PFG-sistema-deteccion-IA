# 2026-10-26 — Funcionalidades 025 y 026: informe breve por rubro y verificable

## Qué se hizo

- **025:**
  - se propusieron PDF de ejemplo para los dos rubros, generados con las capas reales sobre imágenes sintéticas, y la autora los aprobó;
  - informe reordenado y reducido de 8–9 páginas a unas 4, sin números de sección ni saltos de página, con más espacio;
  - lenguaje por rubro;
  - sección y etiquetas de resultados deterministas y probabilísticos;
  - resultados por imagen en una oración más hasta dos hallazgos.
- **026:**
  - código de verificación y QR en el PDF;
  - huella del PDF sellada en Hedera (inmediato y por la tarea programada);
  - API y página pública "Verificar un informe", que calcula la huella en el navegador;
  - código y sello en el historial de informes;
  - enlace "Verificar un informe" en el pie.
- **Calidad:**
  - backend: 480 pruebas y cobertura del 97,7 %;
  - frontend: 202 pruebas.

## Decisiones

- **Las versiones de los componentes (RN29)** quedan como una línea en el recuadro final, en lugar de una sección: la autora pidió quitarla y el requisito exige registrarlas.
- **La sección de deterministas y probabilísticos va antes de los resultados**, para que se entiendan las etiquetas.
- **Se reemplazaron palabras de la lista de veredictos** ("falsa alarma", "auténtica", "fraudulenta") por formulaciones neutras (RN27).
- **La verificación pública nunca devuelve datos del caso**, y el PDF no se sube: la huella se calcula con Web Crypto.
- **La huella registrada es la del PDF final**, que ya incluye el QR con su código.

## Pendiente

- Firma digital del PDF (opcional, CP-27).
- 029: huella de cada versión desplegada.
- 027: inicio con Google.
- 028: ajustes de interfaz, incluida la página de carga desde el celular.
