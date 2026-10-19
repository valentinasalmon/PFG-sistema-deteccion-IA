# Plan técnico: 003 — Auditoría

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Se agrega una tabla `auditoria` de solo inserción y un `ServicioAuditoria` que los demás servicios usan para registrar cada acción. El servicio no conoce Flask: recibe el **origen** de la solicitud (la dirección IP) desde la fábrica de servicios, que lo arma la ruta.

La atomicidad de CA14 se logra con la sesión de SQLAlchemy, que es la unidad de trabajo de cada solicitud:

- **Acciones que cambian datos** (registro, verificación, bloqueo, cambio de contraseña, edición del perfil, cambio de correo): el servicio agrega la entrada de auditoría a la transacción **antes** de que el repositorio confirme. La acción y su entrada se confirman juntas en un único `COMMIT`; si falla, no se aplica ninguna de las dos. Los correos se envían después de confirmar, así que una acción cancelada tampoco envía correos.
- **Acciones rechazadas o fallidas sin otro cambio** (enlace inválido, correo existente, contraseña actual incorrecta): el servicio registra la entrada y la confirma antes de lanzar el error de dominio.
- Si la base rechaza la entrada, se lanza un error de SQLAlchemy: un manejador nuevo deshace la transacción y responde **500** con un mensaje genérico.

La identidad del recurso se guarda como `tipo_recurso` + `id_recurso` (texto), para que las funcionalidades siguientes (casos, imágenes, informes) registren sus propios recursos sin cambiar la tabla. El detalle es un JSON libre; antes de guardarlo, el servicio quita cualquier clave sensible (contraseñas, hashes, tokens, sesiones, cookies), como red de seguridad de CA2.

## Capas afectadas

| Capa | Archivos nuevos o modificados | Responsabilidad |
|---|---|---|
| Modelos | `app/modelos/entrada_auditoria.py` (nuevo) | Entrada de auditoría; bloquea `UPDATE` y `DELETE` desde el ORM |
| Repositorios | `app/repositorios/repositorio_auditoria.py` (nuevo); `repositorio_usuarios.py` (`preparar`) | Agregar entradas sin confirmar; confirmar la transacción; reservar el identificador de un usuario nuevo |
| Servicios | `app/servicios/auditoria.py` (nuevo); `servicio_cuentas.py`, `servicio_sesion.py`, `servicio_perfil.py`, `fabrica.py`, `errores.py`, `tokens.py` | Registro de cada acción, con motivo del fallo |
| Seguridad | `app/seguridad/origen.py` (nuevo); `autenticacion.py` | IP de la solicitud; cierre por duración máxima registrado |
| Rutas | `cuentas.py`, `sesion.py`, `perfil.py`, `errores.py` | Pasan el origen a la fábrica; cierre manual registrado; 500 genérico |
| Migraciones | `migraciones/versions/<id>_crear_tabla_de_auditoria.py` | Tabla e índices |
| Frontend | `src/paginas/PaginaPrivacidad.jsx` | Informa el registro de auditoría |

## Patrones aplicados

- **Repository**: `RepositorioAuditoria` es la única puerta de escritura y solo expone `agregar` y `confirmar` (CA13).
- **Unit of Work** (de SQLAlchemy): la acción y su entrada viajan en la misma transacción (CA14).
- **Inyección de dependencias** con la fábrica de servicios: las pruebas pueden armar los servicios con dobles.

## Contratos

```python
class ServicioAuditoria:
    def __init__(self, repositorio, origen=None): ...
    def registrar(self, accion, resultado, *, usuario=None, recurso=None,
                  detalle=None, confirmar=False) -> EntradaAuditoria
    # usuario: Usuario que actuó o None. recurso: (tipo, id) o un Usuario.
    # resultado: "exitoso" | "fallido" | "rechazado".
    # confirmar=True confirma la transacción (acciones sin otro cambio).
```

