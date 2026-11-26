# Especificación: 045 — Un arnés que se hace cumplir: revisión continua y flujo de integración

- **Rama**: `claude/charming-turing-j7esco` (rama de la sesión del agente: solo puede subir a ella)
- **Estado**: Implementada la parte del agente. Esperan a la autora: correr la limpieza de ramas (etapa 2, CA2) y decidir la configuración de GitHub
- **Requisitos que realiza**: RNF17 (calidad del código), RNF19 (documentación)
- **Reglas de negocio aplicadas**: —
- **Casos de uso**: — (funcionalidad del proceso de desarrollo, no del producto)

Una funcionalidad en tres etapas, como pide su propia política. Las etapas 1 y 2 se escribieron el 2026-11-05 como «038» y «039»; esos números los tomaron después otras funcionalidades integradas, y el 2026-11-16 se unificaron acá.

## Etapa 1 — Revisión continua del arnés (2026-11-05)

### Problema

El 2026-11-05 la autora pidió que el arnés «trabaje todo el tiempo, se mejore día a día y consuma y distribuya la información de manera adecuada», que todos los documentos estén al día y que todo funcione tal como lo declaran.

La auditoría de ese día mostró que el arnés de la 036 hacía cumplir reglas sobre el código, pero **no controlaba su propia documentación**:
- el mapa del arnés declaraba números del 2026-11-02 (282 commits, 84 % con IA, 48 entradas de bitácora, 18 ADR) cuando los reales eran 349, 87 %, 58 y 21;
- 23 entradas de bitácora, desde el 2026-10-21, no figuraban en el índice `docs/bitacora/README.md`;
- medir los números sobre un clon con historial cortado daba un resultado falso (327 commits en lugar de 349) sin ningún aviso.

Como el agente no tiene memoria entre sesiones y trabaja con lo que dicen los documentos, un documento desactualizado le da información falsa.

### Alcance

#### Incluido
- Un verificador que compara lo que declaran los documentos con lo que existe en el repositorio y actualiza solo los números del mapa del arnés.
- Su ejecución al iniciar cada sesión (gancho `SessionStart`), al cerrar cada etapa (`/cerrar-etapa`) y en la integración continua.
- Un comando `/revisar-arnes` para la revisión y la mejora periódicas.
- Las reglas en `CLAUDE.md`: lo declarado tiene que ser verdad, nada se da por verificado sin correrlo y cada error repetido deja un control nuevo.
- Corregir lo que la auditoría encontró desactualizado.

#### Excluido
- Cambiar o quitar controles existentes: queda como propuesta para la autora.
- Verificar servicios externos (AWS, Hedera, Cresium): siguen en `/estado` y en las pruebas de la autora.
- Comparar el contenido de los documentos con la realidad del producto (por ejemplo, si una pantalla hace lo que dice su especificación): eso sigue en las pruebas y en la revisión del Pull Request.

### Criterios de aceptación

- [x] **CA1**: Un enlace relativo roto entre documentos, un comando de la tabla de `CLAUDE.md` sin su archivo (o al revés), un gancho configurado que no existe o una skill sin origen registrado se informan como **error**.
- [x] **CA2**: Una funcionalidad sin especificación o fuera de la tabla, y una entrada de bitácora o un ADR fuera de su índice, se informan como **error**.
- [x] **CA3**: Los números del mapa del arnés se comparan con los reales; con `--actualizar` se reescriben con la fecha del día. Si el historial del clon está cortado, no se calculan (para no publicar números falsos).
- [x] **CA4**: Un cambio en un archivo del arnés posterior a la última fecha del registro de cambios, y una propuesta pendiente de la autora, se informan como **aviso**.
- [x] **CA5**: El verificador corre al iniciar cada sesión (resumen breve que nunca bloquea), en `/cerrar-etapa` y en la integración continua, donde un error impide integrar.
- [x] **CA6**: El verificador tiene pruebas automáticas que cubren cada control, con casos que fallan y casos que pasan.
- [x] **CA7**: Existe `/revisar-arnes` y las reglas nuevas están en `CLAUDE.md`.
- [x] **CA8**: Lo que la auditoría del 2026-11-05 encontró desactualizado queda corregido y el verificador termina sin errores.

