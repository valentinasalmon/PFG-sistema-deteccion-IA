# Especificación: 030 — Revisión y refuerzo de la seguridad

- **Rama**: `funcionalidad/030-seguridad`
- **Estado**: Implementada (se activa en el próximo despliegue)
- **Requisitos que realiza**: RNF01 (CA7), RNF02 (CA4, CA5), RNF20
- **Reglas de negocio aplicadas**: —
- **Casos de uso**: transversal

## Problema

La plataforma maneja evidencia de casos judiciales y de siniestros, y ahora tiene páginas sin sesión: la verificación de informes, la carga desde el celular y el inicio con Google. Hasta esta funcionalidad:
- nada frenaba a quien probara contraseñas o códigos en masa, salvo el bloqueo de una cuenta concreta;
- las dependencias no se revisaban de forma automática.

## Alcance

### Incluido
- Límites de pedidos por IP en Nginx, con respuesta 429 en JSON:
  - acceso;
  - Google;
  - páginas públicas;
  - el resto de la API.
- Cabeceras nuevas: `Permissions-Policy` y `Cross-Origin-Opener-Policy`.
- Revisión de dependencias (`pip-audit` y `npm audit`) en cada Pull Request y cada semana, como condición para desplegar.
- Validación de la configuración de Nginx en la integración continua.
- Actualización de las dependencias de desarrollo con avisos (vitest, undici, zod).
- WeasyPrint solo incrusta recursos `data:` (defensa en profundidad contra SSRF).
- Revisión de seguridad documentada según OWASP Top 10 (2021): [docs/arquitectura/seguridad.md](../../arquitectura/seguridad.md).

### Excluido
- Doble factor de autenticación (trabajo futuro; con Google, lo aporta la cuenta de Google).
- Firewall de aplicaciones (AWS WAF): tiene costo mensual y no se justifica con este volumen.
- Prueba de penetración externa.

## Criterios de aceptación

- [x] **CA1**: Más de 20 envíos por minuto desde una IP (con 10 de ráfaga) a inicio de sesión, registro, verificación o recuperación reciben 429 con el mensaje "Hiciste demasiados intentos seguidos…". Las consultas `GET /api/sesion` no cuentan.
- [x] **CA2**: Los límites no afectan el uso normal:
  - se pueden cargar 30 fotos seguidas desde el celular;
  - la interfaz no recibe 429 al navegar.
- [x] **CA3**: Las respuestas, incluidas las 429, llevan `Permissions-Policy` (cámara solo para la propia plataforma; sin micrófono, ubicación, pagos ni USB) y `Cross-Origin-Opener-Policy: same-origin`.
- [x] **CA4**: La integración continua falla si hay una vulnerabilidad conocida en las dependencias de producción del backend, o una alta o crítica en las del frontend. El despliegue depende de esa verificación.
- [x] **CA5**: La integración continua valida con `nginx -t` las dos configuraciones del sitio.
- [x] **CA6**: Un PDF no descarga recursos de red ni archivos locales.
- [x] **CA7**: La interfaz muestra el mensaje del 429 como cualquier otro error.

## Preguntas abiertas

- Ninguna.
