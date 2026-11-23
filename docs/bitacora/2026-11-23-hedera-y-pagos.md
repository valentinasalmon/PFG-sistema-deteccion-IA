# 2026-11-23 · Verificación independiente en Hedera (048) y preparación de Mercado Pago

## Contexto

La autora integró el cambio a GitHub Flow (PR #97) y configuró la protección de `main`. Dependabot abrió 13 Pull Requests sueltos (se agrupó en la 047). Decidió:

- **Hedera se queda en *testnet***, también para la defensa de febrero (reemplaza el pase a *mainnet*).
- Hace falta que una persona pueda verificar en Hedera sin depender de evidentIA.
- Conectar Identik real y cambiar Cresium por **Mercado Pago**.

## Hecho

- **048, verificación independiente** (rama `hedera/verificacion-independiente`): la red y el tema públicos de Hedera en el PDF (dentro de «Verificar este PDF»), una guía pública `/verificar/sin-evidentia` con los comandos para calcular la huella SHA-256 en Windows, Mac y Linux y cómo encontrarla en HashScan, y un recuadro en la página de verificación. La cuenta y su clave nunca se muestran.
- **Mercado Pago**: la autora creó la aplicación (Checkout Pro con la API de **Orders**: Mercado Pago marcó Preferences como heredada y las funciones nuevas salen solo en Orders), las cuentas de prueba y los avisos (eventos «Order» y «Pagos»), y cargó el token de prueba y la clave de los avisos en Parameter Store (`MERCADO_PAGO_TOKEN`, `MERCADO_PAGO_SECRETO_AVISOS`).

## Decisiones

- **El PDF no puede llevar el enlace a su propio mensaje**: el sello del informe se pide después de generarlo. Por eso el PDF da la red, el tema y la guía, y la persona busca su huella entre los mensajes de esa fecha.
- **Un recuadro aparte en el PDF agregaba una tercera página**: el texto se integró al bloque «Verificar este PDF» y el informe sigue en dos páginas; los comandos completos quedan en la guía.
- **Riesgo de *testnet***: la red de prueba se reinicia cada tanto y borra los mensajes. La guía lo avisa; la plataforma conserva los recibos. Queda registrado en CP-26.
- **Mercado Pago**: la integración se escribe con la documentación oficial a la vista, no de memoria (la firma de los avisos es un punto de seguridad). El entorno del agente no podía leer el sitio de Mercado Pago; se pidió permiso para `www.mercadopago.com.ar` y `api.mercadopago.com`, aprobado por la autora, pero todavía no se aplicó en la sesión.

## Pendiente

- Autora: PR de la 047 y de la 048; probar la guía con un informe real (CA3); el token de Identik.
- Agente: `integraciones/mercado-pago` en cuanto la documentación sea accesible; `integraciones/identik` con el token.
