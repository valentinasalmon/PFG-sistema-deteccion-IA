# Integración con Identik: respuesta comercial y propuesta de flujo (2026-11-05)

Investigación para la funcionalidad 035 (CP-35): verificación de la identidad de quien registra una aseguradora. La fuente es la respuesta de Identik a la consulta de la autora (correo del 2026-11-05). No se pudo leer la documentación de la API desde el entorno del agente porque el proxy bloquea los dominios de Identik, igual que con Hedera y Cresium. Lo que figura acá es lo que informó Identik. Los nombres de los recursos y los campos se completan cuando se lea la documentación o después de la reunión.

## Lo que ofrece Identik

| Servicio | Qué hace | Precio publicado |
|---|---|---|
| Firma electrónica | Firma con sello de tiempo, auditoría y constancia | Packs prepagos en USD sin abono: 100 documentos por USD 42, 300 por USD 114, 500 por USD 170 y 1.000 por USD 270. Hasta 5 firmantes por documento |
| Verificación biométrica dentro de la firma electrónica | DNI de ambos lados y video del rostro con prueba de vida (tecnología de Namirial) | USD 0,80 por firma verificada, con precio especial hasta diciembre de 2026 |
| Firma digital (art. 2, Ley 25.506) | Certificado de AC Digilogix S.A. con validación contra RENAPER, que da presunción de autoría e integridad | En ARS: 1 documento por $ 21.990, 5 por $ 99.990 y 10 por $ 179.990 |
| Verificación de identidad como servicio aparte | Resultado por *webhook* | No tiene precio de lista: Identik la cotiza según el volumen (10 a 30 por mes) |

**Entorno de pruebas (*sandbox*)**: está habilitado con el correo de la autora. Incluye 5 documentos, 1 verificación biométrica y 1 mensaje de WhatsApp. El token de API se genera desde el panel y se muestra una sola vez. Se guarda como secreto en SSM y nunca en el repositorio. Los documentos que salen del *sandbox* llevan la marca «PRUEBA — FIRMA NO VÁLIDA».

**Integración**: hay dos formas. La persona puede ir a una página de Identik o completar la verificación dentro de la plataforma, en un iFrame. El resultado llega al servidor por *webhook* y no pasa por el navegador.

**RENAPER**: la verificación propia de Identik solo coteja contra RENAPER si la empresa que integra tiene credencial del registro para esa finalidad, y evidentIA no la tiene. La firma digital sí valida contra RENAPER.

**Pendiente de confirmar en la reunión**: si los *webhooks* van firmados y cómo se verifica la firma. También cuánto tiempo y dónde se conservan los datos biométricos y personales (Ley 25.326).

## Propuesta de flujo para la 035 (provisoria)

Se propone una **declaración de representación firmada electrónicamente con verificación biométrica**. No se usa el servicio aparte de verificación de identidad.

1. La persona registra la aseguradora como hasta ahora: la elige del catálogo de la SSN y la cuenta queda pendiente de aprobación (RN36 a RN40).
2. La plataforma genera una declaración breve: «Declaro que represento a [aseguradora, CUIT] y que soy [nombre, DNI]». Se envía a Identik como documento para firmar, con la verificación biométrica obligatoria.
3. La persona firma desde el iFrame o desde la página de Identik: foto del DNI, video del rostro y firma.
4. Identik avisa por *webhook*. La plataforma guarda solo el identificador del documento en Identik, el resultado, la fecha y la huella del PDF firmado. Las imágenes del DNI y del rostro nunca pasan por los servidores de evidentIA.
5. El Administrador ve en la solicitud «Identidad verificada por Identik» con el enlace a la constancia, y decide. La aprobación sigue siendo humana: la verificación es un dato más, no reemplaza la revisión.

**Por qué esta opción:**
- se puede probar ya, porque el *sandbox* incluye la firma con verificación biométrica;
- tiene precio publicado (unos USD 1,22 por aseguradora: USD 0,42 por el documento del pack de 100 y USD 0,80 por la verificación);
- además de verificar a la persona, deja una constancia firmada de que declara representar a la aseguradora, y eso es lo que el Administrador necesita evaluar;
- evidentIA no guarda datos biométricos, porque los trata Identik como encargado. Esto reduce la carga de la Ley 25.326, aunque igual hay que informarlo en la Política de Privacidad y pedir el consentimiento.

**Límite**: el *sandbox* trae una sola verificación biométrica. Hay que reservarla para la prueba completa de punta a punta, o pedir más créditos en la reunión. Las pruebas automáticas usan un proveedor simulado, como con el sello y el cobro.

## Firma del informe PDF (CP-27)

Identik podría firmar también el informe:
- con firma electrónica, a unos USD 0,42 por informe;
- con firma digital, a unos $ 22.000 por informe, un costo que no se puede trasladar a cada análisis.

El sello en Hedera ya prueba que el informe no se modificó y cuándo existía. Lo que la firma agregaría es la autoría de evidentIA. Propuesta: dejarlo como trabajo futuro y no sumarlo antes de la entrega.

## Preguntas para la reunión de 30 minutos

1. **Webhooks**: ¿van firmados (HMAC u otro método)? ¿Con qué encabezado? ¿Se reintentan si el servidor no responde?
2. **Datos**: ¿qué devuelve la verificación (nombre, número de DNI, resultado, puntaje)? ¿Cuánto tiempo conserva Identik las imágenes del DNI y el video? ¿Se pueden pedir borrar? ¿Dónde se alojan (país)? ¿Firman un acuerdo de encargado de tratamiento?
3. **Cotejo**: sin credencial de RENAPER, ¿cómo se valida que el DNI es auténtico, más allá de comparar la cara con la foto?
4. **iFrame**: ¿qué dominios hay que habilitar en la política de seguridad de contenidos (CSP)? ¿Funciona bien en el celular?
5. **Sandbox**: ¿se pueden sumar créditos de verificación biométrica para probar más de una vez?
6. **Proyecto académico**: ¿hay alguna condición especial para un proyecto final de carrera? ¿Puedo mencionar a Identik en el informe y en la defensa?
7. **Firma del informe**: con el sello en Hedera ya en marcha, ¿qué agrega su firma electrónica?
