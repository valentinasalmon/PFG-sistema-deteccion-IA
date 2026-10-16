# 2026-10-11 — Funcionalidad 002: avance

Entrada de avance. La entrada de cierre de la funcionalidad se agrega cuando se integre en `desarrollo`.

## Qué se hizo

Documentos: [especificación](../funcionalidades/002-cuentas-y-sesion/especificacion.md), [plan](../funcionalidades/002-cuentas-y-sesion/plan.md) y [tareas](../funcionalidades/002-cuentas-y-sesion/tareas.md).

Antes del plan se construyó y probó un prototipo completo de la 002 (backend y frontend) contra PostgreSQL, Redis y un servidor SMTP reales, y en un navegador real en escritorio y en celular. El plan y las tareas se escribieron a partir de ese prototipo ya verificado.

| Tarea | Contenido | Estado |
|---|---|---|
| T01 | Dependencias, variables de entorno y `.gitignore` | Hecha |
| T02 | Configuración de sesiones, cookies, CSRF, bcrypt, bloqueo, enlaces y correo | Hecha |
| T03 | Modelo `Usuario` y `RepositorioUsuarios` | Hecha |
| T04 | Migración `a58c14fe9514` de la tabla `usuarios` | Hecha |
| T05 | Errores de dominio, política de contraseñas y tokens firmados | Hecha |
| T06 | Envío de correos (SMTP y memoria) con 7 correos en texto y HTML | Hecha, con una corrección posterior |
| T07 | Servicios de cuentas, sesión y perfil, y su fábrica | Hecha |
| T11 | `react-router` 8.4.0, `user-event` y umbral de cobertura del 80 % | Hecha |
| T13 (parte del asistente) | Reglas de contraseña y versión de los textos legales | Hecha |
| T14 (parte del asistente) | Componentes de presentación accesibles y sus pruebas | Hecha |

Estado de las verificaciones: backend con 35 pruebas en verde (la cobertura total vuelve a superar el 80 % en la T10), flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos; frontend con 16 pruebas y cobertura del 100 % de líneas.

## Decisiones tomadas

- **Reparto del trabajo** (decisión de la autora): la autora escribe el código central y abre los Pull Requests; el asistente sube con commits propios las pruebas, los estilos, los textos, la configuración y la documentación de seguimiento, con la línea `Co-Authored-By`. La T07 la subió el asistente a pedido de la autora. Registrado en [CLAUDE.md](../../CLAUDE.md) y en la [guía de flujo de trabajo](../guias/flujo-de-trabajo.md).
- **Sesiones en Redis** con Flask-Session (cerrar sesión invalida la cookie) y **enlaces firmados sin tabla** con itsdangerous. Se registrará como ADR-0010 al cerrar la funcionalidad.
- **Contraseñas de 72 bytes como máximo**: bcrypt 5 rechaza contraseñas más largas con un error; se informa como una regla más de la política.
- **La política de contraseñas se valida en el esquema y en el servicio**, para mostrar todos los errores del formulario juntos sin perder la regla en el dominio.
- **Las contraseñas no se recortan**: el resto de los textos se limpian de espacios, las contraseñas se toman tal cual.
- **Cambiar la contraseña cierra las demás sesiones** pero mantiene la actual.
- **react-router 8.4.0** en lugar de la versión 7: la 8 es la vigente y estable desde junio de 2026.
- **Marca unificada** en correos e interfaz: "Plataforma de análisis de imágenes", color `#1e3a5f`.

## Tecnologías incorporadas

| Tecnología | Versión | Para qué |
|---|---|---|
| Flask-Login | 0.6.3 | Usuario de la sesión y `@login_required` |
| Flask-Session | 0.8.0 | Sesiones guardadas en Redis |
| cachelib | 0.17.0 | Sesiones en memoria durante las pruebas |
| Flask-WTF | 1.3.0 | Protección CSRF |
| bcrypt | 5.0.0 | Hash de contraseñas |
| pydantic + email-validator | 2.14.0 / 2.3.0 | Validación de los datos que recibe la API |
| react-router | 8.4.0 | Rutas del frontend |
| @testing-library/user-event | 14.6.7 | Simular escritura y clics en las pruebas |

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| En el prototipo, las pruebas de cierre de sesiones daban un falso resultado | El accesorio `aplicacion` dejaba abierto el contexto de Flask y Flask-Login reutilizaba el usuario entre solicitudes. Ahora cada solicitud abre su propio contexto, como en producción |
| Una contraseña de más de 72 bytes producía un error 500 | Regla de 72 bytes en la política y verificación que responde "incorrecta" sin fallar |
| Tras iniciar sesión no se volvía a la pantalla pedida y faltaba el aviso de cierre | Las guardas de rutas deciden el destino y el motivo de salida |
| Archivos creados con otro nombre o en otra carpeta (`usuarios.py`, la lista de contraseñas comunes, una plantilla) | Diagnóstico con `ls` y `find`; desde ahora cada tarea verifica la cantidad y la ubicación de los archivos |
| `tareas.md` subido vacío y `plan.md` cortado al pegar | Contenido entregado directamente en el chat y comparado contra el original |
| La plantilla de texto de "contraseña cambiada" tenía el contenido del correo de bloqueo | Corregida, y se agregó una prueba que comprueba el texto propio de cada correo |
| Tras reiniciar la computadora, `python` y `flake8` no se encontraban | Faltaba activar el entorno virtual (`source .venv/bin/activate`) en la terminal nueva |
| Entre la T07 y la T09 la cobertura total baja del 80 % | Es esperable hasta la T10; mientras tanto se verifica con `pytest --no-cov` |

