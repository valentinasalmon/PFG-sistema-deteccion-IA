# Plan técnico: 002 — Cuentas y sesión

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

La funcionalidad agrega la primera entidad del dominio, `Usuario`, y todo el ciclo de vida de una cuenta: registro con consentimiento, verificación del correo, inicio y cierre de sesión con bloqueo por intentos fallidos, recuperación y cambio de la contraseña, y edición del perfil. Respeta la arquitectura en capas de la 001:

```
React (pantallas) ──▶ api/cliente.js (JSON + CSRF) ──proxy /api──▶ Flask
                                                                     │
  rutas/cuentas.py · rutas/sesion.py · rutas/perfil.py   (validan con esquemas pydantic)
                                │
  servicios/servicio_cuentas · servicio_sesion · servicio_perfil   (reglas de negocio)
        │                    │                     │
  repositorios/repositorio_usuarios   servicios/tokens   servicios/servicio_correos
        │                                                   │
  modelos/usuario ──▶ PostgreSQL               integraciones/correo ──▶ Mailpit (SMTP)
                                                            plantillas/correos/*.html|txt
  seguridad/autenticacion (Flask-Login + Flask-Session) ──▶ Redis (sesiones)
```

**Sesiones del lado del servidor.** La cookie solo contiene un identificador aleatorio; los datos de la sesión viven en Redis (Flask-Session). Cerrar sesión borra la entrada de Redis, por lo que la cookie anterior deja de servir (CA11). El identificador que guarda Flask-Login es `"id:version_sesion"`: al restablecer o cambiar la contraseña se incrementa `version_sesion` y todas las sesiones anteriores quedan inválidas (CA14). La inactividad se controla con el vencimiento de la sesión en Redis (30 minutos, renovado en cada solicitud) y la duración máxima con la hora de inicio guardada en la sesión (8 horas) (CA12).

**Enlaces firmados sin estado.** Los enlaces de verificación, recuperación y cambio de correo llevan un token firmado con `itsdangerous` que vence solo (24 h, 1 h y 24 h). No se guardan en la base: cada token incluye un dato que cambia al usarse, y eso lo vuelve de un solo uso (la cuenta pasa a verificada; cambia el hash de la contraseña; cambia el correo).

