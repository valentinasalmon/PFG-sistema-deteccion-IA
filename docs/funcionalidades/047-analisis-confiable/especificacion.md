# 047 · Análisis confiable para fotos de celular

**Estado**: especificada (2026-11-18). **Rama**: `plataforma/analisis-confiable`. **Pedido**: la autora, al probar la plataforma con fotos de celular («la mayoría usa iPhone; quiero que todo funcione bien para todo»).

## Problema

1. **Metadatos que «no se toman» en fotos subidas desde el celular.** La extracción funciona (ExifTool lee JPEG y HEIC), pero según el camino que use la persona, el celular puede entregar la foto **ya sin metadatos**: el selector de fotos de iOS convierte a JPEG y, según la versión, quita la ubicación o todo el EXIF; WhatsApp borra casi todo. No hay información confiable de qué hace cada versión de iOS: hay que medirlo.
2. **El mapa ELA «transforma todo».** El mapa se estira para que el punto más brillante quede blanco; en una foto sin cambios, con error mínimo y parejo, el ruido se amplifica unas 40 veces y la foto entera se ve encendida (medido el 2026-11-18 con fotos de prueba guardadas al 97 %, como las de un celular).
3. **Fotos que no son de un siniestro.** Nada avisa si se sube una foto que no tiene que ver con un siniestro vial o laboral (una selfie, un documento, una captura de pantalla).

## Alcance

- **Medir antes de decidir**: una página de prueba, sin cuenta, donde la autora sube una foto desde el celular y ve qué llegó al servidor (formato recibido, si llegó convertida, cantidad de metadatos, cámara, fecha y si trae ubicación). La foto no se guarda. Con esa página se prueba cada camino del iPhone (galería, cámara, Archivos) y de Android.
- **Procedencia de cada imagen**: al subirla se registra qué llegó (formato, si trae EXIF y ubicación) y desde qué navegador, para conocer en producción cuántas fotos llegan sin datos y por qué camino.
- **Mejor camino para el iPhone**, según lo que muestre la medición: el que conserve más datos se ofrece primero en la carga desde el celular, con instrucciones cortas.
- **Aviso claro** cuando una foto llega sin metadatos: la causa probable (galería del iPhone, WhatsApp, captura de pantalla) y cómo subir el original, en lugar de una tabla vacía. Es un indicio, no un veredicto (RN27).
- **Mapa ELA con escala absoluta**: una foto sin cambios se ve oscura y una zona con error distinto se sigue destacando. Sin cambiar los umbrales de detección.
- **Filtro de contenido que avisa, no bloquea**: si una foto no parece de un siniestro vial o laboral, la plataforma lo dice al subirla y la persona decide si la incluye en el análisis (ADR-0017: la decisión es de una persona). El modelo corre en el servidor; antes de elegirlo se mide su peso y su tiempo en la máquina de producción.

## Criterios de aceptación

- [ ] **CA1**: La página de prueba informa, para una foto subida, el formato recibido, si trae EXIF, la cámara, la fecha y si trae ubicación, sin guardar la foto.
- [ ] **CA2**: Probado con un iPhone real (autora) por galería, cámara y Archivos; el resultado queda en la bitácora y decide el camino recomendado.
- [ ] **CA3**: Una foto que llega sin metadatos muestra el aviso con su causa probable y cómo subir el original.
- [ ] **CA4**: El mapa ELA de una foto sin cambios guardada al 97 % tiene menos del 2 % de píxeles encendidos; una zona editada sigue destacándose.
- [ ] **CA5**: Una foto ajena a un siniestro muestra el aviso y se puede incluir igual; una de un auto o de un lugar de trabajo no lo muestra (medido sobre un conjunto de prueba sin imágenes de casos reales).
- [ ] **CA6**: Pruebas automáticas de cada parte, sensor de diseño, accesibilidad, teclado y recorridos en computadora y celular.

## Fuera de alcance

- Recuperar metadatos que el celular ya borró: no es posible; solo se puede explicar y ofrecer otro camino.
- Bloquear fotos automáticamente.
