# ADR-0023: Flujo de trabajo con GitHub Flow y despliegue continuo

- **Estado**: Aceptada (decisión de mejora del proceso, tomada por la autora el 2026-11-16 a propuesta del agente)
- **Fecha**: 2026-11-16
- **Requisitos relacionados**: RNF20 (integración continua y Conventional Commits), CP-06 (despliegue automático)
- **Reemplaza**: el modelo de ramas de [flujo de trabajo](../../guias/flujo-de-trabajo.md) vigente desde el inicio del proyecto (`main`, `desarrollo` y una rama por funcionalidad o corrección)

## Contexto

El proyecto empezó con un modelo inspirado en Git Flow: `main` para las versiones, `desarrollo` para integrar y una rama `funcionalidad/NNN-…`, `correccion/…` o `documentacion/…` por cada cambio. Era razonable al principio, con funcionalidades grandes que se integraban cada varios días.

A medida que el proyecto creció, y con un agente de IA trabajando todos los días, el modelo mostró tres problemas medidos:

1. **Demasiadas ramas que no cuentan nada.** Al 2026-11-16 había 72 ramas, muchas de un arreglo o un documento suelto (por ejemplo, cinco tandas de la 034 y nueve correcciones sueltas).
2. **Cada cambio pasaba por dos Pull Requests** (la rama hacia `desarrollo` y `desarrollo` hacia `main`) con las mismas verificaciones en los dos: el segundo no agregaba control, solo trabajo. Entre el 10 y el 16 de noviembre la autora abrió siete (#89 a #95) para cinco cambios chicos.
3. **La historia de `main` era ruidosa**: entraban todos los commits intermedios, incluidos los de «corrijo lo anterior».

Además, en el PR #94 la rama se integró con la integración continua todavía corriendo: nada lo impedía.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| A. Seguir igual | Sin trabajo de transición | Los tres problemas siguen |
| B. Ramas permanentes por área (`interfaz`, `hedera`…) | Pocas ramas con nombres claros | Una rama que vive meses se aleja de la principal: conflictos y Pull Requests que arrastran cambios viejos |
| C. **GitHub Flow**: `main` única rama permanente, ramas cortas por objetivo, un Pull Request directo a `main`, protección de `main` y fusión con *squash* | Un solo Pull Request por objetivo; la protección automática reemplaza al paso manual por `desarrollo`; historia de `main` legible (un commit por objetivo); es el modelo de los equipos que despliegan seguido | Cada fusión se publica en producción: exige que la protección de `main` esté activa |

## Decisión

Se adopta **C, GitHub Flow con despliegue continuo**:

- **`main` es la única rama permanente**: siempre en verde y siempre igual a producción (`evidentiaa.com.ar`). Se retira `desarrollo`.
- **Ramas cortas por objetivo**, con el área adelante: `interfaz/…`, `plataforma/…`, `integraciones/…`, `hedera/…`, `infraestructura/…`, `documentacion/…`, `red-neuronal/…`. Todo lo del objetivo se acumula en su rama; un arreglo chico del mismo tema no abre rama propia.
- **Un Pull Request por objetivo, directo a `main`.** No se puede integrar hasta que **todas** las verificaciones estén en verde (protección de la rama en GitHub).
- **Fusión con *squash***: cada Pull Request entra a `main` como un solo commit con el título del Pull Request y su número. El detalle queda en el Pull Request; GitHub conserva las líneas `Co-Authored-By`, así la asistencia de IA sigue declarada en cada commit de `main`.
- **Versiones** con etiquetas (`v1.0`, `v1.1`…) y GitHub Releases, con notas armadas solas a partir de los títulos de los Pull Requests.
- **Dependabot** abre Pull Requests con las actualizaciones de dependencias, que pasan por las mismas verificaciones.
- Las **ramas viejas** se conservan como etiquetas `archivo/<área>/<nombre>` y se borran de la lista; el [mapa de ramas](../../guias/mapa-de-ramas.md) las agrupa por área para la defensa. Las ramas nuevas no necesitan etiqueta: el Pull Request guarda sus commits.
- Los **commits** siguen siendo de un cambio completo y los revisa el gancho del arnés `revisar_commit.py` (formato, 72 caracteres, `Co-Authored-By`).

## Consecuencias

- **Se gana**: la mitad de los Pull Requests, una historia que se lee como la lista de objetivos cumplidos, una lista de ramas que muestra solo el trabajo en curso y una protección automática que antes no existía.
- **Se pierde**: el paso intermedio por `desarrollo`, que permitía juntar varios cambios antes de publicarlos. Se compensa con ramas por objetivo (que ya juntan los cambios de un tema) y con la protección de `main`.
- **Condiciona**: la protección de `main` y la fusión con *squash* tienen que estar configuradas en GitHub ([guía](../../guias/configurar-github.md)); sin ellas, la decisión pierde su red de seguridad.
- **Trazabilidad**: requisito (`docs/especificacion/`) → funcionalidad (`docs/funcionalidades/NNN-…`) → rama y Pull Request → commit en `main` → versión (`docs/versiones.md`).