**Correos.** Se envían por SMTP en forma directa (en la 007 pasan a la cola de tareas). En desarrollo los captura Mailpit (<http://localhost:8025>); en las pruebas, un enviador en memoria (patrón Strategy). Cada correo tiene versión HTML y de texto, generadas con plantillas Jinja2.

## Capas afectadas

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Configuración | `app/configuracion/entornos.py` (modificado) | Sesiones, cookies, CSRF, bcrypt, bloqueo, vigencia de enlaces, correo |
| Extensiones | `app/extensiones.py` (modificado) | `gestor_sesiones` (Flask-Login), `sesiones_servidor` (Flask-Session), `proteccion_csrf` (Flask-WTF) |
| Fábrica | `app/__init__.py` (modificado) | Registra modelos, sesiones, CSRF, autenticación y el enviador de correo |
| Utilidades | `app/utilidades/tiempo.py` | `ahora_utc()`: fecha y hora UTC sin zona, igual en toda la aplicación |
| Modelos | `app/modelos/usuario.py` | Tabla `usuarios` |
| Repositorios | `app/repositorios/repositorio_usuarios.py` | Consultas y guardado de usuarios |
| Servicios | `app/servicios/errores.py` | Excepciones de dominio, sin HTTP |
| Servicios | `app/servicios/contrasenias.py` | Política de contraseñas y hash bcrypt |
| Servicios | `app/servicios/tokens.py` | Tokens firmados de los enlaces |
| Servicios | `app/servicios/servicio_correos.py` | Arma cada correo con su plantilla y lo envía |
| Servicios | `app/servicios/servicio_cuentas.py` | Registro, verificación, reenvío, recuperación y restablecimiento |
| Servicios | `app/servicios/servicio_sesion.py` | Autenticación con bloqueo y carga del usuario de la sesión |
| Servicios | `app/servicios/servicio_perfil.py` | Datos personales, cambio de contraseña y de correo |
| Servicios | `app/servicios/fabrica.py` | Arma cada servicio con sus dependencias reales |
| Integraciones | `app/integraciones/correo.py` | `EnviadorSMTP`, `EnviadorMemoria` y `crear_enviador` |
| Esquemas | `app/esquemas/__init__.py`, `app/esquemas/cuentas.py` | Validación de entradas con pydantic y mensajes en español |
| Seguridad | `app/seguridad/autenticacion.py` | Flask-Login, 401 en JSON, duración máxima, inicio, renovación y cierre de sesión |
| Rutas | `app/rutas/cuentas.py`, `sesion.py`, `perfil.py`, `errores.py` | Endpoints y traducción de errores a JSON |
| Plantillas | `app/plantillas/correos/*.html` y `*.txt` | Texto de los 7 correos |
| Recursos | `backend/recursos/contrasenias_comunes.txt` | Lista de contraseñas comunes |
| Migraciones | `migraciones/versions/a58c14fe9514_crear_tabla_de_usuarios.py` | Crea la tabla `usuarios` |
| Frontend | `src/api/cliente.js`, `cuentas.js`, `sesion.js`, `perfil.js` | Único acceso a la API; CSRF y errores |
| Frontend | `src/contextos/`, `src/hooks/` | Sesión compartida, formularios y acciones de enlaces |
| Frontend | `src/componentes/` | Campos accesibles, avisos, reglas de contraseña, encabezado, disposiciones y guardas de rutas |
| Frontend | `src/paginas/` | 12 pantallas (ver "Pantallas") |
| Frontend | `src/App.jsx`, `src/main.jsx` | Rutas de la aplicación |

## Patrones aplicados

- **Repository**: `RepositorioUsuarios` es el único que consulta la tabla `usuarios`.
- **Service Layer**: los servicios contienen las reglas (bloqueo, un solo uso de los enlaces, perfil inmodificable) y no conocen Flask; lanzan excepciones de dominio que `rutas/errores.py` traduce a HTTP.
- **Inyección de dependencias + Factory**: `servicios/fabrica.py` arma cada servicio con su repositorio, sus correos y sus tokens. Las rutas solo conocen la fábrica.
- **Strategy**: `EnviadorSMTP` (desarrollo y producción) y `EnviadorMemoria` (pruebas) cumplen la misma interfaz `enviar(correo) -> bool`. En la 017 se apunta el SMTP a Amazon SES sin cambiar código.
- **Adapter**: `integraciones/correo.py` aísla `smtplib`.
- **Decorator**: `@login_required` protege las rutas con sesión (base del decorador de roles de la 014).

## Contratos

### API

Todas las respuestas son JSON. Los errores tienen la forma `{"mensaje": "...", "codigo": "...", "errores": {"campo": "..."}}`. Toda solicitud `POST`, `PATCH` o `DELETE` debe llevar la cabecera `X-CSRFToken`.

| Método y ruta | Sesión | Cuerpo | Respuestas |
|---|---|---|---|
| `GET /api/sesion/csrf` | No | — | 200 `{csrf}` |
| `POST /api/cuentas/registro` | No | `nombre, apellido, correo, contrasenia, perfil, colegio?, empresa?, acepta_terminos` | 201 `{mensaje}` (igual si el correo ya existía); 400 `datos_invalidos` |
| `POST /api/cuentas/verificacion` | No | `token` | 200; 400 `enlace_invalido` |
| `POST /api/cuentas/verificacion/reenvio` | No | `correo` | 200 `{mensaje}` genérico |
| `POST /api/cuentas/recuperacion` | No | `correo` | 200 `{mensaje}` genérico |
| `POST /api/cuentas/recuperacion/restablecer` | No | `token, contrasenia` | 200; 400 `enlace_invalido` o `datos_invalidos` |
| `POST /api/sesion` | No | `correo, contrasenia` | 200 `{usuario, csrf}`; 401 `credenciales_invalidas`; 403 `cuenta_no_verificada` |
| `GET /api/sesion` | Sí | — | 200 `{usuario}`; 401 `sesion_requerida` |
| `DELETE /api/sesion` | Sí | — | 200 |
| `GET /api/perfil` | Sí | — | 200 `{usuario}` |
| `PATCH /api/perfil` | Sí | `nombre?, apellido?, colegio?, empresa?` | 200 `{usuario}`; 400 si se envía `perfil` o un dato que no corresponde al perfil |
| `POST /api/perfil/contrasenia` | Sí | `contrasenia_actual, contrasenia_nueva` | 200; 400 |
| `POST /api/perfil/correo` | Sí | `correo_nuevo, contrasenia` | 200; 400; 409 `conflicto` |
| `POST /api/perfil/correo/confirmacion` | No | `token` | 200; 400; 409 |

Códigos de error comunes: 400 `csrf_invalido`, 404 `no_encontrado`, 405 `metodo_no_permitido`.

### Backend

| Elemento | Firma | Excepciones |
|---|---|---|
| `ServicioCuentas` | `registrar(solicitud)`, `verificar_correo(token)`, `reenviar_verificacion(correo)`, `solicitar_recuperacion(correo)`, `restablecer_contrasenia(token, nueva)` | `ErrorValidacion`, `TokenInvalido` |
| `ServicioSesion` | `autenticar(correo, contrasenia) -> Usuario`, `obtener_usuario_de_sesion(identificador) -> Usuario \| None` | `CredencialesInvalidas`, `CuentaNoVerificada` |
| `ServicioPerfil` | `actualizar_datos(usuario, cambios) -> Usuario`, `cambiar_contrasenia(usuario, actual, nueva) -> Usuario`, `solicitar_cambio_correo(usuario, correo_nuevo, contrasenia)`, `confirmar_cambio_correo(token)` | `ErrorValidacion`, `ConflictoDatos`, `TokenInvalido` |
