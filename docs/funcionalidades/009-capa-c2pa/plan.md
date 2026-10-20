# Plan técnico: 009 — Capa 2 (credenciales de contenido C2PA)

Referencias: [especificacion.md](especificacion.md) · [ADR-0006](../../arquitectura/decisiones/0006-capas-de-analisis-strategy.md) (capas intercambiables)

## Resumen de la solución

- Nueva capa `CapaC2PA` en `backend/app/analisis/credenciales_c2pa.py`.
  - Hereda de `CapaAnalisis` y se agrega en `registro.py` después de la de metadatos, sin cambiar el motor ni la capa 1 (ADR-0006, RNF18).
  - El módulo no se llama `c2pa.py`, como proponía el documento de reutilización, para no confundirlo con la biblioteca `c2pa`.
- **Lectura y verificación** con c2pa-python 0.38.0:
  - `c2pa.Reader` lee los bytes en memoria, sin copias de la evidencia en disco.
  - El contexto de validación se crea una sola vez por capa, con la lista de confianza y los usos de clave aceptados.
  - Se desactiva toda descarga durante el análisis: revocaciones (`ocsp_fetch`) y credenciales remotas (`remote_manifest_fetch`).
- **Lista de confianza** en `backend/recursos/confianza_c2pa/`, con su README de fuente y actualización:
  - `C2PA-TRUST-LIST.pem`: 32 certificados de firma.
  - `C2PA-TSA-TRUST-LIST.pem`: 23 autoridades de sello de tiempo.
  - La variable `CARPETA_CONFIANZA_C2PA` permite usar otra carpeta.
- **Refactorización**: el cálculo del nivel (`calcular_nivel`), la intensidad de la conclusión y el texto acotado pasan de `metadatos.py` a `base.py`, porque ahora los usan las dos capas.
- **Informe y pantalla**:
  - Título "Capa 2 · Credenciales de contenido (C2PA)" y recuadro "¿Qué significa?" en `informe_analisis.py`.
  - En `SeccionAnalisis.jsx`: el título, una etiqueta con el estado de la firma y la tabla "Datos de las credenciales".

## Revisión del código C2PA del TIF

### Qué funciona y se conserva

| Pieza del TIF | Qué se conserva |
|---|---|
| `c2pa_service.py` | La interpretación del origen digital con el vocabulario IPTC (`trainedAlgorithmicMedia`, `compositeWithTrainedAlgorithmicMedia`). La idea de que la falta de manifiesto "no aporta ni resta". La lectura de `softwareAgent` y `claim_generator_info`. |
| `probar_c2pa_firma.py` | El uso de `c2pa.Reader` con un contexto de confianza. La separación entre fallas que muestran un **contenido modificado** (`mismatch`, `hashedURI`) y fallas del **certificado**. Los datos de `signature_info` (emisor, nombre común). |
| `tests/test_c2pa_service.py` | Los casos de ChatGPT y Gemini con declaración de IA, sin manifiesto, y con manifiesto que no declara IA. Se reescriben con imágenes firmadas en la prueba. |
| Prueba de canales | Las 10 imágenes y lo esperado por canal pasan a ser el criterio CA8. |

### Qué se corrige o mejora

| Problema del TIF | Corrección |
|---|---|
| `c2pa_service.py` leía el manifiesto con ExifTool y no verificaba la firma (`firma_verificada: None`), así que la declaración de IA quedaba como indicio "fuerte" sin confirmar. | La lectura y la verificación las hace c2pa-python. ExifTool sigue leyendo esos datos en la capa 1, aclarando que no verifica la firma. |
| **La firma de OpenAI aparecía como no confiable** (`signingCredential.untrusted` y `signingCredential.invalid: certificate missing required EKU`). | Ver el hallazgo siguiente. |
| La lista de confianza se descargaba en cada ejecución de la sonda. | Se guarda en el repositorio con su huella, y la versión se registra en cada resultado (RN29). |
| `analizar_c2pa` escribía en la base de datos. | La capa es una función pura que devuelve un `ResultadoCapa`; el servicio de análisis es quien guarda (hallazgo 4 del documento de reutilización). |
| Clasificación binaria: "fuerte" o "sin indicios". | Cuatro estados de la firma, y la severidad de cada hallazgo depende del estado (ver la tabla de abajo). |
| No miraba las ediciones registradas en el manifiesto. | Las acciones de edición (recorte, filtro, ajuste de color, dibujo, contenido agregado o quitado) son un hallazgo. |

