# Investigación: carga de imágenes desde el celular (2026-10-25)

La autora marcó como prioritario poder subir las fotos desde el celular, en Android y en iOS. Las fotos de un siniestro o de una prueba se sacan casi siempre con el celular, y hoy la plataforma está pensada para la computadora. Este documento junta las opciones para revisarlas con la autora (pros y contras) y es insumo del informe final.

## 1. Hallazgos técnicos

- **La web ya puede usar la cámara y la galería**: `<input type="file" accept="image/*">` abre en Android y en iOS un menú para sacar la foto o elegirla de la galería. Con `capture="environment"` se abre directamente la cámara trasera. No hace falta una aplicación.
- **HEIC/HEIF**: es el formato por defecto del iPhone. Hoy la plataforma solo acepta JPEG y PNG, así que hay que aceptarlo. Algunos selectores entregan el archivo con extensión `.jpg` aunque por dentro sea HEIC: se valida por la firma binaria, como ya hace la plataforma. Chrome, Firefox y Edge no muestran HEIC, así que hace falta generar la vista previa en el servidor (Pillow con `pillow-heif`).
- **Metadatos**: hay reportes de que iOS quita la ubicación GPS cuando la foto se elige de la galería desde el navegador, mientras conserva el resto de los datos EXIF. Además, convertir de HEIC a JPEG puede perder metadatos. **Consecuencia:** el original nunca se convierte (RN23); la conversión es solo para la vista previa. Hay que avisar a la persona que sacar la foto en el momento conserva más datos.
- **Fecha del archivo**: en iOS, la fecha de modificación del archivo puede ser la de la carga y no la de la captura. Por eso la fecha real se toma del EXIF.
- **Fotos tomadas desde la propia página (`getUserMedia`)**: no tienen EXIF. Sirven para un "modo evidencia" con datos de captura propios (ver la idea 4), pero la capa de metadatos va a informar que faltan datos.
- **WhatsApp y otras mensajerías comprimen las fotos y les borran los metadatos**: no son un canal apto para evidencia.

## 2. Ideas y alternativas (para revisar pros y contras)

| # | Idea | Pros | Contras |
|---|---|---|---|
| 1 | **Web móvil adaptada** (base): botones "Sacar foto" y "Elegir de la galería" en la pantalla del caso | Funciona en Android e iOS sin instalar nada; se reutiliza toda la carga actual | Hay que adaptar la pantalla del caso al celular; depende de iniciar sesión en el celular |
| 2 | **QR de un solo uso desde la computadora** (base): "Cargar desde el celular" muestra un QR que vence a los 15 min y abre una página de carga para ese caso | No hay que iniciar sesión en el celular; es muy cómodo cuando se trabaja en la compu | Es un enlace con permiso de carga: hay que limitarlo en tiempo, cantidad y caso, y auditarlo |
| 3 | **Enlace de carga para terceros**: la aseguradora o el abogado le manda al asegurado o al cliente un enlace (por correo o WhatsApp) para que suba sus propias fotos, sin cuenta | Refleja el flujo real de un siniestro; ahorra el reenvío de fotos por WhatsApp, que las comprime | Lo usan personas externas: requiere consentimiento y privacidad, límites contra abuso y aclarar quién responde por las fotos |
| 4 | **"Modo evidencia" con captura guiada**: la página abre la cámara con pautas (encuadre, distancia, varias tomas) y registra hora, ubicación del navegador (con permiso) y dispositivo | Cadena de custodia desde el origen; buena demostración en la defensa | Las fotos no tienen EXIF; la ubicación depende del permiso; más desarrollo |
| 5 | **Huella calculada en el celular antes de enviar** (Web Crypto API) y comparada con la del servidor | Prueba que el archivo no cambió en el camino; es barato de hacer | Agrega poco si ya hay HTTPS; hay que explicarlo bien en el informe |
| 6 | **Aplicación instalable (PWA)** con ícono en la pantalla de inicio y "Compartir con evidentIA" desde la galería (Web Share Target) | Sensación de aplicación sin tiendas; compartir desde la galería es muy natural | "Compartir con" funciona en Android con Chrome, **no en iOS**; requiere *service worker* |
| 7 | **Carga reanudable** (por partes) para conexiones móviles débiles | Las fotos grandes no se pierden si se corta la señal | Más complejidad en el backend; con 20 MB por foto quizás no haga falta |
| 8 | **Correo por caso**: cada caso tiene una dirección a la que se reenvían las fotos | Conocido por todos | Hay que recibir correos con SES; riesgo de suplantación; algunos clientes de correo comprimen las fotos |
| 9 | **Aplicación nativa** (React Native / Expo) | Control total de la cámara y de los metadatos; atestación del dispositivo (App Attest, Play Integrity) | No llega a la entrega: tiempos de las tiendas y de desarrollo. **Trabajo futuro** |
| 10 | **Fomentar celulares con credenciales de contenido (C2PA)**: algunos modelos recientes firman las fotos al sacarlas; la capa 2 ya las lee | Es la prueba de origen más fuerte; no cuesta desarrollo | Depende del modelo de celular; hay que confirmar qué equipos lo hacen |

