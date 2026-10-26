# 029 · Huella de cada versión desplegada en Hedera ("host tokenizado")

**Requisitos**: RF56 (CA1, CA2) · **Reglas**: RN29 · **Decisiones**: ADR-0018, CP-29 (opción a)

## Objetivo

Poder probar con qué código se analizó cada caso. Cada versión que se despliega deja su huella sellada en una red pública, y cada análisis queda enlazado a esa versión.

## Criterios de aceptación

- [x] **CA1 (RF56 CA1)**:
  - al desplegar, `desplegar.sh` calcula el SHA-256 del artefacto desplegado y ejecuta `flask sellos registrar-version` con el commit y esa huella;
  - la versión se registra una sola vez por commit, se audita (`version.despliegue`) y su huella se sella en Hedera con `tipo: version`;
  - si Hedera no responde, la tarea de sellos lo reintenta;
  - el despliegue nunca falla por esto.
- [x] **CA2 (RF56 CA2)**: cada análisis guarda el commit de la plataforma en sus versiones. La página pública de verificación de un informe muestra "Analizado con evidentIA X (código abc1234)", con su sello y el enlace a HashScan.
- [x] **CA3**: la versión no se imprime en el PDF, por pedido de la autora.