## Pendientes

- **Autora**: T08 (`app/esquemas/`), T09 (seguridad y rutas), T12 (`src/api/`), T13 (contexto y hooks), T14 (`Encabezado`, `Disposiciones`, `Rutas`, `FormularioReenvio`), T15 (pantallas, `App.jsx`, `main.jsx`) y T16 (recorrido manual).
- **Asistente**: `test_esquemas.py` (después de la T08), pruebas de integración de la API (T10, después de la T09), pruebas del cliente (T12), `global.css`, textos legales, página 404 y pruebas de pantallas (T15), ADR-0010 y entrada de cierre.

## Actualización 2026-10-15: backend terminado

| Tarea | Contenido | Estado |
|---|---|---|
| T08 | Esquemas de validación (autora) y sus pruebas (asistente) | Hecha |
| T09 | Autenticación, rutas de la API y manejo de errores en JSON (autora) | Hecha: 15 rutas en `/api` |
| T10 | Pruebas de integración de la API (asistente) | Hecha: 94 pruebas, cobertura 99,6 % |
| T15 (parte del asistente) | Términos de Uso, Política de Privacidad y página no encontrada, con pruebas | Hecha |

- El backend de la 002 cumple los criterios CA1 a CA22 del lado del servidor, verificados por pruebas automáticas. flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- **Revisión de accesibilidad con la skill `ui-ux-pro-max`**: los textos, botones, enlaces y avisos superan el contraste 4,5:1 (WCAG AA). El borde de los campos (`#d1d5db`) tenía 1,47:1 y WCAG 1.4.11 exige 3:1 para el contorno de los controles: se cambia a `#6b7280` (4,8:1) en `global.css`, que se sube junto con las pantallas. Los errores ya cumplían la guía de la skill: se muestran debajo de cada campo, asociados con `aria-describedby`, y el resumen se anuncia con `role="alert"`.
- Se quitó una línea vacía al comienzo de dos plantillas de correo.
- La instalación de `react-router` en la computadora de la autora falló por un corte de red (`ETIMEDOUT`); se documentaron los pasos para reintentar y para forzar IPv4 en WSL.

### Pendientes actualizados

- **Autora**: T12 (`src/api/`), T13 (contexto y hooks), T14 (`Encabezado`, `Disposiciones`, `Rutas`, `FormularioReenvio`), T15 (pantallas, `App.jsx`, `main.jsx`) y T16 (recorrido manual).
- **Asistente**: pruebas del cliente (después de la T12), `global.css`, `renderizar.jsx` y pruebas de pantallas (después de la T15), ADR-0010 y entrada de cierre.

## Actualización 2026-10-16: frontend terminado

| Tarea | Contenido | Estado |
|---|---|---|
| T12 | Cliente de la API con CSRF (autora) y sus pruebas (asistente) | Hecha |
| T13 | Contexto de sesión y hooks (autora); utilidades y pruebas (asistente) | Hecha |
| T14 | Encabezado, disposiciones, guardas y reenvío (autora); componentes de presentación (asistente) | Hecha |
| T15 | 7 pantallas con formularios (autora); rutas, inicio, estado, estilos y pruebas (asistente) | Hecha |

- **Frontend**: 59 pruebas, cobertura del 99 %, ESLint sin errores y compilación de producción correcta.
- **Recorrido en un navegador real** con PostgreSQL, Redis y un servidor de correo: registro con los errores juntos, verificación por correo, enlace reutilizado rechazado, mensaje genérico ante credenciales inválidas, inicio, edición del perfil, cambio de contraseña sin perder la sesión, cierre de sesión con aviso, página de estado y diseño sin desbordes en celular (375 px). Sin errores en la consola.
- **Correcciones durante la integración**: el archivo `useAccionAICargar.js` (con I mayúscula) se renombró a `useAccionAlCargar.js`; las guardas de navegación se movieron de `src/componentes/` a `src/rutas/`, como indica la [estructura del repositorio](../arquitectura/estructura-del-repositorio.md).
- **Decisión de arquitectura registrada**: [ADR-0010](../arquitectura/decisiones/0010-sesiones-en-redis-y-enlaces-firmados.md), sesiones del servidor en Redis y enlaces firmados sin estado.

### Pendientes para cerrar la 002

- **Autora**: T16 (recorrido manual con Docker y Mailpit) y el Pull Request hacia `desarrollo`.
- **Asistente**: revisar la integración continua del Pull Request, marcar los criterios de aceptación, cambiar el estado a "Completado" y escribir la entrada de cierre de la bitácora.
