# 023 · Tareas

- [x] Especificación y plan.
- [x] `SelladorHedera`, `crear_tema_hedera`, `enlace_explorador` y `fecha_de_consenso`; quitar `SelladorBFA`.
- [x] Configuración `HEDERA_*` y dependencia `hiero-sdk-python`.
- [x] Comando `flask sellos crear-tema` (clave oculta).
- [x] `sello.enlace` en la API y "Verificar en HashScan" en la tarjeta de la imagen.
- [x] Textos de la pantalla y del informe PDF: Hedera en lugar de BFA.
- [x] Terraform (`hedera_red`, `hedera_cuenta`, `hedera_tema`) y `generar_entorno.sh` (incluye `HEDERA_CLAVE`).
- [x] Pruebas unitarias y de frontend.
- [x] Guía de activación en `docs/guias/despliegue-aws.md`.
- [x] Prueba real en *testnet* (autora, 2026-11-02): clave cargada en SSM desde la consola de AWS, Terraform ya tenía los datos de Hedera (sin cambios), redespliegue y `/estado` muestra «Sello de tiempo · Hedera (testnet): Funciona» con el último sello confirmado.
- [x] Estado del sello en `/estado` (2026-10-31): modo, red, si hay sellos fallidos o demorados (más de 30 minutos sin confirmar) y la fecha del último confirmado, sin cuenta, tema ni huellas. Sirve para hacer la prueba real sin entrar al servidor.
