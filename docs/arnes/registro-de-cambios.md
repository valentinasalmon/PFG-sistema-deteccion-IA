# Registro de cambios del arnés

Cada cambio en las reglas, los comandos, los ganchos o los controles del arnés, con el problema que lo motivó. Reconstruido desde el historial de git y la bitácora; desde la funcionalidad 036 se completa al cerrar cada etapa (`/cerrar-etapa`).

| Fecha | Cambio | Pieza | Motivo |
|---|---|---|---|
| 2026-10-08 | Estructura del repositorio, `CLAUDE.md`, constitución y comandos `/especificar`, `/planificar`, `/tareas` | Guías | Trabajar con un agente de IA desde el inicio con reglas escritas y un flujo guiado por especificaciones |
| 2026-10-08 | Instalación de 7 skills con registro de origen y huella (`skills-lock.json`) | Guías | Darle al agente conocimiento especializado (diseño, revisión, diagramas, crítica) de fuentes identificables |
| 2026-10-09 | Validación de los mensajes de commit en español (commitlint) | Sensores | Historial legible y uniforme, con tipos en español |
| 2026-10-09 | Integración continua en GitHub Actions | Sensores | Que ningún cambio, del agente o de la autora, se integre sin pasar estilo, análisis y pruebas |
| 2026-10-09 | import-linter con los contratos de capas y ganchos de pre-commit (incluida la detección de claves privadas) | Sensores | La arquitectura en capas y la regla de no subir secretos eran solo texto; pasan a verificarse en cada prueba y en cada commit |
| 2026-10-11 | Primer reparto del trabajo con el asistente | Persona | Definir qué hace el agente y qué hace la autora |
| 2026-10-16 | Nuevo reparto: el agente escribe y sube todo; la autora revisa, integra y decide | Persona | El primer reparto (la autora copiaba los archivos) era lento y propenso a errores |
| 2026-10-19 | Despliegue automático desde `main`, condicionado a la integración continua | Sensores | Que a producción llegue solo lo verificado |
| 2026-10-21 | Guía de identidad visual y ADR-0017 (descargo de IA, persona en el circuito, umbrales publicados) | Guías | Toda pantalla y todo resultado con la misma identidad y las mismas garantías legales |
| 2026-10-25 | Regla: todo hallazgo o decisión va a `docs/informe-final/insumos.md` | Memoria | Que el informe final no dependa de recordar lo que pasó semanas atrás |
| 2026-10-26 | Auditoría de dependencias y configuración de Nginx en la integración continua (030) | Sensores | Revisión de seguridad OWASP: detectar vulnerabilidades conocidas automáticamente |
| 2026-10-29 | Regla: el agente actualiza Trello al terminar cualquier trabajo, sin que se lo pidan | Memoria | La autora perdía el seguimiento del avance |
| 2026-10-30 | Regla: toda la red neuronal se documenta aparte, en `docs/red-neuronal/`, y siempre al día | Memoria | La documentación de la red estaba dispersa |
| 2026-10-30 | Trabajo repartido en dos sesiones de agente (red neuronal y sistema) con traspaso entre ellas | Persona / Memoria | Evitar que una sola sesión mezcle contextos distintos |
| 2026-10-31 | Página `/estado` con el estado del sello en Hedera | Sensores | El agente no llega a producción; hacía falta una forma de verificar una integración externa sin entrar al servidor |
| 2026-11-02 | Guía de despliegue: primero la consola web para cargar secretos | Guías | La autora pegó en la terminal un bloque de la guía con las marcas de código |
| 2026-11-02 | **Funcionalidad 036**: ganchos de Claude Code (secretos y estilo), comando `/cerrar-etapa`, comandos alineados con el reparto vigente, mapa del arnés, este registro y ADR-0021 | Todas | Consolidar el arnés como un sistema: hacer cumplir automáticamente reglas que eran solo texto y corregir comandos desactualizados desde el 2026-10-16 |
| 2026-11-02 | Primer falso positivo del gancho de secretos (bloqueó un commit cuyo mensaje nombraba un archivo secreto); el agente intentó corregir el gancho y Claude Code se lo impidió por ser auto-modificación de un control. La corrección queda como [propuesta para la autora](propuesta-ajuste-gancho-secretos.md) | Sensores / Persona | El arnés protege sus propios controles: un agente no puede debilitar lo que lo vigila sin aprobación humana |
| 2026-11-02 | Regla: toda integración con un servicio externo se prueba contra el servicio real antes de darla por terminada, y su estado se ve en `/estado` | Guías | El sello en Hedera pasó todas las pruebas automáticas, pero en producción el PDF salía con el sello pendiente: los dobles de prueba no reproducían la demora real |
| 2026-11-05 | **Funcionalidad 038**: verificador de la documentación del arnés (`verificar_arnes.py`) al iniciar cada sesión (`SessionStart`), en `/cerrar-etapa` y en la integración continua; los números del mapa del arnés se calculan solos | Sensores | La auditoría del día encontró el mapa del arnés con números del 2026-11-02 y 23 entradas de bitácora fuera de su índice desde el 2026-10-21: nadie lo había notado porque ningún control revisaba los documentos |
| 2026-11-05 | Los números del proceso solo se calculan con el historial completo del clon | Sensores | Medidos sobre el clon parcial de la sesión en la nube daban 327 commits en lugar de 349, sin ningún aviso |
| 2026-11-05 | Comando `/revisar-arnes` y sección «El arnés se revisa solo y mejora siempre» en `CLAUDE.md`: lo declarado tiene que ser verdad, nada se da por verificado sin correrlo, cada error repetido deja un control nuevo y el agente no debilita controles por su cuenta | Guías / Persona | Pedido de la autora: el arnés tiene que trabajar todo el tiempo, mejorarse día a día y distribuir la información de manera adecuada |
