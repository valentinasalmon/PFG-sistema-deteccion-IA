# 2026-10-19 — Funcionalidad 005: casos y permisos

## Qué se hizo

Ya existe la unidad de trabajo de la plataforma: el caso. Se puede crear, buscar, editar, cerrar, archivar, compartir, transferir y eliminar, con permisos por persona y por organización. Documentos: [especificación](../funcionalidades/005-casos/especificacion.md), [plan](../funcionalidades/005-casos/plan.md) y [tareas](../funcionalidades/005-casos/tareas.md). La rama `funcionalidad/005-casos` parte de `desarrollo` con la 021 integrada.

- **Backend**:
  - Tablas `casos` y `accesos_caso` (migración `057c1b5b72d9`).
  - `ServicioCasos` con permisos, estados, retención, accesos y transferencias.
  - 15 rutas nuevas, 5 correos nuevos (texto y HTML) y 8 acciones de auditoría.
  - `RepositorioBase` común a los repositorios de casos y organizaciones.
- **Reglas pendientes de la 004**:
  - Abandonar exige transferir antes los casos a cargo.
  - Al desvincular a un miembro, sus casos pasan al Referente y pierde sus accesos.
  - Al eliminar una organización se eliminan sus casos y la pantalla informa cuántos.
- **Frontend**:
  - Pantalla "Casos": búsqueda y filtros guardados en la dirección, paginación y casos que esperan aceptación.
  - "Nuevo caso" y la pantalla de cada caso, con las secciones que habilita el permiso.
  - El inicio muestra cuántos casos hay en cada estado.
  - Enlace "Casos" en el encabezado y componentes `CampoSeleccion` y `CampoAreaTexto`.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA6 Crear y consultar | Pruebas de API (numeración, fecha futura, espacios inválidos, perfil Aseguradora sin espacio personal, 404 sin permiso, listado sin archivados, filtros y búsqueda sin acentos) y de pantalla | Cumplidos |
| CA7 – CA12 Editar y estados | Pruebas de API (edición con valor anterior y nuevo en la auditoría, Lector sin edición, transiciones válidas e inválidas, retención al cerrar, desarchivar sin reiniciar y reabrir sin vencimiento) y de pantalla | Cumplidos |
| CA13 – CA16 Compartir | Pruebas de API (miembro, toda la organización con miembros futuros, permiso más alto, caso personal, no miembro, cambio de nivel y revocación con aviso) y de pantalla | Cumplidos |
| CA17, CA18 Transferir | Pruebas de API y de pantalla (organización con y sin Colaboración; personal con aceptación, rechazo y cancelación) | Cumplidos |
| CA19, CA20 Eliminar | Pruebas con número incorrecto y correcto (sin distinguir mayúsculas), avisos y bloqueo En análisis | Cumplidos |
| CA21 – CA23 Reglas de la 004 | Pruebas de abandono, desvinculación y eliminación de la organización | Cumplidos |
| CA24 Auditoría | Pruebas de las entradas exitosas y rechazadas | Cumplido |

**Cifras:**
- Backend: 234 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 153 pruebas (24 nuevas), cobertura del 98 %, ESLint sin errores y compilación correcta.
- Migración: probada con `upgrade`, `check` y `downgrade` en PostgreSQL.

**Recorrido en navegador real** con PostgreSQL, Redis y correo, con dos cuentas:
- Una Referente crea el estudio, invita a una abogada y esta acepta desde el celular.
- La Referente crea un caso del estudio y lo comparte en Lectura. La invitada lo ve en solo lectura, sin acciones (375 px, sin desbordes).
- La Referente cierra el caso y aparece el vencimiento de la retención.
- La Referente crea un caso personal y lo transfiere por correo. La invitada lo acepta desde "Casos" y lo elimina escribiendo el número en minúsculas.
- La búsqueda por "exp-55" encuentra "EXP-55/2026" y queda en la dirección, y el inicio muestra el resumen por estado.
- No hubo errores en la consola.

## Decisiones tomadas por el asistente

- **La transferencia de un caso personal requiere aceptación; la de organización es inmediata.**
  - En la organización, los dos son miembros y el Referente ya puede reasignar casos (RN14).
  - En el espacio personal, el caso entra en el espacio de otra persona, que tiene que estar de acuerdo (RF33 CA2).
  - Solo puede recibirlo una cuenta con perfil Abogado, porque las de aseguradora no tienen espacio personal.
- **Las personas con perfil Aseguradora no tienen espacio personal**: crean casos en su aseguradora aprobada (continúa la decisión de la 021).
- **Las organizaciones pendientes de aprobación no pueden tener casos**: "Nuevo caso" no las ofrece y el backend las rechaza.
- **Número de caso**:
  - Sale del identificador de la fila (secuencia global, RN16), con un número provisorio único dentro de la misma transacción.
  - Así no hay una tabla de contadores ni carreras entre solicitudes.
- **Búsqueda por expediente** sobre una columna normalizada (minúsculas y sin tildes), igual en SQLite y en PostgreSQL.
- **Reabrir vuelve a Borrador** hasta que la 008 agregue los informes: `tiene_informes` ya está preparado para cambiar ese comportamiento.
- **Las acciones posibles las calcula el backend** y viajan en cada respuesta; el frontend no repite las reglas de permisos ni de estados.
- **Sin permiso, 404; con un permiso menor, 403**, igual que en las organizaciones.
- **Al transferir dentro de una organización, el anterior Responsable conserva Colaboración por defecto**, con una casilla para no conservarla (RF33 CA3).
- **Los filtros del listado viven en la dirección** (`/casos?estado=cerrado`): se pueden compartir, sobreviven a recargar y el inicio los usa como accesos directos.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| El número provisorio superaba los 20 caracteres de la columna | Se acortó a `TMP-` y 16 caracteres hexadecimales |
| Pylint marcaba código duplicado entre los repositorios | Se extrajo `RepositorioBase` con `preparar`, `quitar` y `confirmar` |
| Una plantilla de correo usaba `destinatario`, que choca con el parámetro del método de envío | Se renombró la variable a `receptor` |
| El aviso de éxito aparecía antes de que se recargara la lista de accesos | Primero se recarga el caso y después se muestra el aviso |

## Pendientes

- **Autora**: revisar e integrar el Pull Request de la 005. RN12, RN14 y RF33 CA2 siguen marcadas como **[PROPUESTA]** en la especificación general hasta que las confirme.
- **006**: imágenes del caso; reemplaza la sección "Imágenes e informes" de la pantalla del caso.
- **008**: `Caso.tiene_informes` real, para que reabrir vuelva a Analizado.
- **013, 014 y 015**: panel completo, límites del plan y destrucción al vencer la retención.