### Hallazgo: por qué la firma de OpenAI "no era confiable"

Al extraer los certificados del manifiesto de la imagen de ChatGPT se vio lo siguiente:
- El certificado de OpenAI lo emite **Trufo C2PA Claim Signing CA (2025)**.
- La raíz de esa autoridad, **Trufo C2PA Root CA**, **sí está en la lista oficial**.

El rechazo venía de dos causas:
1. **La sonda se ejecutó sin `--confianza`**, como ya registraba el documento de reutilización.
2. **c2pa-python no trae una configuración de usos de clave (EKU)**: sin ella rechaza todo certificado, aun uno con el uso `c2pa-kp-claimSigning`, con "certificate missing required EKU". Lo comprobé firmando una imagen de prueba con ese uso.

La corrección es configurar `trust_config` con los mismos usos que acepta el validador de referencia de C2PA:
- `c2pa-kp-claimSigning`;
- `documentSigning`;
- `emailProtection`;
- `timeStamping`;
- `OCSPSigning`;
- el de firma C2PA de Microsoft.

Con esa configuración, ChatGPT y Gemini quedan **confiables**.

El sello de tiempo de OpenAI lo emite su propia autoridad, que no está en la lista de sellos. Por eso se informa como "válido, emitido por una autoridad fuera de la lista de confianza". Es un dato informativo y no un hallazgo, porque la firma principal sí es confiable.

### Resultado con las imágenes de prueba de canales del TIF

`IMAGENES_CANALES_TIF=… pytest pruebas/unitarias/test_capa_c2pa.py`:

| Canal | ChatGPT | Gemini |
|---|---|---|
| Archivo original | 100 %, firma confiable | 100 %, firma confiable |
| WhatsApp como documento | 100 %, firma confiable | 100 %, firma confiable |
| Correo electrónico | 100 %, firma confiable | 100 %, firma confiable |
| WhatsApp como foto | 0 %, sin credenciales | 0 %, sin credenciales |
| Captura de pantalla | 0 %, sin credenciales | 0 %, sin credenciales |

Coincide con la prueba de canales del TIF. Las imágenes no se suben al repositorio.

## Cálculo del nivel de indicio de la capa 2

Severidad de cada hallazgo según el estado de la firma:

| Hallazgo | Confiable | Firmante no reconocido | Modificada después de firmarse | No válidas |
|---|---|---|---|---|
| Declaración de IA u origen sintético | Directo | Fuerte | Moderado | Moderado |
| Ediciones registradas | Fuerte | Moderado | Débil | Débil |
| Problema de la firma | — | Débil | Moderado | Moderado |

Hay además dos casos que no dependen de la firma:
- **Manifiesto ilegible**: moderado.
- **Sin manifiesto**: neutro, con nivel 0.

**Nivel**:
- Una firma confiable que declara IA (`trainedAlgorithmicMedia` o `compositeWithTrainedAlgorithmicMedia`) vale **100 %** (RN28, RF40 CA1).
- En los demás casos se usa el método común de la 007: la base de la anomalía más grave (directo 90, fuerte 70, moderado 45, débil 20) más 10 por cada otra moderada o más grave, con un máximo de 90.

**Por qué una declaración con firma modificada o no válida pesa poco.** Un manifiesto copiado de una imagen generada a una foto real deja exactamente ese rastro: la firma ya no coincide con el contenido. Si pesara mucho, se podría hacer pasar una foto real por una imagen de IA.

