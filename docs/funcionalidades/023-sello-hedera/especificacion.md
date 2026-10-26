# 023 · Sello de tiempo en Hedera

**Requisitos**: RF37 (CA1 a CA5), RNF07 (CA3), RNF20 (CA1) · **Regla**: RN23 · **Decisión**: [ADR-0018](../../arquitectura/decisiones/0018-sello-de-tiempo-en-hedera.md)

## Objetivo

Reemplazar Blockchain Federal Argentina por Hedera Consensus Service para acreditar que cada imagen existía, con esa huella exacta, en una fecha determinada. Lo que se veía y hacía con BFA en la 016 se mantiene: estados, reintento, pantalla del caso e informe. Cambia solo el servicio que registra la huella.

## Criterios de aceptación

- [x] **CA1 (RF37 CA1)**: al cargar una imagen se publica su huella en el tema de Hedera de la plataforma, y queda en `enviado` con el recibo `<red>:<tema>/<secuencia>`. Cuando el mensaje aparece en el *mirror node* público, pasa a `sellado`.
- [x] **CA2 (RF37 CA2)**: el sello confirmado guarda la referencia (red, tema y número de mensaje) y la fecha de consenso, y ambas aparecen en la tarjeta de la imagen y en el informe PDF.
- [x] **CA3 (RF37 CA3)**: si Hedera o el *mirror node* no responden, la tarea programada reintenta cada 15 minutos. Cargar o analizar nunca falla por el sello.
- [x] **CA4 (RF37 CA4)**: el sellador sigue siendo intercambiable:
  - `hedera`: el servicio real;
  - `simulado`: desarrollo y pruebas;
  - `desactivado`.
  
  Si el modo es `hedera` y falta la cuenta, la clave o el tema, el sello queda desactivado y se avisa en el log.
- [x] **CA5 (RF37 CA5)**: el mensaje publicado contiene solo `{"v":1,"tipo":"imagen","sha256":...}`, sin datos personales ni del caso. Al verificar, se comprueba que el mensaje contiene exactamente la huella de la imagen.
- [x] **CA6**: la tarjeta de la imagen tiene el enlace "Verificar en HashScan", para que cualquier persona compruebe el sello sin depender de la plataforma.
- [x] **CA7**: la clave privada de la cuenta nunca está en el repositorio ni en el estado de Terraform. Se pide sin mostrarla al crear el tema y se guarda como SecureString en SSM. El Account ID y el Topic ID tampoco se suben al repositorio: van en `terraform.tfvars`.
- [x] **CA8**: el comando `flask sellos crear-tema` crea el tema de la plataforma (una vez por red). Solo la cuenta de la plataforma puede publicar en él.

## Fuera de alcance

- Huella de los informes PDF y página pública de verificación: funcionalidad 026.
- Huella de cada versión desplegada: funcionalidad 029.
- Pasar a *mainnet*: semana de cierre (CP-26).