Las fábricas de servicios reciben un tercer argumento opcional `origen` (`{"ip": "..."}`).

`TokenInvalido` agrega el atributo `motivo`: `vencido`, `alterado` o `ya_usado`.

Acciones registradas (constantes en `app/servicios/auditoria.py`):

| Acción | Resultados | Detalle |
|---|---|---|
| `cuenta.registro` | exitoso; rechazado (`correo_existente`) | perfil; motivo |
| `cuenta.verificacion` | exitoso; fallido (motivo del enlace) | motivo |
| `cuenta.reenvio_verificacion` | exitoso; rechazado (`correo_inexistente`, `ya_verificada`) | correo indicado |
| `sesion.inicio` | exitoso; fallido (`correo_inexistente`, `contrasenia_incorrecta`, `cuenta_bloqueada`, `cuenta_no_verificada`) | correo intentado si no existe |
| `cuenta.bloqueo` | exitoso | `bloqueado_hasta`, intentos |
| `sesion.cierre` | exitoso | motivo: `manual` o `duracion_maxima` |
| `contrasenia.recuperacion` | exitoso; rechazado (`correo_inexistente`) | correo indicado |
| `contrasenia.restablecimiento` | exitoso; fallido (motivo del enlace) | motivo |
| `contrasenia.cambio` | exitoso; fallido (`contrasenia_incorrecta`) | — |
| `perfil.edicion` | exitoso; rechazado (`cambio_de_perfil`, `dato_de_otro_perfil`) | `{campo: {anterior, nuevo}}` |
| `correo.solicitud_cambio` | exitoso; fallido (`contrasenia_incorrecta`); rechazado (`correo_en_uso`) | `anterior`, `nuevo` |
| `correo.cambio` | exitoso; fallido (motivo del enlace) | `anterior`, `nuevo` |

## Cambios en datos

Tabla `auditoria`:

| Columna | Tipo | Notas |
|---|---|---|
| `id` | BigInteger | Clave primaria |
| `fecha` | DateTime | UTC, índice |
| `id_usuario` | Integer, nulo | FK a `usuarios.id` con `ON DELETE SET NULL` (preparación de RN34 y RNF06 CA5) |
| `ip` | String(45) | Admite IPv6 |
| `accion` | String(60) | Índice |
| `tipo_recurso` | String(40), nulo | |
| `id_recurso` | String(64), nulo | |
| `resultado` | String(10) | Restricción: `exitoso`, `fallido`, `rechazado` |
| `detalle` | JSON (JSONB en PostgreSQL) | |

Índice compuesto `(id_usuario, fecha)` para reconstruir la actividad de una cuenta.

## Bibliotecas nuevas

Ninguna.

## Estrategia de pruebas

- Unitarias: limpieza de claves sensibles, origen por defecto, modelo que rechaza modificaciones y eliminaciones, repositorio sin operaciones de cambio.
- Integración: una prueba por acción de la tabla anterior a través de la API, comprobando acción, resultado, usuario, IP, recurso y detalle (CA1, CA3 a CA12); ninguna entrada contiene la contraseña, el hash ni el token usados (CA2); si guardar la entrada falla, la cuenta no se crea, no se envía el correo y la respuesta es un 500 genérico (CA14).
- Migración: `flask db upgrade` y `flask db check` contra PostgreSQL.

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Detrás de Nginx (017), `remote_addr` sería la IP del proxy | En la 017 se configura `ProxyFix` con la cantidad exacta de proxies; anotado como pendiente |
| La tabla crece sin límite | Índices por fecha; la eliminación a los 5 años es de la 015 |
| Una acción nueva olvida registrar su entrada | Cada funcionalidad agrega sus acciones a la tabla de este plan y una prueba por acción |
| Inicios de sesión fallidos masivos llenan la tabla | Aceptado: es la evidencia de un ataque (RNF06 CA7); el bloqueo limita los intentos por cuenta |