## Etapa 2 — Orden del repositorio y del flujo de integración (2026-11-05)

### Problema

El 2026-11-05 la autora preguntó si no había demasiados commits y Pull Requests, pidió limpiar las ramas en desuso, unir las tandas de diseño, mejorar la organización del repositorio y el README principal, siempre con criterio de ingeniería.

Diagnóstico con datos del 2026-11-05 (sobre `desarrollo`):

| Indicador | Valor | Lectura |
|---|---|---|
| Commits | 353 en 18 días con actividad (~19 por día) | Commits chicos son una buena práctica; la cantidad sola no es el problema |
| Commits solo de documentación | 135 (38 %) | El seguimiento se sube en commits sueltos |
| Pull Requests | 73 (~4 por día), mediana de 3 commits | Cada uno cuesta una revisión de la autora: **este es el costo real** |
| Tandas de diseño en ramas y Pull Requests separados | 8 (5 de la 034, 3 de la 028) | Una funcionalidad partida en varias ramas |
| Merges «traer `desarrollo`» a una rama | 18 | Ruido en el historial |
| Ramas en el remoto | 62, de las cuales 51 ya integradas | La guía decía «se elimina la rama» y no se hacía |
| Pasos a producción (`desarrollo` → `main`) | 14, con una sola etiqueta (`v0.1`) | La guía declara versiones etiquetadas y no se cumple |
| Estados de las funcionalidades de diseño | 028 y 034 con estados distintos en su especificación y en la tabla | Lo declarado no coincide |

### Alcance

#### Incluido
- Política escrita de ramas, commits y Pull Requests (una funcionalidad, una rama, un Pull Request; tandas como etapas de la misma rama; seguimiento en el mismo Pull Request; borrar la rama al integrar; versiones etiquetadas).
- Limpieza de las ramas remotas integradas o superadas, con una etiqueta de archivo para las que tenían contenido propio.
- Control nuevo en el verificador del arnés: avisa cuando hay ramas integradas sin borrar.
- Historial unificado del diseño de la interfaz (022, 028, 033, 034 y 037) y estados corregidos.
- README principal al día.
- Propuesta para la autora sobre la configuración de GitHub (integración con *squash*, borrado automático de ramas, etiqueta por versión).

#### Excluido
- Reescribir la historia ya integrada (no se reescribe historia compartida).
- Borrar ramas de trabajo en curso (010, 018, 037 y las de otras sesiones activas).
- Cambiar la configuración de GitHub: no hay acceso desde la sesión y es una decisión de la autora.

### Criterios de aceptación

- [x] **CA1**: `docs/guias/flujo-de-trabajo.md` define la política de ramas, commits, Pull Requests y versiones, con su justificación, y los comandos del flujo la aplican.
- [ ] **CA2**: En el remoto no quedan ramas integradas ni superadas, salvo las de trabajo en curso; lo que tenía contenido propio queda en una etiqueta `archivo/…`. *Pendiente: el script está listo y probado en simulación (52 para borrar, 2 para archivar), pero lo corre la autora porque la sesión del agente recibe 403 al borrar ramas ajenas.*
- [x] **CA3**: El verificador del arnés avisa si hay ramas remotas integradas en `desarrollo` sin borrar, con pruebas.
- [x] **CA4**: Las tandas de diseño están en un solo historial, con su Pull Request y su bitácora, y los estados de la 028 y la 034 coinciden en todos los documentos.
- [x] **CA5**: El README principal describe el sistema, el estado, cómo levantarlo y dónde está cada documento, sin datos desactualizados.
- [x] **CA6**: La propuesta de configuración de GitHub está en `docs/arnes/` y el verificador la recuerda.

## Etapa 3 — Que la política se cumpla sola (2026-11-16)

### Problema

El 2026-11-16 la autora pidió aplicar el arnés de verdad: «no puede ser que estemos abriendo Pull Requests para cualquier cosa, ni commits para cambios mínimos; quiero el repositorio más escalable». La política de la etapa 2 había quedado **solo como texto** y, como toda regla sin sensor, no se cumplía. Los 30 Pull Requests del #67 al #96 (14 días) muestran que casi la mitad son de proceso:

