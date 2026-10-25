# ADR-0018: Sello de tiempo en Hedera en lugar de Blockchain Federal Argentina

- **Estado**: Aceptada (decisión de la autora, 2026-10-25)
- **Fecha**: 2026-10-25
- **Requisitos relacionados**: RF37, RF55, RNF07, RNF20

## Contexto

La funcionalidad 016 sellaba la huella de cada imagen en Blockchain Federal Argentina (BFA). En las pruebas del 2026-10-22, el servicio 2.0 estaba caído y el 1.0 rechazaba las conexiones desde fuera de Argentina, donde está el servidor de AWS. Además, la autora quiere que los informes PDF sean inalterables, lo que también requiere registrar su huella en una red pública. Ver [la investigación](../../investigacion/2026-10-25-hedera.md).

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| BFA, pidiendo el sello desde el navegador | Infraestructura argentina, gratis | El servidor no controla el proceso; depende de dónde esté el usuario; el servicio 2.0 está caído |
| OpenTimestamps (Bitcoin) | Gratis, sin cuenta | Confirmación de 1 a 12 horas; no permite publicar datos propios |
| Ethereum o Polygon | Muy conocidas | Tarifas variables, gestión de billetera más compleja |
| **Hedera Consensus Service** | Tarifas fijas y bajas en USD, finalidad en segundos, sin geobloqueo, verificación pública (HashScan y *mirror node*), SDK oficial en Python | Hay que comprar HBAR para *mainnet* y custodiar una clave privada |

## Decisión

Se usa **Hedera Consensus Service** para sellar la huella SHA-256 de cada imagen y de cada informe PDF. Se implementa como un `SelladorHedera` dentro del patrón Strategy existente (ADR-0006 y ADR-0012), y lo pide el servidor. Se mantiene `SelladorSimulado` para desarrollo y pruebas. Se elimina `SelladorBFA`.

## Consecuencias

- **Se gana:** sellado controlado por el servidor, verificable por cualquiera y con un costo previsible (alrededor de US$ 0,0008 por mensaje).
- **Se pierde:** el respaldo de una infraestructura estatal argentina, que se documenta como limitación en el informe final.
- **Queda condicionado a:** la creación de una cuenta y de un tema en Hedera; el resguardo de la clave privada en SSM, nunca en el repositorio; y la elección de red (CP-26).
