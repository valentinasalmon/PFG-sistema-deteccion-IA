# 2026-10-16 — Funcionalidad 003: auditoría

## Qué se hizo

Se creó el registro de auditoría y se empezó a usar con todas las acciones de cuenta y sesión de la funcionalidad 002. Documentos: [especificación](../funcionalidades/003-auditoria/especificacion.md), [plan](../funcionalidades/003-auditoria/plan.md) y [tareas](../funcionalidades/003-auditoria/tareas.md). Decisión de arquitectura: [ADR-0011](../arquitectura/decisiones/0011-auditoria-en-la-misma-transaccion.md).

- **Backend**: tabla `auditoria` (migración `3d740a09a480`), modelo `EntradaAuditoria` que rechaza modificaciones y eliminaciones, `RepositorioAuditoria` de solo inserción, `ServicioAuditoria` y registro de 12 acciones en los servicios de cuentas, sesión y perfil. Las rutas pasan la dirección IP a la fábrica de servicios y un manejador nuevo responde 500 genérico si la base falla.
- **Frontend**: la Política de Privacidad tiene una sección nueva, "Registro de actividad", que informa qué se guarda, para qué, que no se puede modificar y que se conserva cinco años.

## Nuevo reparto del trabajo

Desde esta funcionalidad, a pedido de la autora, el asistente escribe y sube todo el trabajo de cada funcionalidad (especificación, plan, tareas, código, pruebas y documentación) y la autora revisa, abre e integra los Pull Requests y toma las decisiones importantes. Quedó registrado en [CLAUDE.md](../../CLAUDE.md) y en la [guía de flujo de trabajo](../guias/flujo-de-trabajo.md). Todos los commits del asistente siguen llevando la línea `Co-Authored-By`.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1, CA2 Contenido y sin secretos | Prueba de los campos de una entrada; prueba que recorre registro, inicios, cambio y restablecimiento de contraseña y busca contraseñas, hash, tokens e identificador de sesión en todas las entradas; prueba unitaria de la limpieza del detalle | Cumplidos |
| CA3 – CA6 Sesión | Pruebas de inicio exitoso, cada motivo de fallo, correo intentado, bloqueo con vencimiento y cierre manual y por duración máxima | Cumplidos |
| CA7 – CA10 Registro, verificación y contraseña | Pruebas de cada acción, con enlaces usados, alterados y vencidos | Cumplidos |
| CA11, CA12 Perfil y correo | Pruebas del valor anterior y nuevo, de los rechazos y del cambio de correo completo | Cumplidos |
| CA13 Solo inserción | Pruebas: no hay rutas de auditoría, el repositorio solo agrega y el modelo rechaza `UPDATE` y `DELETE` | Cumplido |
| CA14 Acción cancelada | Pruebas que fuerzan el fallo de la entrada: la cuenta no se crea, no se envía el correo, el perfil no cambia y la sesión no se abre ni se cierra | Cumplido |

Cifras: backend con 127 pruebas, cobertura del 99,6 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos; frontend con 75 pruebas. Recorrido en navegador real con PostgreSQL, Redis y correo: las 6 entradas del recorrido aparecen en la tabla con la IP, el recurso y el detalle en JSONB, y al borrar la cuenta (dentro de una transacción deshecha) las entradas se conservan con el usuario vacío. La migración se probó con `upgrade`, `check` y `downgrade`.

## Decisiones tomadas por el asistente

Tomadas sin consultar, según el nuevo reparto. Cualquiera puede revertirse.

- **Misma transacción** para la acción y su entrada (ADR-0011), en lugar de registrar después o en la cola: es la única forma de cumplir CA14 sin código de compensación.
- **Resultados**: `fallido` cuando falla una verificación (contraseña, enlace); `rechazado` cuando la regla impide la acción (correo existente, cambio de perfil, correo en uso, reenvío o recuperación de un correo inexistente).
- **Motivos de los enlaces inválidos**: `vencido`, `alterado`, `ya_usado` o `no_corresponde`; se agregaron a `TokenInvalido` sin cambiar los mensajes que ve la persona.
- **Edición del perfil sin cambios** (los mismos datos) no genera entrada, porque no modifica nada.
- **Correos en el detalle**: se guarda el correo indicado en reenvíos y recuperaciones de correos inexistentes, igual que en los inicios de sesión fallidos (RNF06 CA7), para detectar intentos de enumerar cuentas.
- **Solo inserción en la aplicación**: la restricción de permisos en PostgreSQL queda para la 017.
- **Versión de los textos legales**: sigue en 1.0, porque el texto todavía es provisorio y no se pidió una nueva aceptación.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| Para registrar la creación de una cuenta con su identificador hacía falta el `id` antes de confirmar | Nuevo `RepositorioUsuarios.preparar`, que agrega y hace `flush` sin confirmar |
| La primera versión de la limpieza del detalle quitaba cualquier clave con "sesion", incluida la que indica que se cerraron las sesiones | Se limitó a `id_sesion` e `identificador_sesion` |
| pylint marcaba código duplicado entre los constructores de dos servicios | Se reordenaron las asignaciones de uno de ellos |

## Pendientes

- **Autora**: revisar y abrir el Pull Request de `funcionalidad/003-auditoria` hacia `desarrollo`. Validar con los tutores el texto nuevo de la Política de Privacidad, junto con el resto de los textos legales.
- **017**: `ProxyFix` para la IP real detrás de Nginx y quitar al usuario de la aplicación los permisos de `UPDATE` y `DELETE` sobre `auditoria`.
- **015**: eliminación de las entradas con más de 5 años. **019**: anonimización al eliminar la cuenta (ya preparada con `ON DELETE SET NULL`).
- Siguiente según la [hoja de ruta](../guias/hoja-de-ruta.md): **004, Organizaciones e invitaciones**.
