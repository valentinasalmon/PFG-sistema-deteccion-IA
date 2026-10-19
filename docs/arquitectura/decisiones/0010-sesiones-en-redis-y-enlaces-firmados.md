# ADR-0010: Sesiones del servidor en Redis y enlaces firmados sin estado

- **Estado**: Aceptada
- **Fecha**: 2026-10-16
- **Requisitos relacionados**: RF02, RF03, RF04, RF05, RF07, RNF01, RNF02

Complementa la [ADR-0003](0003-sesion-con-cookies.md) (sesión en cookie en lugar de JWT).

## Contexto

La ADR-0003 eligió una sesión en cookie `HttpOnly`. Quedaban dos preguntas abiertas para la funcionalidad 002:

1. **Dónde vive la sesión.** Flask guarda por defecto los datos de la sesión dentro de la cookie, firmados. Así, al cerrar sesión se borra la cookie del navegador, pero una copia robada de esa cookie sigue siendo válida hasta su vencimiento. La especificación exige que, tras cerrar sesión, cualquier solicitud con la misma cookie sea rechazada (CA11), y que restablecer la contraseña cierre todas las sesiones abiertas (CA14).
2. **Cómo se hacen de un solo uso los enlaces enviados por correo** (verificación, recuperación y cambio de correo), que además vencen a las 24 horas o a la hora (RNF01 CA5).

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Sesión firmada dentro de la cookie (por defecto en Flask) | Sin servicio adicional | Cerrar sesión no invalida una copia de la cookie; no se pueden cerrar todas las sesiones de una cuenta |
| **Sesión en Redis con Flask-Session** | Cerrar sesión borra la entrada en el servidor y la cookie deja de servir; el vencimiento por inactividad lo maneja Redis; Redis ya está en el proyecto (ADR-0004) | Si Redis se reinicia, se cierran las sesiones |
| Sesión en PostgreSQL | Persistente | Una consulta a la base en cada solicitud; hay que limpiar las sesiones vencidas |
| Enlaces con tabla de tokens en la base | Control explícito de cada token | Tabla, migración y tarea de limpieza adicionales |
| **Enlaces firmados con itsdangerous, sin tabla** | Vencen solos; nada que guardar ni limpiar | El "un solo uso" se logra con un dato que cambia al usarse (ver Decisión) |

## Decisión

- **Sesiones en Redis** con Flask-Session (prefijo `sesion:`). La cookie solo contiene un identificador aleatorio, con `HttpOnly`, `SameSite=Strict` y, en producción, `Secure`. La inactividad máxima (30 minutos) es el vencimiento en Redis, que se renueva en cada solicitud; la duración máxima (8 horas) se controla con la hora de inicio guardada en la sesión. El identificador de sesión se regenera al iniciar sesión.
- **Cierre de todas las sesiones**: Flask-Login guarda `"id:version_sesion"`. Restablecer o cambiar la contraseña incrementa `version_sesion` y las sesiones anteriores dejan de coincidir. Al cambiar la contraseña desde el perfil, la sesión actual se renueva para no obligar a volver a ingresar.
- **Enlaces firmados** con `itsdangerous`, con un propósito distinto para cada tipo de enlace y su vencimiento. Cada token incluye un dato que cambia al usarse: la cuenta pasa a verificada; cambia el hash de la contraseña (se compara una huella); cambia el correo actual.
- En las pruebas, las sesiones usan `cachelib` en memoria, con el mismo comportamiento.

## Consecuencias

- Se cumplen CA11, CA12 y CA14 sin tablas adicionales; verificado con pruebas automáticas y con Redis real.
- Redis pasa a ser imprescindible también para iniciar sesión, no solo para la cola de tareas. En producción (017) debe tener persistencia para no cerrar las sesiones en cada reinicio.
- La clave secreta firma tanto las sesiones como los enlaces: su filtración permitiría falsificar enlaces. Es obligatoria en producción y nunca se sube al repositorio.
- Las bibliotecas incorporadas son Flask-Session 0.8.0, cachelib 0.17.0 e itsdangerous (incluida con Flask).
