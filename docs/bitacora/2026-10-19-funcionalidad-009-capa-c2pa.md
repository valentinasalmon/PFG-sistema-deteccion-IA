# 2026-10-19 — Funcionalidad 009: capa de credenciales de contenido (C2PA)

## Qué se hizo

Se agregó la **capa 2** del análisis. Lee las credenciales de contenido C2PA de cada imagen y **verifica su firma** contra la lista de confianza oficial del consorcio C2PA. Las firman, por ejemplo, ChatGPT, Gemini, Adobe Firefly y algunos teléfonos.

Una declaración de IA con firma confiable es el indicio más fuerte del sistema y lleva el nivel al 100 % (RN28).

Documentos: [especificación](../funcionalidades/009-capa-c2pa/especificacion.md), [plan](../funcionalidades/009-capa-c2pa/plan.md) y [tareas](../funcionalidades/009-capa-c2pa/tareas.md). La rama `funcionalidad/009-capa-c2pa` parte de `desarrollo` con la 008 integrada.

- **Se partió de lo hecho en el TIF**: `c2pa_service.py`, `probar_c2pa_firma.py`, sus pruebas y la prueba de canales. El plan detalla qué se conservó, qué se corrigió y por qué.
- **Verificación**:
  - Usa c2pa-python 0.38.0 con la lista de confianza guardada en `backend/recursos/confianza_c2pa/`.
  - La lista tiene 32 emisores de firmas y 23 autoridades de sello de tiempo. Su README indica la fuente y cómo actualizarla.
  - Durante el análisis no se descarga nada.
- **Cuatro estados de la firma**:
  - confiable;
  - firmante no reconocido;
  - modificada después de firmarse;
  - no válidas.
- **Hallazgos**:
  - Declaración de IA o de origen sintético.
  - Ediciones registradas.
  - Problemas de la firma, con el detalle de la validación traducido.
  - Credenciales ilegibles.

  El peso de cada hallazgo depende del estado de la firma.
- **Sin credenciales**: se informa "Sin credenciales de contenido" con nivel 0, aclarando que su ausencia no constituye evidencia de autenticidad (RN28).
- **Datos informados**: firmante, fecha de la firma, herramienta, agente de software, origen declarado, acciones registradas y sello de tiempo (RF40 CA4).
- **Pantalla e informe PDF**:
  - Título "Credenciales de contenido (C2PA)".
  - Una etiqueta con el estado de la firma.
  - La tabla "Datos de las credenciales".
  - El recuadro "¿Qué significa?".
- **Refactorización**: el cálculo del nivel y los textos de intensidad pasaron a `app/analisis/base.py`, compartidos con la capa de metadatos.
- **Mejoras del PDF**:
  - El título de cada capa ya no queda solo al pie de una página, separado de su contenido.
  - Se agregó la leyenda "Este informe no constituye un dictamen pericial. Consulte a un profesional especializado." en todas las páginas. La exige RNF23 CA2 y faltaba desde la 008.

## Hallazgo principal: la firma de OpenAI sí es confiable

En el TIF, la imagen de ChatGPT figuraba con `signingCredential.untrusted` y "certificate missing required EKU". Al extraer los certificados del manifiesto se encontraron dos cosas:
- El certificado de OpenAI lo emite **Trufo**, una autoridad que sí está en la lista oficial.
- c2pa-python rechaza todo certificado si no se le configuran los usos de clave aceptados (EKU). Lo comprobé firmando una imagen de prueba.

Con la lista oficial y la misma configuración de usos que el validador de referencia de C2PA, ChatGPT y Gemini quedan **confiables**.

Resultado con las 10 imágenes de la prueba de canales del TIF (sin subirlas al repositorio):

| Canal | ChatGPT | Gemini |
|---|---|---|
| Original, WhatsApp como documento y correo | 100 %, firma confiable | 100 %, firma confiable |
| WhatsApp como foto y captura de pantalla | 0 %, sin credenciales | 0 %, sin credenciales |

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 Firma confiable con IA | Imagen firmada por una autoridad de prueba incluida en la lista: 100 % y "el indicio más fuerte"; ChatGPT y Gemini reales | Cumplido |
| CA2 Firma no confiable o no válida | Firmante fuera de la lista oficial (70 %); un byte cambiado después de firmar (55 %, `assertion.dataHash.mismatch`); clasificación de fallas | Cumplido |
| CA3 Sin credenciales | JPEG y PNG sin manifiesto; foto de WhatsApp y captura reales | Cumplido |
| CA4 Datos | Firmante, herramienta, agente, origen y acciones en la tabla | Cumplido |
| CA5 Fallas | Manifiesto ilegible (anomalía moderada); sin biblioteca o sin lista: "No disponible" | Cumplido |
| CA6 Textos y versiones | Búsqueda de términos de veredicto; versión con c2pa-python y huella de la lista | Cumplido |
| CA7 Pantalla e informe | Pruebas del frontend y del HTML del informe; recorrido en navegador y PDF | Cumplido |
| CA8 Canales del TIF | `IMAGENES_CANALES_TIF=… pytest pruebas/unitarias/test_capa_c2pa.py` | Cumplido |

