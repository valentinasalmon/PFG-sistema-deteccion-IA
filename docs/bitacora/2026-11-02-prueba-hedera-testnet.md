# 2026-11-02 — Hedera funcionando en *testnet* en producción

La autora hizo la prueba real de la funcionalidad 023, que estaba pendiente desde el 2026-10-25 porque el entorno del agente no llega a Hedera.

## Cómo se hizo

1. **Clave privada en SSM.** El comando de la guía falló porque se pegó el bloque entero del documento, con las marcas de código, en la terminal. Se cargó desde la consola web de AWS (*Parameter Store*, tipo SecureString). La guía ahora ofrece primero ese camino.
2. **Terraform.** `terraform plan` dio «No changes»: los parámetros `SELLO_TIEMPO`, `HEDERA_RED`, `HEDERA_CUENTA` y `HEDERA_TEMA` ya estaban cargados de antes. No hizo falta `apply`.
3. **Redespliegue** relanzando la última ejecución de `main` en GitHub Actions, para que el servidor regenere su configuración con la clave.
4. **Comprobación** en `/estado` (página agregada el 2026-10-31): «Sello de tiempo · Hedera (testnet): Funciona», con el último sello confirmado.

## Qué demuestra

El estado «Funciona» con fecha solo aparece si el *mirror node* público de Hedera devolvió el mensaje con la huella: el sello es real, no simulado.

## Pendiente

- Comprobar que un informe nuevo muestre la versión del sistema en la página de verificación (029).
- Pasar a *mainnet* antes de la defensa (CP-26).
