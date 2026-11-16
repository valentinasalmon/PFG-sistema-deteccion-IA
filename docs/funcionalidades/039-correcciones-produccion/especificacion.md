# 039 · Correcciones de producción

**Estado**: implementada (2026-11-10). **Rama**: `funcionalidad/039-correcciones-produccion`. **Pedido**: la autora, al probar la 038 en producción, y pendientes propuestos por el agente.

## Problema

- Al escanear el QR «Análisis detallado» del PDF e iniciar sesión, la autora llegaba al análisis pero veía solo el resumen: el detalle de cada técnica seguía plegado, así que el QR no cumplía lo que promete.
- Los correos de los casos decían «caso» también a las aseguradoras, cuando las pantallas y el PDF ya dicen «siniestro» (037).
- El sensor de diseño y los recorridos de punta a punta eran obligatorios para cambios de interfaz, pero solo se corrían a mano.
- La guía de usuario no reflejaba la 037 ni la 038.
- La autora va a comprar el dominio y necesita los pasos completos.

## Alcance

- El QR del PDF abre el análisis con **todo el detalle desplegado** (`?etapa=analisis&detalle=completo`). Los PDF ya emitidos conservan su enlace anterior.
- Los correos de los casos (acceso, transferencia, solicitud y respuesta, eliminación, aviso de retención y fin o fallo del análisis) dicen «siniestro» cuando la persona destinataria es de una aseguradora, en el asunto, el texto y el botón.
- Trabajo nuevo **Interfaz** en la integración continua: levanta la base, Redis, el backend y el frontend, crea la cuenta de demostración y corre el sensor de diseño y el recorrido del abogado en computadora y celular. Falla si hay un paso roto, un problema de diseño o un error de la página.
- Guía de usuario al día (vocabulario, aprobación de todas las organizaciones, invitaciones, QR de un solo uso, PDF breve con dos QR, administración).
- Guía de despliegue: pasos detallados para comprar el dominio, apuntar el DNS, pasar la plataforma al dominio, verificar el dominio en SES y salir del modo de prueba.

## Criterios de aceptación

- [x] **CA1**: El enlace del QR «Análisis detallado» abre el análisis con los resultados y el detalle de cada técnica desplegados; sin el parámetro, siguen plegados.
- [x] **CA2**: Una persona de una aseguradora recibe correos que dicen «siniestro»; una de un estudio, «caso».
- [x] **CA3**: El trabajo «Interfaz» corre en cada Pull Request y en `main`, y falla ante un paso roto o un problema de diseño.
- [x] **CA4**: La guía de usuario y la de despliegue describen el comportamiento actual.

## Fuera de alcance

- La aprobación de estudios en producción (la autora no ve el correo ni el pendiente): en el entorno local funciona con el código de producción por los dos caminos; la causa más probable es SES en modo de prueba. Queda como verificación de la autora (ver la bitácora).
