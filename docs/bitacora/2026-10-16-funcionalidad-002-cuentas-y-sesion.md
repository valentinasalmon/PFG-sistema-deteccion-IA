# 2026-10-16 — Funcionalidad 002: cuentas y sesión

## Qué se hizo

Se implementó el ciclo de vida completo de una cuenta: registro con consentimiento, verificación del correo, inicio y cierre de sesión con bloqueo por intentos fallidos, recuperación y cambio de la contraseña, y edición del perfil con cambio de correo. Documentos: [especificación](../funcionalidades/002-cuentas-y-sesion/especificacion.md), [plan](../funcionalidades/002-cuentas-y-sesion/plan.md) y [tareas](../funcionalidades/002-cuentas-y-sesion/tareas.md). El detalle del día a día está en la [entrada de avance](2026-10-11-funcionalidad-002-avance.md).

- **Backend**: modelo `Usuario` y su migración, servicios de cuentas, sesión y perfil, 14 endpoints nuevos en `/api`, sesiones en Redis, protección CSRF y 7 correos con plantillas en texto y HTML.
- **Frontend**: cliente de la API con CSRF, contexto de sesión, guardas de navegación y 12 pantallas: acceso, enlaces de los correos, perfil, inicio, textos legales, estado y página no encontrada.
- **Forma de trabajo**: desde esta funcionalidad, la autora escribe el código central y el asistente sube las pruebas, los estilos, los textos, la configuración y la documentación de seguimiento ([CLAUDE.md](../../CLAUDE.md)).

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA6 Registro y verificación | Pruebas de integración y recorrido con Mailpit | Cumplidos |
| CA7 – CA12 Sesión | Pruebas (bloqueo, cookie reutilizada, 8 horas) y recorrido | Cumplidos |
| CA13 – CA16 Contraseña | Pruebas (enlace de un solo uso, vencido, alterado) y recorrido | Cumplidos |
| CA17 – CA19 Perfil | Pruebas y recorrido | Cumplidos |
| CA20 – CA22 Seguridad | Pruebas con CSRF activado, hash bcrypt y 401 sin sesión; cookie revisada en el navegador | Cumplidos |

Cifras finales: backend con 94 pruebas y cobertura del 99,6 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos; frontend con 59 pruebas y cobertura del 99 %, ESLint sin errores y compilación correcta. Integración continua del [Pull Request #3](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/3) en verde en sus tres trabajos.

## Decisiones tomadas

- [ADR-0010](../arquitectura/decisiones/0010-sesiones-en-redis-y-enlaces-firmados.md): sesiones del servidor en Redis y enlaces firmados sin estado.
- El perfil (Abogado o Aseguradora) no puede cambiarse después del registro (RN01, CP-12).
- RF08 y RF09 (baja de la cuenta y copia de los datos) pasan a la funcionalidad 019.
- Contraseñas de 72 bytes como máximo, política validada en el esquema y en el servicio, y contraseñas sin recortar espacios.
- Mensajes genéricos y hash ficticio para no revelar qué correos están registrados.
- Contorno de los campos con contraste 4,8:1 (WCAG 1.4.11), detectado con la skill `ui-ux-pro-max`.

## Tecnologías incorporadas

Flask-Login 0.6.3, Flask-Session 0.8.0, cachelib 0.17.0, Flask-WTF 1.3.0, bcrypt 5.0.0, pydantic 2.14.0, email-validator 2.3.0, react-router 8.4.0 y @testing-library/user-event 14.6.7.

## Problemas encontrados y cómo se resolvieron

Ver la tabla de la [entrada de avance](2026-10-11-funcionalidad-002-avance.md). Los principales: un contexto de Flask compartido entre solicitudes en las pruebas, el error 500 de bcrypt con contraseñas largas, dos carreras de redirección en el frontend, una plantilla de correo con el contenido de otra y archivos creados con nombres o ubicaciones distintos. Todos quedaron corregidos y cubiertos por pruebas o por verificaciones en las tareas.

## Pendientes

- Validar con los tutores el texto definitivo de los Términos de Uso y de la Política de Privacidad (pregunta abierta de la especificación).
- Registrar en la auditoría las acciones de cuenta (funcionalidad 003).
- Pasar el envío de correos a la cola de tareas (007) y a Amazon SES (017).
- Siguiente funcionalidad según la [hoja de ruta](../guias/hoja-de-ruta.md): **003, Auditoría**.
