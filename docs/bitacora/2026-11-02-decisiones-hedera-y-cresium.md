# 2026-11-02 — Decisiones de la autora, revisión de Hedera e investigación de Cresium

Rama `documentacion/decisiones-y-cresium`, creada desde `funcionalidad/034-cuarta-tanda`, porque edita las mismas cuestiones abiertas.

## Decisiones de la autora

- **CP-37 (Clarity)**: se usa solo durante las pruebas y se quita antes de la versión final. El texto provisorio de la política queda tal cual, porque ya dice «durante el período de prueba». Se sumó a pendientes la tarea de quitarlo.
- **CP-26 (Hedera)**: primero *testnet*; antes de la defensa, compra de HBAR y paso a *mainnet*.
- **CP-20 (correos en la auditoría al borrar una cuenta)**: la autora pidió que el agente proponga y documente. Se mantiene la regla actual (se conservan cinco años, sin vínculo con la cuenta), con la alternativa de una huella con clave secreta (HMAC) si los tutores piden minimizar. El motivo está en la cuestión.
- **CP-36 (marca)**: se mantiene evidentIA para el proyecto académico (ya estaba resuelta así).
- **CP-38 (nueva, precios)**: se definen con el análisis de costos.
- **CP-35 (Identik)**: se usa para las aseguradoras; falta definir el flujo.
- **010 y 012 (red neuronal)**: siguen en el otro chat.
- **Revisión de la 034, cierre (018) y dominio**: los hace la autora al final.

## Hedera: ¿ya funciona de verdad?

El código está completo y es real:
- usa el SDK oficial (`hiero-sdk-python`) para publicar la huella en el tema;
- confirma cada sello contra el *mirror node* público y guarda la fecha de consenso;
- un temporizador lo reintenta cada 15 minutos, y el despliegue registra la huella de cada versión.

Lo que **nunca se probó es contra la red real**: el proxy del entorno del agente bloquea Hedera (igual que el 2026-10-25). La prueba la hace la autora en *testnet* con la guía de `despliegue-aws.md`, a la que se sumaron dos pasos: comprobar en `/estado` y ver el sello en HashScan, con qué revisar si dice «Desactivado», «Con demoras» o «Con fallas».

Se corrigió la descripción del servicio y del temporizador de sellos, que todavía decían «Blockchain Federal Argentina».

## Cresium

Investigación en `docs/investigacion/2026-11-02-integracion-cresium.md`. Cresium sí tiene API (cobros con CVU propio por pedido y avisos firmados con HMAC-SHA256), pero no se pudo leer su documentación desde el entorno. El sistema ya tiene el proveedor intercambiable; faltan los precios, la cuenta con entorno de pruebas y unos 2 o 3 días de implementación.
