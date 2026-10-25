# 023 · Plan técnico

## Decisiones

- **Se reutiliza todo lo de la 016**: modelo (`sello_estado`, `sello_recibo`, `sello_referencia`, `sello_fecha`, `sello_simulado`, `sello_intentos`), `ServicioSellos`, la tarea `flask sellos procesar` con su temporizador de 15 minutos, la pantalla y el informe. **No hace falta migración.**
- **`SelladorHedera`** (`app/integraciones/sello_tiempo.py`) reemplaza a `SelladorBFA`:
  - `sellar(huella, tipo="imagen")`: publica el mensaje con `TopicMessageSubmitTransaction` del SDK oficial `hiero-sdk-python` y devuelve `<red>:<tema>/<secuencia>`. El SDK se importa solo en este modo.
  - `verificar(huella, recibo)`: hace `GET <mirror>/api/v1/topics/<tema>/messages/<secuencia>` con `urllib`, decodifica el mensaje y compara la huella. Un 404 significa "todavía no". La fecha es la marca de consenso.
  - Cualquier error del SDK o de la red se informa como `SelloNoDisponible`, y el servicio reintenta.
- **El parámetro `tipo`** queda listo para la 026 (`"informe"`) y la 029 (`"version"`).
- **Configuración**:
  - variables `SELLO_TIEMPO=hedera`, `HEDERA_RED`, `HEDERA_CUENTA`, `HEDERA_CLAVE`, `HEDERA_TEMA` y `HEDERA_URL_MIRROR` (opcional);
  - en producción salen de SSM: Terraform crea red, cuenta y tema solo si están completos, porque SSM no acepta valores vacíos, y la autora crea a mano la clave como SecureString.
- **Enlace público**: `enlace_explorador(recibo)` arma la URL de HashScan, y `imagen_a_dict` la devuelve en `sello.enlace`.
- **Se quitó** el código de BFA y su variable `URL_SELLO_BFA`.

## Pruebas

- **Unitarias**:
  - publicación simulada (`_publicar` reemplazado) y *mirror node* simulado (`urlopen` reemplazado), sin llamar nunca a la red real;
  - contenido del mensaje, recibo, confirmación y fecha;
  - 404, huella ajena, red caída y recibo inválido;
  - creación del sellador según la configuración;
  - comando `crear-tema` con la clave oculta.
- **Frontend**: texto "Registrada en Hedera" y enlace a HashScan.
- **Prueba real**: la hace la autora en *testnet* con los pasos de `docs/guias/despliegue-aws.md`.