| Ejemplo | Nivel |
|---|---|
| ChatGPT o Gemini, firma confiable | 100 |
| Foto editada con firma confiable (recorte y ajuste de color) | 70 |
| Declaración de IA con firmante fuera de la lista | 70 (fuerte; el débil de la firma no suma) |
| Declaración de IA en una imagen modificada después de firmarse | 55 |
| Firmante fuera de la lista, sin otros hallazgos | 20 |
| Cámara con firma confiable y sin ediciones; o sin credenciales | 0 |

## Capas afectadas

| Capa | Cambio |
|---|---|
| `analisis` | `credenciales_c2pa.py` (nuevo); `base.py` (cálculo de nivel y textos comunes); `metadatos.py` (usa lo común); `registro.py`. |
| `configuracion` | `CARPETA_CONFIANZA_C2PA`. |
| `informes` | Título y "¿Qué significa?" de la capa 2. En la plantilla, el título de cada capa ya no queda separado de su contenido por un salto de página. |
| `recursos` | Lista de confianza y su README. |
| Frontend | `SeccionAnalisis.jsx`: título, estado de la firma y tabla de la capa 2. |

Las rutas, los servicios, los repositorios y los modelos no cambian: el resultado entra en las tablas de la 007 (`resultados_capa`, `anomalias`, `detalle` en JSON).

## Cambios en datos

Ninguno; no hay migración. El `detalle` de la capa 2 guarda:
- `tabla`: los datos informados;
- `sin_credenciales`;
- `estado_firma`.

## Bibliotecas nuevas

- `c2pa-python==0.38.0` (SDK c2pa-rs 0.91.0), en producción. Trae su biblioteca nativa en el paquete; no necesita nada del sistema.
- `cryptography==50.0.2`, en desarrollo: crea la autoridad certificante de las pruebas. Ya era una dependencia de c2pa-python; se fija para las pruebas.

## Estrategia de pruebas

- **Unitarias** (`test_capa_c2pa.py`, 31 casos con los parametrizados). Una autoridad certificante creada en cada ejecución firma imágenes JPEG y PNG con c2pa-python. Con ellas se prueban los cuatro estados reales:
  - **confiable**: la raíz de prueba está en la lista;
  - **firmante no reconocido**: se usa la lista oficial;
  - **modificada**: se cambia un byte después de firmar;
  - **sin credenciales**.

  También se prueban las ediciones, el contenido sintético sin IA, la clasificación de las fallas, el manifiesto ilegible, la falta de biblioteca y de lista, la versión, la ausencia de veredictos y el registro.
- **Prueba de canales del TIF**: corre solo si se define `IMAGENES_CANALES_TIF`.
- **Integración**: un análisis por la API devuelve las dos capas, y la capa 2 informa "sin credenciales".
- **Informe**: título, tabla y recuadro de la capa 2; ningún "¿Qué significa?" usa términos de veredicto.
- **Frontend**: estado de la firma, tabla "Datos de las credenciales" y "Sin credenciales".
- **Navegador real**: cuatro imágenes (ChatGPT, Gemini, ChatGPT reenviada por WhatsApp y una editada con Photoshop), resultados en computadora y celular, y PDF descargado.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La lista oficial cambia (altas y bajas de emisores). | Se actualiza reemplazando el archivo; cada resultado registra la huella de la lista que usó. |
| Un emisor conocido no está en la lista oficial. | Se informa como "firmante no reconocido" (indicio fuerte, no máximo), sin ocultar la declaración. |
| c2pa-python cambia su API o sus códigos de validación. | Versión fijada; las pruebas firman y validan imágenes reales con la biblioteca. |
| Sin consultar revocaciones, no se detecta un certificado revocado después de firmar. | Se aceptó para no depender de la red durante el análisis. La información de revocación incluida en el manifiesto sí se valida. |
