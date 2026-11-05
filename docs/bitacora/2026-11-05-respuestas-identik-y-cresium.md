# 2026-11-05 — Respuestas de Identik y Cresium

Rama `claude/kind-hopper-ize2ln`, creada desde `desarrollo`. Es la sesión dedicada a las cuestiones abiertas, los correos y las preguntas a los tutores.

## Realizado

- Se analizó la respuesta de Identik. El entorno de pruebas ya está habilitado y los precios están publicados. Se registró en `docs/investigacion/2026-11-05-integracion-identik.md`, con una propuesta de flujo para la 035 y las preguntas para la reunión de 30 minutos.
- Se redactaron las respuestas a Identik y a Cresium, para que la autora las envíe. Cresium pide monotributo para el alta, así que se le consulta si tiene un entorno de pruebas o una opción para proyectos académicos.
- Se actualizaron CP-34 y CP-35, la lista de pendientes, que ahora tiene tres preguntas nuevas para los tutores, y los insumos del informe final.

## Decisiones (provisorias, a confirmar por la autora)

- **035**: se usará una declaración de representación firmada electrónicamente con verificación biométrica, y no el servicio aparte de verificación. Motivos: se puede probar ya en el entorno de pruebas, tiene precio publicado (unos USD 1,22 por aseguradora), deja una constancia del vínculo con la aseguradora y evidentIA no guarda datos biométricos.
- **Firma del informe con Identik**: pasa a trabajo futuro, porque el sello en Hedera ya cubre la integridad.
- **Cobro real con Cresium**: si no aparece una opción sin monotributo antes del 2026-11-10, pasa a trabajo futuro.

## Pendiente

- La autora envía los dos correos y agenda la reunión con Identik.
- Después de la reunión: especificar la 035 con `/especificar`, guardar el token del *sandbox* en SSM y no en el repositorio, e integrar.
- No se pudo leer la documentación de la API de Identik, porque el proxy del entorno bloquea sus dominios.
