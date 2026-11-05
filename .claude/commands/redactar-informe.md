---
description: Redacta o actualiza una sección del informe final con la voz, la estructura y la evidencia que exige la guía.
---

Redactá la sección del informe que indica `$ARGUMENTS` (por ejemplo, «Capítulo XII» o «Recursos financieros»).

1. Leé `docs/informe-final/guia-de-redaccion.md`, `hechos-del-sistema.md`, `trabajo-con-ia.md`, `plan-de-negocios.md` (si la sección es de negocios o de recursos) y el estado del informe. Recalculá las cifras con `python backend/herramientas/cifras_del_proyecto.py`.
2. Si la sección ya existe en el documento de la autora, leela primero e **integrá**: conservá lo que está bien y reemplazá solo lo que falta o está desactualizado.
3. Escribí como un especialista en el tema de la sección (requisitos, arquitectura, gestión, marketing B2B, propiedad intelectual, finanzas de emprendimientos en Argentina, protección de datos), con el criterio del capítulo en la sección 6 de la guía.
4. Reglas de forma: presente impersonal, prosa sin viñetas, terminología única, números a la española, APA 7. Toda tabla y figura con número, título y nota. Todo dato con su fuente. Lo que no existe va como previsto. Nunca inventes un dato: si falta, marcá **[completar: qué y de dónde sale]** y avisalo.
5. Entregá en el chat el texto listo para pegar, indicando dónde va y qué reemplaza, y agregá a la bibliografía lo que cites.
6. Antes de entregar, pasá tu propio texto por `python backend/herramientas/revisar_informe.py` (guardalo en el *scratchpad*) y corregí lo que marque.
