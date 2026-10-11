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
| `GestorTokens` | `generar(proposito, datos) -> str`, `leer(proposito, token, vigencia) -> dict` | `TokenInvalido` |
| `contrasenias` | `problema_de_politica(c) -> str \| None`, `validar_politica(c, campo)`, `generar_hash(c, costo) -> str`, `verificar(c, hash) -> bool` | `ErrorValidacion` |
| `crear_enviador` | `crear_enviador(configuracion) -> EnviadorSMTP \| EnviadorMemoria` | — |

### Variables de entorno nuevas

| Variable | Obligatoria en | Ejemplo en desarrollo |
|---|---|---|
| `URL_FRONTEND` | producción | `http://localhost:5173` |
| `SERVIDOR_CORREO` | producción | `localhost` |
| `PUERTO_CORREO` | — (por defecto 1025) | `1025` |
| `USUARIO_CORREO`, `CONTRASENIA_CORREO` | — | vacías (Mailpit no pide credenciales) |
| `USAR_TLS_CORREO` | — (por defecto `no`; `si` en producción) | `no` |
| `REMITENTE_CORREO` | producción | `Plataforma de análisis de imágenes <no-responder@localhost>` |

### Pantallas

| Ruta | Acceso | Pantalla |
|---|---|---|
| `/iniciar-sesion`, `/registro`, `/recuperar-contrasenia` | Solo sin sesión | Acceso |
| `/verificar-correo`, `/restablecer-contrasenia`, `/confirmar-correo` | Libre (llegan desde un correo) | Enlaces |
| `/terminos`, `/privacidad`, `/estado` | Libre | Textos legales y estado del sistema (la antigua página de la 001) |
| `/`, `/perfil` | Con sesión | Inicio y Mi perfil |

## Cambios en datos

Tabla `usuarios` (migración `a58c14fe9514`):

| Columna | Tipo | Notas |
|---|---|---|
| `id` | entero | Clave primaria |
| `nombre`, `apellido` | texto (100) | Obligatorios |
| `correo` | texto (254) | Único, con índice; se guarda en minúsculas (RN03) |
| `hash_contrasenia` | texto (60) | Hash bcrypt, costo 12 (CA20) |
| `perfil` | texto (20) | `abogado` o `aseguradora` (restricción `ck_usuarios_perfil`); no se modifica (RN01) |
| `colegio`, `empresa` | texto (150) | Opcionales; solo el que corresponde al perfil (RN02) |
| `rol` | texto (20) | `usuario` por defecto; `administrador` en la 014 |
| `version_terminos`, `aceptacion_terminos_en` | texto, fecha | Consentimiento (CA5, Ley 25.326) |
| `correo_verificado_en` | fecha | Nula hasta verificar |
| `intentos_fallidos`, `bloqueado_hasta` | entero, fecha | Bloqueo (CA10) |
| `version_sesion` | entero | Invalida todas las sesiones al cambiar |
| `creado_en`, `actualizado_en` | fecha | Fechas en UTC |

## Bibliotecas nuevas

Todas en su última versión estable a la fecha.

| Biblioteca | Versión | Para qué se usa |
|---|---|---|
| Flask-Login | 0.6.3 | Usuario de la sesión y `@login_required` |
| Flask-Session | 0.8.0 | Sesiones guardadas en Redis |
| cachelib | 0.17.0 | Sesiones en memoria durante las pruebas |
| Flask-WTF | 1.3.0 | Protección CSRF (`CSRFProtect`) |
| bcrypt | 5.0.0 | Hash de contraseñas |
| pydantic | 2.14.0 | Validación de los datos que recibe la API |
| email-validator | 2.3.0 | Formato de los correos en pydantic |
| react-router | 8.4.0 | Rutas del frontend |
| @testing-library/user-event | 14.6.7 | Simular la escritura y los clics en las pruebas |

`itsdangerous` y `Jinja2` ya vienen con Flask.

## Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Sesión en Redis y no en una cookie firmada | Cerrar sesión debe invalidar la cookie (CA11); con una cookie firmada seguiría siendo válida |
| Tokens de enlace sin tabla en la base | Vencen solos y se vuelven de un solo uso por el dato que cambia; menos código y nada que limpiar |
| Mensajes genéricos en registro, recuperación e inicio de sesión | No revelar qué correos están registrados (CA3, CA8, CA13) |
| Cálculo de un hash ficticio cuando el correo no existe | El tiempo de respuesta no delata si la cuenta existe |
| Pedir la contraseña para cambiar el correo | Una sesión olvidada abierta no alcanza para apoderarse de la cuenta |
| Cambiar la contraseña cierra las demás sesiones, pero no la actual | Seguridad sin obligar a volver a ingresar a quien hizo el cambio |
| Contraseña de 72 bytes como máximo | bcrypt 5 rechaza contraseñas más largas; se informa como una regla más |
| La política de contraseñas se valida en el esquema y en el servicio | El formulario muestra todos los errores juntos; el servicio garantiza la regla aunque se lo use desde otro lugar |
| Lista propia de contraseñas comunes | De las 10 000 más usadas (SecLists), solo 5 cumplen la política base; se completa con contraseñas frecuentes en Argentina |
| Fechas en UTC sin zona horaria | Comparaciones uniformes entre PostgreSQL y SQLite (pruebas) |

Se registra como **ADR-0010: sesiones del servidor en Redis y enlaces firmados sin estado**, que complementa la ADR-0003.

## Estrategia de pruebas

**Backend (pytest, 94 pruebas, cobertura 99 %)**

- Unitarias: política de contraseñas (incluidos 72 bytes), tokens (vencido, alterado, de otro propósito), esquemas (mensajes en español, contraseñas sin recortar espacios), correos (plantillas y enviadores), configuración de producción.
- Integración por endpoint, una o más pruebas por cada criterio de aceptación: CA1–CA6 y CA13–CA15 en `test_rutas_cuentas.py`, CA7–CA12 y CA22 en `test_rutas_sesion.py`, CA16–CA19 en `test_rutas_perfil.py`, CA20–CA21 en `test_seguridad.py` (con CSRF activado como en producción).
- El accesorio `aplicacion` no deja abierto el contexto de Flask entre solicitudes: cada solicitud de prueba abre el suyo, como en producción. (Si quedara abierto, Flask-Login reutilizaría el usuario de una solicitud anterior y las pruebas de cierre de sesiones darían un falso resultado.)

**Frontend (Vitest + Testing Library, 50 pruebas, cobertura 98 %, umbral 80 %)**

- Cliente HTTP: CSRF, reintento ante token vencido, errores, sin conexión, sesión vencida.
- Pantallas renderizadas con todas las rutas y la API simulada: acceso, registro, enlaces, recuperación y perfil.

**Manual (en el navegador, con Docker Compose)**

- Recorrido completo: registro → correo en Mailpit → verificación → inicio de sesión → perfil → cambio de contraseña → cierre de sesión.
- Probado en el prototipo con PostgreSQL, Redis y SMTP reales, en escritorio y en pantalla de celular (375 px).

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Si Redis se reinicia, se cierran todas las sesiones | Aceptable: solo obliga a volver a ingresar. En producción, Redis con persistencia (017) |
| El envío de correo falla o tarda | El enviador registra el error y la operación no se cae; en la 007 pasa a segundo plano con reintentos |
| Los correos de prueba llegan a direcciones reales | En desarrollo todo va a Mailpit; nunca se configura un SMTP real fuera de producción |
| Clave secreta filtrada permitiría falsificar enlaces | Solo en `.env` (fuera del repositorio) y obligatoria en producción |
| Textos legales provisorios | Marcados como provisorios y versionados; al cambiarlos se sube la versión |
