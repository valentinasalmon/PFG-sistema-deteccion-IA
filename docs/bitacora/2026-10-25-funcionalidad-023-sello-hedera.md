# 2026-10-25 — Funcionalidad 023: sello de tiempo en Hedera

## Qué se hizo

- `SelladorHedera` reemplaza a `SelladorBFA`:
  - publica la huella en un tema de Hedera Consensus Service con el SDK oficial `hiero-sdk-python`;
  - confirma el sello en el *mirror node* público, comprobando que el mensaje contiene exactamente esa huella.
- Comando `flask sellos crear-tema`, que pide la clave privada sin mostrarla.
- La tarjeta de la imagen muestra "Registrada en Hedera" con el enlace "Verificar en HashScan". El informe PDF dice "Sello de tiempo en Hedera" y explica cómo verificarlo.
- Terraform y `generar_entorno.sh`:
  - variables `hedera_red`, `hedera_cuenta` y `hedera_tema`;
  - la clave se carga a mano como SecureString en SSM.
- Guía de activación en `docs/guias/despliegue-aws.md`.
- Calidad:
  - backend: flake8 sin errores, pylint 10/10, import-linter con 3 contratos cumplidos, 469 pruebas y cobertura del 97,6 %;
  - frontend: 195 pruebas.

## Decisiones

- **Sin migración:** se reutilizan las columnas de la 016. El recibo pasa a ser `<red>:<tema>/<secuencia>`.
- **Si falta algún dato de Hedera, el sello queda desactivado** con un aviso en el log, en lugar de impedir que arranque la plataforma.
- **El Account ID de la autora no figura en el repositorio**, a pedido suyo: va solo en `terraform.tfvars` (ignorado por Git) y en SSM. Los ejemplos usan cuentas ficticias.
- **Se quitó la CSP para `tsaapi.bfa.ar`.** HashScan se abre como enlace y no necesita permiso de conexión.
- **No se pudo probar contra la red real desde el entorno del agente**, porque el proxy bloquea Hedera. La prueba la hace la autora en *testnet*.

## Pendiente

- La autora crea el tema, carga la clave en SSM, aplica Terraform, despliega y prueba con una imagen.
