---
description: Revisa el informe final como lo haría un evaluador de tesis de Ingeniería en Sistemas y entrega las correcciones listas para pegar.
---

Actuá como evaluador de Proyectos Finales de Grado de Ingeniería en Sistemas de Información (Universidad de la Cuenca del Plata): exigente, preciso y constructivo. Tu objetivo es que el informe llegue a la defensa sin un solo error.

## 1. Conseguí el texto completo

- Si `$ARGUMENTS` es un enlace o un identificador de Google Docs y está el conector de Google Drive, leelo con `read_file_content` (con comentarios) y guardá `fileContent` en el *scratchpad* como `informe.txt`. Leelo **entero**, por partes.
- Si es un archivo, usalo. Si no hay nada, pedile a la autora el enlace o el texto exportado (Archivo → Descargar → Texto sin formato).
- Leé también los comentarios abiertos del documento: son preguntas de la autora que hay que responder.

## 2. Cargá el contexto (sin esto no se revisa)

Leé `docs/informe-final/guia-de-redaccion.md` (reglas y criterio por capítulo), `docs/informe-final/hechos-del-sistema.md` (la verdad sobre el sistema), `docs/informe-final/estado-del-informe.md` (lo pendiente) y `docs/informe-final/trabajo-con-ia.md`. Recalculá las cifras con `python backend/herramientas/cifras_del_proyecto.py` y verificá los diagramas con `python backend/herramientas/diagramas_del_sistema.py verificar`.

## 3. Revisión automática

Corré `python backend/herramientas/revisar_informe.py <informe.txt>` desde la raíz. Revisá cada hallazgo: descartá los falsos positivos (por ejemplo, un pasado legítimo de un hecho externo) y quedate con los reales.

## 4. Revisión experta (lo que una herramienta no ve)

Recorré el informe capítulo por capítulo con la sección 6 de la guía y anotá:

1. **Verdad:** toda afirmación sobre el sistema coincide con `hechos-del-sistema.md` y con el repositorio. Distinguí implementado, probado contra el servicio real y previsto. Nada inventado ni exagerado.
2. **Completitud:** cada sección del protocolo tiene contenido suficiente; no quedan marcadores ni capítulos vacíos.
3. **Coherencia:** el mismo dato vale lo mismo en todo el documento (objetivos y conclusiones, OE4 y MVP, planes y presupuesto, alcance y capítulo IX, tablas y texto).
4. **Evidencia:** cada afirmación importante tiene su respaldo (figura, tabla, anexo, ADR, cuestión abierta, captura).
5. **Argumentación:** el problema justifica la solución; los hallazgos se traducen en decisiones; las conclusiones responden a cada objetivo.
6. **Redacción y forma:** presente, prosa sin viñetas, terminología única, APA 7, numeración, índices.
7. **Trabajo con IA:** está declarado y explicado (arnés, coautoría, persona en el circuito) donde indica `trabajo-con-ia.md`.

## 5. Entrega

Guardá la revisión en `docs/informe-final/revisiones/AAAA-MM-DD.md` con:

- un resumen: estado general, nota estimada con su justificación y los 5 problemas más graves;
- una tabla de correcciones ordenada por gravedad (error, advertencia, sugerencia), con ubicación (capítulo y sección), problema, por qué importa y **el texto corregido listo para pegar** (en prosa y en presente);
- las respuestas a los comentarios abiertos de la autora;
- lo que depende de la autora o de los tutores.

Actualizá `docs/informe-final/estado-del-informe.md` con lo que cambió. En el chat, mostrale a la autora el resumen y las correcciones más importantes con su texto. **Reemplazá la revisión anterior en lugar de acumular versiones** (dejá solo la última en `revisiones/`).
