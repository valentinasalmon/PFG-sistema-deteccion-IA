# 2026-10-22 — Corrección de la 016: Sello de Tiempo 1.0 de BFA

## Qué se hizo

- Sello de Tiempo 2.0 (`tsa2.buenosaires.gob.ar`) estaba caído. La autora probó la versión 1.0 en `https://bfa.ar/sello` con las herramientas de desarrollador del navegador. El sellado funcionó: `POST https://tsaapi.bfa.ar/api/tsa/stamp/` con el formulario `file_hash` respondió 200 con `{"temporary_rd": "...", "status": "success"}` y descargó el archivo `.rd.temp`.
- Se volvió al formato de la versión 1.0, con la dirección correcta (`tsaapi.bfa.ar`). Los datos se envían como formulario, que es como los manda la página de BFA.
- Cuando la verificación devuelve el recibo definitivo (`permanent_rd`), se guarda en lugar del temporal.

## Decisiones

- La respuesta de `verify` todavía no se pudo observar: la página de BFA dio "no se pudo conectar" al verificar. El cliente busca el bloque y la fecha en la raíz de la respuesta o en `attestation`. Si no la confirma en 96 intentos (24 h), la imagen queda como fallida, pero el recibo temporal se conserva.

## Pendiente

- La autora prueba `stamp` y `verify` con curl desde su PC y desde el servidor. Si funcionan, se activa `sello_tiempo = "bfa"`.
