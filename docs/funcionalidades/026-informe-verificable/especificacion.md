# 026 · Informe inalterable y verificable

**Requisitos**: RF55 (CA1 a CA3; CA4 opcional) · **Reglas**: RN23, RN29 · **Decisiones**: ADR-0018, CP-27

## Objetivo

Que cualquiera que reciba un informe (un juzgado, un perito, un liquidador) pueda comprobar que el PDF no fue modificado, sin cuenta y sin depender de la palabra de la plataforma.

## Criterios de aceptación

- [x] **CA1 (RF55 CA1)**: la huella SHA-256 de cada PDF se sella en Hedera, con el mismo mecanismo que las imágenes (estado, reintentos cada 15 minutos y auditoría con `tipo: informe`). El primer intento se hace apenas se confirma el informe; el sello nunca impide generarlo.
- [x] **CA2 (RF55 CA2)**: el PDF tiene una sección "Verificación de este informe" con:
  - un QR;
  - la dirección de la página pública;
  - un código de 12 caracteres sin caracteres ambiguos, impreso en grupos de 4.
- [x] **CA3 (RF55 CA3)**: la página pública `/verificar` y `/verificar/<código>`:
  - el navegador calcula la huella del PDF elegido (el archivo nunca se sube) y la compara con la registrada;
  - responde "coincide", "no coincide" o "no es un informe de la plataforma";
  - muestra la fecha, la huella y el sello en Hedera, con enlace a HashScan;
  - sin código, busca el informe por la huella;
  - nunca muestra datos del caso.
- [x] **CA4**: el historial de informes del caso muestra el código (con enlace a la verificación) y el estado del sello.
- [ ] **CA5 (opcional, CP-27)**: firma digital del PDF con certificado de la plataforma.