**Cifras:**
- Backend: 388 pruebas más 2 que solo corren con las imágenes del TIF (las 2 pasan con ellas), cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 187 pruebas, cobertura del 98 %, ESLint sin errores y compilación correcta.
- No hay migración: el resultado entra en las tablas de la 007.

**Recorrido en navegador real** con cuatro imágenes: ChatGPT, Gemini, la de ChatGPT reenviada como foto por WhatsApp y una editada con Photoshop.
- ChatGPT y Gemini: 100 % con "Firma confiable" y la tabla con OpenAI y Google como firmantes.
- La reenviada por WhatsApp: "Sin credenciales", 0 %. La capa de metadatos le da 20 % solo por sus dimensiones.
- La editada: 0 % en la capa 2 y 90 % en la de metadatos.
- El PDF descargado tiene 10 páginas, con la capa 2 en cada imagen.
- En celular no hay desborde, y no hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Lista de confianza guardada en el repositorio**, no descargada en cada análisis: el resultado no depende de la red y se puede reproducir. Cada resultado registra la huella abreviada de la lista (RN29). Son certificados públicos, no secretos.
- **Sin consultas en línea durante el análisis** (revocaciones ni credenciales remotas). Así el análisis no depende de servicios externos ni hace pedidos a direcciones que trae un archivo no confiable. Se pierde la detección de una revocación posterior a la firma, y queda anotado en los riesgos del plan.
- **Usos de clave aceptados iguales a los del validador de referencia de C2PA.** Sin ellos, c2pa-python rechaza todos los certificados reales.
- **Una declaración de IA pesa según la firma**: directo si es confiable, fuerte si el firmante no es reconocido, moderado si el archivo cambió o la firma no es válida. Si una declaración copiada a una foto real pesara mucho, una foto real podría pasar por una imagen generada.
- **El 100 % se reserva para la IA declarada** (`trainedAlgorithmicMedia` y `compositeWithTrainedAlgorithmicMedia`). Otros orígenes sintéticos llegan a 90 %.
- **Solo se analiza el manifiesto activo**, no los ingredientes: es lo que describe la imagen tal como llegó.
- **Módulo `credenciales_c2pa.py`** y no `c2pa.py`, para no confundirlo con la biblioteca.
- **Pruebas sin imágenes externas**: una autoridad certificante creada en cada ejecución firma las imágenes con c2pa-python, y así se reproducen los cuatro estados reales de la firma.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| "certificate missing required EKU" aun con certificados correctos | Configuración `trust_config` con los usos de clave del validador de referencia |
| Una acción `c2pa.opened` sin ingrediente da `assertion.action.ingredientMismatch`, que no es un problema de firma | El estado se llama "No válidas: la firma o el manifiesto no superan la validación", y el código tiene su explicación en español |
| pylint marcó código repetido entre las dos capas | El cálculo de la intensidad y de las anomalías principales pasó a `base.py` |
| En el PDF, el título de la capa 2 quedaba al pie de una página y su contenido en la siguiente | El título y el nivel no se separan de lo que sigue |
| El entorno virtual de pruebas de la sesión estaba desactualizado | Se recreó desde `requirements-dev.txt` |

## Pendientes

- **Autora**:
  - Revisar e integrar el Pull Request de la 009.
  - Revisar con los tutores las severidades de la capa 2 y su texto de "¿Qué significa?".
  - Confirmar la licencia de uso de la lista de confianza de C2PA, igual que la del catálogo de la SSN.
  - Sigue pendiente lo de la 008: el hito v0.1 (Pull Request de `desarrollo` hacia `main` y etiqueta) y el valor de `VERSION_APLICACION`.
- **Revisión periódica**: actualizar la lista de confianza; el README de la carpeta explica cómo.
- **Para avanzar con la red neuronal (010 y 012)** hacen falta CP-07 (conjunto de datos y umbral) y CP-21 (quién entrena y dónde).
- **Siguiente**: 011 (capa 3, ELA).
