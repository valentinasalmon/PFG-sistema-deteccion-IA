# Especificación: 038 — Revisión continua del arnés

- **Rama**: `claude/charming-turing-j7esco` (rama de la sesión del agente, sale de `desarrollo`)
- **Estado**: Implementada
- **Requisitos que realiza**: RNF17 (calidad del código), RNF19 (documentación)
- **Reglas de negocio aplicadas**: —
- **Casos de uso**: — (funcionalidad del proceso de desarrollo, no del producto)

## Problema

El 2026-11-05 la autora pidió que el arnés «trabaje todo el tiempo, se mejore día a día y consuma y distribuya la información de manera adecuada», que todos los documentos estén al día y que todo funcione tal como lo declaran.

La auditoría de ese día mostró que el arnés de la 036 hacía cumplir reglas sobre el código, pero **no controlaba su propia documentación**:
- el mapa del arnés declaraba números del 2026-11-02 (282 commits, 84 % con IA, 48 entradas de bitácora, 18 ADR) cuando los reales eran 349, 87 %, 58 y 21;
- 23 entradas de bitácora, desde el 2026-10-21, no figuraban en el índice `docs/bitacora/README.md`;
- medir los números sobre un clon con historial cortado daba un resultado falso (327 commits en lugar de 349) sin ningún aviso.

Como el agente no tiene memoria entre sesiones y trabaja con lo que dicen los documentos, un documento desactualizado le da información falsa.

## Alcance

### Incluido
- Un verificador que compara lo que declaran los documentos con lo que existe en el repositorio y actualiza solo los números del mapa del arnés.
- Su ejecución al iniciar cada sesión (gancho `SessionStart`), al cerrar cada etapa (`/cerrar-etapa`) y en la integración continua.
- Un comando `/revisar-arnes` para la revisión y la mejora periódicas.
- Las reglas en `CLAUDE.md`: lo declarado tiene que ser verdad, nada se da por verificado sin correrlo y cada error repetido deja un control nuevo.
- Corregir lo que la auditoría encontró desactualizado.

### Excluido
- Cambiar o quitar controles existentes: queda como propuesta para la autora.
- Verificar servicios externos (AWS, Hedera, Cresium): siguen en `/estado` y en las pruebas de la autora.
- Comparar el contenido de los documentos con la realidad del producto (por ejemplo, si una pantalla hace lo que dice su especificación): eso sigue en las pruebas y en la revisión del Pull Request.

## Criterios de aceptación

- [x] **CA1**: Un enlace relativo roto entre documentos, un comando de la tabla de `CLAUDE.md` sin su archivo (o al revés), un gancho configurado que no existe o una skill sin origen registrado se informan como **error**.
- [x] **CA2**: Una funcionalidad sin especificación o fuera de la tabla, y una entrada de bitácora o un ADR fuera de su índice, se informan como **error**.
- [x] **CA3**: Los números del mapa del arnés se comparan con los reales; con `--actualizar` se reescriben con la fecha del día. Si el historial del clon está cortado, no se calculan (para no publicar números falsos).
- [x] **CA4**: Un cambio en un archivo del arnés posterior a la última fecha del registro de cambios, y una propuesta pendiente de la autora, se informan como **aviso**.
- [x] **CA5**: El verificador corre al iniciar cada sesión (resumen breve que nunca bloquea), en `/cerrar-etapa` y en la integración continua, donde un error impide integrar.
- [x] **CA6**: El verificador tiene pruebas automáticas que cubren cada control, con casos que fallan y casos que pasan.
- [x] **CA7**: Existe `/revisar-arnes` y las reglas nuevas están en `CLAUDE.md`.
- [x] **CA8**: Lo que la auditoría del 2026-11-05 encontró desactualizado queda corregido y el verificador termina sin errores.

## Preguntas abiertas

- Ninguna. La frecuencia de `/revisar-arnes` (semanal) es una propuesta del agente; la autora puede cambiarla.
