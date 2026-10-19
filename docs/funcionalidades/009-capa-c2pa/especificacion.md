# Especificación: 009 — Capa 2 (credenciales de contenido C2PA)

- **Rama**: `funcionalidad/009-capa-c2pa`
- **Estado**: Completada (pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF40; RF43 (CA1 a CA4, para esta capa); RNF23 (CA1)
- **Reglas de negocio aplicadas**: RN26, RN27, RN28, RN29
- **Casos de uso**: la parte de CU28 que ejecuta la capa 2

## Problema

Cada vez más generadores de imágenes, como ChatGPT, Gemini o Adobe Firefly, y algunos teléfonos y cámaras firman lo que producen con **credenciales de contenido**, según el estándar C2PA. Esas credenciales, llamadas manifiesto, declaran:
- quién firmó el archivo;
- con qué herramienta se hizo;
- si lo generó una inteligencia artificial;
- qué ediciones se le hicieron.

Una firma digital las protege: si alguien cambia la imagen o el manifiesto, la firma deja de coincidir.

La capa de metadatos (007) ya lee esos datos, pero no puede comprobar la firma: cualquiera podría copiarlos o inventarlos. Esta capa **verifica la firma** contra la lista de confianza oficial del consorcio C2PA. Una declaración de IA con firma confiable es el indicio más fuerte del sistema (RN28).

El repositorio anterior (`valentinasalmon/TIF`) dejó dos piezas útiles:
- `c2pa_service.py`, que lee el manifiesto con ExifTool sin verificar la firma;
- `probar_c2pa_firma.py`, una sonda que ya usaba c2pa-python.

Sus resultados guardados mostraban la firma de OpenAI como "no confiable". La revisión de esta funcionalidad explica por qué y lo corrige (ver el plan).

## Alcance

### Incluido

**Lectura y verificación (RF40)**
- La capa lee el manifiesto C2PA de la imagen y verifica su firma contra la lista de confianza oficial de C2PA.
- La lista de confianza se guarda en la plataforma, con su versión: la verificación no depende de una descarga en el momento del análisis y se puede reproducir.
- La capa no descarga nada de internet durante el análisis.
- El resultado distingue cuatro estados de la firma:
  - **Confiable**: la firma es válida y el firmante está en la lista de confianza.
  - **Firmante no reconocido**: la firma es válida, pero el firmante no está en la lista.
  - **Archivo modificado después de firmarse**: la imagen o el manifiesto no coinciden con lo que se firmó.
  - **No válidas**: la firma o el manifiesto no superan la validación; por ejemplo, un certificado vencido o revocado, o una acción que no coincide con el resto del manifiesto.

**Hallazgos**
- **Declaración de IA**: el manifiesto declara que el contenido fue generado o compuesto con IA, según el vocabulario IPTC.
- **Ediciones registradas**: el manifiesto registra acciones de edición, como recortes, filtros, ajustes de color o contenido agregado o quitado.
- **Problemas de la firma**: firmante no reconocido, archivo modificado después de firmarse o credenciales no válidas, con el detalle de la validación.
- **Credenciales dañadas**: el archivo tiene un manifiesto que no se puede leer.
- Cada hallazgo pesa según el estado de la firma: un dato con firma confiable pesa más que uno con firma no reconocida o inválida.

**Nivel de indicio**
- Una declaración de IA con firma confiable lleva el nivel al **máximo (100 %)** y se informa como el indicio más fuerte del sistema (RN28).
- En los demás casos, el nivel se calcula como en la capa de metadatos, con 90 % como máximo. El método está en el plan.

**Sin credenciales (RN28)**
- Una imagen sin manifiesto se informa como **"Sin credenciales de contenido"**, con nivel 0.
- La conclusión aclara que la falta de credenciales no indica que la imagen sea original. Es lo habitual en fotos de teléfonos y en imágenes que pasaron por WhatsApp o por una captura de pantalla, porque esos canales las eliminan.

**Datos informados (RF40 CA4)**: estado de la firma, firmante, fecha de la firma, herramienta declarada, origen declarado, acciones registradas y sello de tiempo de la firma.

**En pantalla y en el informe**: la capa aparece como "Credenciales de contenido (C2PA)", con su nivel, sus hallazgos, sus datos y su recuadro "¿Qué significa?".

**Versiones (RN29)**: versión de la capa, de c2pa-python y de la lista de confianza usada.

### Excluido

- **Descargar la lista de confianza en cada análisis.** Se actualiza reemplazando el archivo guardado, como el catálogo de aseguradoras.
- **Credenciales remotas**, que el archivo indica por enlace y no lleva dentro: la capa no las descarga.
- **Firmar con C2PA** las imágenes o el informe.
- **Revisar los ingredientes**, es decir, los manifiestos de las imágenes usadas para componer otra: solo se analiza el manifiesto activo.

## Criterios de aceptación

- [x] **CA1**: Dado un manifiesto con firma confiable que declara generación por IA, entonces el nivel es 100 % y la conclusión lo presenta como el indicio más fuerte del sistema (RF40 CA1, RN28).
- [x] **CA2**: Dado un manifiesto con firmante no reconocido, archivo modificado después de firmarse o credenciales no válidas, entonces se informa como anomalía con el detalle de la validación, y una declaración de IA en ese manifiesto no lleva el nivel al máximo (RF40 CA2).
- [x] **CA3**: Dada una imagen sin manifiesto, entonces se informa "Sin credenciales de contenido" con nivel 0 y la aclaración de que su ausencia no constituye evidencia de autenticidad (RF40 CA3, RN28).
- [x] **CA4**: Dado un manifiesto válido, entonces se informan el firmante, la herramienta declarada y las acciones registradas (RF40 CA4).
- [x] **CA5**: Dado un manifiesto ilegible o una falla de la biblioteca, entonces se informa como anomalía o como "No disponible" con el motivo, y las demás capas siguen (RN26).
- [x] **CA6**: La conclusión es un indicio con la recomendación de consultar a un profesional, sin términos de veredicto (RN27), y el resultado registra las versiones de la capa, de c2pa-python y de la lista de confianza (RN29).
- [x] **CA7**: La capa aparece en la pantalla del análisis y en el informe PDF, con su recuadro "¿Qué significa?" (RNF23 CA1).
- [x] **CA8**: Con las imágenes de prueba de canales del repositorio anterior, la capa reproduce lo esperado:
  - Firma confiable en el original, en el envío como documento de WhatsApp y en el correo electrónico.
  - Sin credenciales en la foto de WhatsApp y en la captura de pantalla.

## Preguntas abiertas

- Ninguna que bloquee.
- Las severidades y los textos de "¿Qué significa?" son una propuesta para revisar con los tutores.
- La licencia de uso de la lista de confianza de C2PA queda por confirmar, igual que la del catálogo de la SSN (CP-18).
