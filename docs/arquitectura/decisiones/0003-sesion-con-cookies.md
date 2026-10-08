# ADR-0003: Autenticación con sesión en cookie en lugar de JWT

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RF03, RF04, RNF01, RNF02

## Contexto

Con una interfaz React es habitual autenticar con tokens JWT. La propuesta del proyecto especifica Flask-Login.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| JWT en almacenamiento del navegador | Sin estado en el servidor | Expuesto a robo por XSS; revocar un token antes de su vencimiento es complejo |
| **Sesión de Flask-Login en cookie `HttpOnly`** | La cookie no es accesible desde JavaScript; cerrar sesión la invalida de inmediato; respeta la propuesta original | Requiere protección CSRF |

## Decisión

Flask-Login con cookie de sesión `Secure`, `HttpOnly` y `SameSite=Strict`, más un token CSRF en cada solicitud que modifica datos.

## Consecuencias

- RF04 (cerrar sesión) y RF05 CA3 (cerrar todas las sesiones) son simples de cumplir.
- El frontend debe enviar el token CSRF en una cabecera.