| Patrón | Pull Requests | Ejemplo |
|---|---|---|
| Paso a `main` después de cada funcionalidad | 8 | #94 integra la 041 y enseguida #96 pasa `desarrollo` a `main` |
| Una funcionalidad en varios Pull Requests | 6 de la 010 | #75, #76, #77, #78, #79 y #85 |
| Duplicados o con la base equivocada, cerrados sin integrar | 4 | #93 (la 041 dos veces), #68 (apuntaba a `main`) |
| Merges «incorporar desarrollo» dentro de las ramas | 5 desde el 2026-11-05 | 043, 038, 012 |

Además, la rama de esta misma funcionalidad tenía 9 commits chicos, nunca se integró y sus números (038 y 039) los tomaron otras funcionalidades en el medio; al renumerarla al 044, también estaba tomado por una rama en curso (`funcionalidad/044-portada-y-identidad`). Los números chocan porque cada sesión elige «el siguiente» mirando solo su copia: la rama del informe (`claude/gracious-thompson-9slyyn`) agrega una `039-arnes-del-informe` que también choca.

### Alcance

#### Incluido
- **Control en la integración continua** («Forma del Pull Request»): un Pull Request hacia `desarrollo` falla si trae merges o más de 3 commits. Simulado sobre los Pull Requests reales, habría frenado el #87, el #89 y el #95.
- **`infraestructura/scripts/compactar_rama.sh`**: rebasa la rama sobre `desarrollo` y la deja en un solo commit, conservando las líneas `Co-Authored-By`.
- **Reglas para el agente** en `CLAUDE.md`, `/cerrar-etapa` y la guía: guardar seguido en la rama pero entregar un commit por funcionalidad; un solo Pull Request por rama y nunca uno nuevo si hay uno abierto; el paso a `main` se propone por hito de `docs/versiones.md` o por una corrección urgente de producción, no después de cada funcionalidad; las correcciones chicas esperan a la próxima funcionalidad del área.
- **Control de numeración** en el verificador: error si dos carpetas comparten número; aviso si una rama sin integrar agrega una carpeta con un número ya ocupado. `/especificar` elige el número mirando también las ramas remotas.
- **Índice de la bitácora**: otra vez faltaban 6 entradas (del 2026-11-05 al 2026-11-16); se completó. Con el verificador en la integración continua, ya no se puede integrar sin el índice al día.
- **`limpiar_ramas.sh` más prudente**: solo archiva ramas con contenido propio abandonadas hace más de 14 días y nunca toca la rama actual (antes habría archivado ramas de otras sesiones con trabajo sin integrar).
- **Esta funcionalidad aplicada a sí misma**: las etapas 1 y 2 renumeradas (eran 038 y 039; el 044 también estaba tomado) y todo el trabajo en un solo commit.

#### Excluido
- La configuración de GitHub (*squash*, borrado automático de ramas): sigue como propuesta para la autora; con *squash*, el control de cantidad de commits deja de ser necesario.

### Criterios de aceptación

- [x] **CA1**: Un Pull Request hacia `desarrollo` con merges o con más de 3 commits falla en la integración continua con un mensaje que dice cómo arreglarlo.
- [x] **CA2**: `compactar_rama.sh` deja la rama en un commit sobre `desarrollo`, conserva el contenido y las líneas de co-autoría, se detiene ante conflictos sin cambiar nada y nunca toca `main` ni `desarrollo` (probado en un repositorio de prueba).
- [x] **CA3**: `CLAUDE.md`, `/cerrar-etapa` y la guía de flujo de trabajo dicen cuándo el agente propone un Pull Request y cuándo un paso a `main`.
- [x] **CA4**: El trabajo de la 045 llega a `desarrollo` como un solo commit, sin números repetidos de funcionalidad.
- [x] **CA5**: El verificador da error si dos carpetas comparten número y avisa si una rama sin integrar agrega un número ocupado, con pruebas.

## Preguntas abiertas

- Integrar con *squash* cambia cómo se cuentan los commits del informe: lo decide la autora (ver `docs/arnes/propuesta-flujo-de-integracion.md`).
- La frecuencia de `/revisar-arnes` (semanal) es una propuesta del agente.
