# 2026-10-22 — Corrección de la 016: dirección real del sello de BFA

## Qué se hizo

- La autora probó la conexión desde su PC: `tsa.bfa.ar` no existe (no resuelve), aunque `bfa.ar` responde. La dirección que usaba la 016 era una suposición incorrecta.
- Con las herramientas de desarrollador del navegador, sobre `https://bfa.ar/sello2`, se encontró el servicio real: `https://tsa2.buenosaires.gob.ar/stamp`.
- Se adaptó `SelladorBFA` al formato del proyecto `tsa2` de BFA: `POST /stamp` con `{"hashes": [huella]}` y `GET /verify/<huella>`, que responde `{stamped, stamps}`. No hay recibo aparte: la huella identifica el sello.
- Se cambió la dirección por defecto (`URL_SELLO_BFA`) y se actualizaron las pruebas, el plan y el ejemplo de Terraform.

## Decisiones

- Los nombres de los campos de la respuesta de verificación salen del prototipo público de BFA y no se pudieron confirmar contra el servicio. El cliente acepta las variantes `blocknumber`, `blockNumber` y `block`. Si el bloque no viene, la referencia queda como "BFA".
- El modo real sigue desactivado en producción.

## Pendiente

- El 2026-10-22 el servicio respondía 404 en `/stamp` y `/verify`, y la propia página de BFA daba error al sellar. Se registró como CP-25.
- Cuando responda: repetir la prueba con curl desde la PC y desde el servidor, ajustar los campos si hace falta y activar `sello_tiempo = "bfa"`.
- Decisión de la autora: pedirle a BFA una cuenta habilitada y esperar hasta el 2026-10-29. Si no hay respuesta, cambiar a otro servicio de sello de tiempo (CP-25).
