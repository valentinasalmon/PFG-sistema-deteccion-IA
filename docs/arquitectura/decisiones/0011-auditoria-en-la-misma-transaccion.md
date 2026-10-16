# ADR-0011: Registro de auditoría en la misma transacción que la acción

- **Estado**: Aceptada
- **Fecha**: 2026-10-16
- **Requisitos relacionados**: RNF06 (CA2, CA3, CA5, CA8), RN34

## Contexto

La funcionalidad 003 crea el registro de auditoría. Tres requisitos condicionan su diseño:

1. **No hay acciones sin rastro** (RNF06 CA8, decisión de la autora): si una entrada no puede guardarse, la acción que la origina se cancela.
2. **Solo inserción** (RNF06 CA3): la aplicación no puede modificar ni eliminar entradas.
3. **Las entradas sobreviven a la cuenta** (RNF06 CA5, RN34): al eliminarse una cuenta, sus entradas se conservan con el usuario anonimizado.

Además, los servicios no conocen Flask (constitución, RNF17), pero la entrada necesita la dirección IP de la solicitud.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Archivo de registro (*logging*) | Simple | No es consultable, no garantiza CA8 y se pierde al rotar los registros |
| Escribir la entrada después de confirmar la acción | Simple | Si la entrada falla, la acción ya quedó aplicada: no cumple CA8 |
| Escribir la entrada en un trabajo de la cola (RQ) | No suma tiempo a la solicitud | Si Redis o el trabajador fallan, la acción queda sin rastro |
| **Tabla propia, escrita en la misma transacción que la acción** | Cumple CA8 con la unidad de trabajo de SQLAlchemy: un único `COMMIT` | Cada acción suma un `INSERT`; los servicios deben agregar la entrada antes de confirmar |
| Disparadores (*triggers*) de PostgreSQL | Imposibles de olvidar | No conocen la IP ni el usuario de la aplicación; no funcionan en SQLite (pruebas) |

## Decisión

- **Tabla `auditoria`** con fecha UTC, usuario, IP, acción, tipo e identificador del recurso (texto, para que cualquier funcionalidad registre sus recursos), resultado (`exitoso`, `fallido`, `rechazado`) y detalle en JSON (JSONB en PostgreSQL).
- **`ServicioAuditoria.registrar`** suma la entrada a la transacción en curso. En las acciones que cambian datos, el servicio la agrega **antes** de que el repositorio confirme; en los rechazos sin otro cambio, la confirma antes de lanzar el error de dominio. Los correos se envían después de confirmar.
- Un manejador de `SQLAlchemyError` deshace la transacción y responde 500 con un mensaje genérico.
- **Solo inserción**: `RepositorioAuditoria` solo expone `agregar` y `confirmar`, y el modelo rechaza `UPDATE` y `DELETE` desde el ORM con eventos de SQLAlchemy.
- **Anonimización**: la clave foránea a `usuarios` usa `ON DELETE SET NULL`.
- **Origen**: la ruta arma `{"ip": request.remote_addr}` y lo pasa a la fábrica de servicios.
- **Sin secretos**: el servicio quita del detalle cualquier clave de contraseña, hash, huella, token, cookie, CSRF o identificador de sesión, como red de seguridad.

## Consecuencias

- CA8 se cumple sin código de compensación: se verificó con pruebas que fuerzan el fallo de la entrada (la cuenta no se crea, no se envía el correo, la sesión no se abre ni se cierra).
- La protección de solo inserción es de la aplicación, no de la base: un acceso directo a PostgreSQL puede modificar la tabla. En la 017 conviene que el usuario de la aplicación no tenga permisos de `UPDATE` ni `DELETE` sobre `auditoria`, salvo el proceso de retención de la 015.
- Detrás de Nginx (017), `remote_addr` es la IP del proxy: hay que configurar `ProxyFix` con la cantidad exacta de proxies.
- Cada funcionalidad nueva agrega sus acciones como constantes en `app/servicios/auditoria.py` y una prueba por acción.