**Propuesta provisoria** (a confirmar con la autora): para la entrega, ideas **1, 2 y 5**, más soporte de HEIC. Si sobra tiempo, la **3** porque aporta mucho a aseguradoras. La **9** va como trabajo futuro y la **8** se descarta.

## 3. Decisión de la autora y propuesta final al tutor (2026-10-26)

- **La plataforma no se adapta para usarse en el celular**: la persona trabaja en la computadora y las fotos se suben desde el celular a ese caso.
- **Sin instalar apps de las tiendas y en pocos pasos.** Se descartaron las opciones con cable. Las inalámbricas que pasan por la computadora (AirDrop, Quick Share, iCloud, LocalSend) se descartaron porque agregan pasos y dependen de la configuración del celular.
- **Propuesta enviada al tutor:**
  - *código de carga* de un solo uso (QR y 6 dígitos, 15 minutos, solo carga en ese caso, auditado);
  - **compartir desde la galería**: en Android con **Web Share Target API** (la plataforma instalada como PWA desde Chrome, una sola vez); en iPhone con un **Atajo de Apple (Shortcuts)** en la hoja para compartir (agregado una sola vez desde un enlace de iCloud), porque Safari no implementa Web Share Target ([WebKit #194593](https://bugs.webkit.org/show_bug.cgi?id=194593));
  - el QR queda como alternativa sin preparación.
- **A verificar:** si el Atajo envía el original (HEIC con metadatos) y no una copia convertida. Web Share Target funciona en Chrome y Samsung Internet, no en Firefox.

## 4. Decisión del tutor (2026-10-26)

El tutor indicó probar el **QR desde la computadora hacia la galería del celular**, y se implementó (funcionalidad 024, etapa 2). El código de 6 dígitos y el "compartir desde la galería" quedan como mejora futura.

**Drive y Dropbox se descartaron:**
- duplican los pasos;
- agregan un custodio intermedio sin trazabilidad, que puede comprimir o convertir la foto;
- sacan la evidencia del control de la plataforma.

Como ampliación futura, importar desde un enlace enviado por un tercero requeriría:
- descargar solo ese archivo, sin acceder a cuentas;
- no guardar el enlace;
- aceptar solo dominios de Drive y Dropbox;
- marcar el origen como "enviado por un tercero, sin garantía de origen";
- una declaración del usuario de que tiene autorización (Ley 25.326 de Protección de Datos Personales).

## Fuentes

- Conversión a HEIC en Safari 17 o posterior: https://bugs.webkit.org/show_bug.cgi?id=303803
- Pérdida de ubicación al elegir fotos desde el navegador en iOS 16.4: https://developer.apple.com/forums/thread/727451
- Pérdida de metadatos al convertir HEIC: https://phabricator.wikimedia.org/T211745
- Trampas de formato y orientación al subir desde el celular: https://hackernoon.com/uploading-jpg-files-on-mobile-with-orientation-size-and-format-traps-a-quick-guide
- Fecha de modificación incorrecta en iOS 16.6: https://bugs.webkit.org/show_bug.cgi?id=232561
- Web Share Target en Chrome: https://developer.chrome.com/docs/android/trusted-web-activity/web-share-target
- Subir fotos con Atajos ("Obtener contenido de URL"): https://dev.to/chatgptnexus/2025011522-22-09-article-2eia y https://community.zapier.com/featured-articles-65/how-to-send-photos-from-ios-to-zap-workflows-using-shortcuts-webhooks-by-zapier-12951
