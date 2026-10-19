# 2026-10-19 — Funcionalidad 019: eliminación de cuenta y copia de datos personales

## Qué se hizo

Desde "Mi perfil", cada persona puede descargar una copia de sus datos y eliminar su cuenta, como piden los artículos 14 y 16 de la Ley N.° 25.326. Documentos: [especificación](../funcionalidades/019-baja-de-cuenta/especificacion.md), [plan](../funcionalidades/019-baja-de-cuenta/plan.md) y [tareas](../funcionalidades/019-baja-de-cuenta/tareas.md). La rama `funcionalidad/019-baja-de-cuenta` parte de `desarrollo` con la 005 integrada.

- **Copia de los datos**:
  - En JSON y en PDF, con cuenta, consentimiento, organizaciones, invitaciones, casos a cargo y actividad registrada.
  - No incluye datos de otras personas ni el contenido de los casos.
  - Los enlaces vencen a los 15 minutos y además exigen la sesión de la misma persona.
  - Un correo avisa que se generó la copia.
- **Eliminación de la cuenta**:
  - La pantalla muestra qué falta resolver, con enlaces a cada caso y a cada organización.
  - La confirmación es con la contraseña, y todo se elimina en una sola transacción.
  - La auditoría queda sin usuario, se cierran todas las sesiones y llega un correo de confirmación. El correo puede volver a registrarse.
- **Otros cambios**:
  - WeasyPrint 70.0 (ya previsto para el informe de la 008) y Pango en la integración continua.
  - Claves foráneas activas en SQLite durante las pruebas.
  - Accesorio `cuenta` común en `conftest.py` (antes estaba repetido en dos archivos).
  - Política de Privacidad actualizada.
  - Corrección: un correo largo desbordaba "Mi perfil" en un celular.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA4 Copia | Pruebas de API: enlaces y aviso sin enlace, contenido del JSON sin datos de terceros, PDF válido, y enlaces de otra persona, alterados, vencidos o sin sesión. Pruebas de pantalla | Cumplidos |
| CA5 – CA8 Pendientes y contraseña | Pruebas de API y de pantalla: casos, Referente con otros miembros, organizaciones de un solo miembro con cantidad de casos, y contraseña incorrecta auditada | Cumplidos |
| CA9 – CA11 Eliminación | Pruebas de API: cascadas, transferencias canceladas, auditoría sin usuario, otra sesión invalidada, correo de confirmación y nuevo registro con el mismo correo | Cumplidos |

**Cifras:**
- Backend: 247 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 159 pruebas, cobertura del 98 %, ESLint sin errores y compilación correcta.

**Recorrido en navegador real** con PostgreSQL, Redis y correo:
- Una abogada con un estudio compartido, un estudio propio y tres casos descarga su copia en PDF (2 páginas) y en JSON.
- Ve los pendientes y los resuelve: elimina el caso personal, transfiere el del estudio y designa otra Referente.
- Elimina su cuenta y vuelve al inicio de sesión con el aviso. Llega el correo "Tu cuenta fue eliminada".
- En PostgreSQL, todas sus entradas de auditoría quedaron con el usuario vacío.
- Desde el celular, la otra abogada ve que su estudio se eliminaría con su cuenta.
- No hubo errores en la consola ni desbordes a 375 px.

## Decisiones tomadas por el asistente

- **La copia se genera al momento y no se guarda.** RF09 CA4 pide menos de 10 días y el objetivo es la entrega inmediata. Guardarla agregaría otra copia de datos personales que habría que proteger y borrar. Cuando exista S3 (006) se puede revisar.
- **El enlace exige además la sesión.** "URL firmada de corta duración" se cumple con el token de 15 minutos. Pedir también la sesión evita que un enlace filtrado (por ejemplo, en el historial) entregue los datos.
- **El correo de aviso no lleva el enlace.** Sirve para que la persona se entere si la copia no la pidió ella. Así los datos no quedan accesibles desde la casilla.
- **La actividad registrada entra en la copia, sin el detalle.** El derecho de acceso alcanza a la IP y a las acciones. El detalle puede tener datos de otros (por ejemplo, a quién invitó).
- **La pantalla de baja no repite las acciones.** Lleva a cada caso y a cada organización, donde ya están transferir, eliminar y designar Referente con sus confirmaciones.
- **Se exigen todos los casos a cargo, no solo los "activos".** El caso necesita un Responsable: un caso cerrado o archivado tampoco puede quedar sin dueño.
- **Los casos de las organizaciones de un solo miembro no se piden por separado.** Se eliminan con la organización (RN09), y la pantalla avisa cuántos son (CU06 2c).
- **La auditoría se anonimiza con la clave foránea**, sin modificar el registro de solo inserción (RNF06 CA3).
- **Las claves foráneas de SQLite quedan activas en las pruebas.** Antes, las pruebas no veían el `ON DELETE` que sí aplica PostgreSQL. Las 234 pruebas anteriores siguieron pasando.

## Cuestión abierta registrada

- **CP-20 (para la autora y los tutores)**: los correos que quedan en el detalle de algunas entradas de auditoría (intentos de inicio de sesión fallidos y cambios de correo) se conservan después de la baja hasta que se cumplen los 5 años.
  - Propuesta provisoria: conservarlos, informándolo en la Política de Privacidad, que ya lo dice.
  - Alternativa: guardar una huella SHA-256 en lugar del correo.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| La entrada de auditoría de la eliminación y el borrado del usuario podían enviarse a la base en cualquier orden, y fallar la clave foránea | El repositorio envía lo pendiente (`flush`) antes de eliminar la cuenta |
| Una prueba de la 003 exigía que el repositorio de auditoría tuviera solo `agregar` y `confirmar` | Se actualizó: la nueva consulta `de_usuario` es de lectura y no modifica entradas |
| Un correo largo desbordaba los datos fijos de "Mi perfil" a 375 px | `minmax(0, 1fr)` y `overflow-wrap: anywhere` |

## Pendientes

- **Autora**:
  - Revisar e integrar el Pull Request de la 019.
  - Decidir CP-20 con los tutores.
  - Decidir si el cambio en la Política de Privacidad requiere una versión nueva de los términos aceptados.
- **006 y 008**: al eliminar casos (también en la baja), borrar sus imágenes e informes del almacenamiento.
