# Revisión de seguridad (OWASP Top 10, 2021)

Revisión hecha el 2026-10-28, en la funcionalidad 030, sobre el código de `desarrollo` (incluida la 027) y la infraestructura de AWS. Para cada riesgo del OWASP Top 10 se indican las medidas con su evidencia y lo que queda pendiente.

## Resumen

| Riesgo | Estado | Medidas principales |
|---|---|---|
| A01 Control de acceso | Cubierto | Permisos por caso y por rol en los servicios; enlaces firmados de 5 minutos; token de carga de 192 bits del que solo se guarda la huella |
| A02 Fallas criptográficas | Cubierto | TLS 1.2+, HSTS, bcrypt con costo 12, cifrado en S3, EBS y SSM |
| A03 Inyección | Cubierto | ORM y consultas parametrizadas, validación con pydantic, escape automático en Jinja y React, ExifTool sin intérprete de comandos |
| A04 Diseño inseguro | Cubierto | Respuestas que no revelan qué cuentas existen, bloqueo por intentos, límites de pedidos, especificaciones y ADR |
| A05 Configuración insegura | Cubierto | Cabeceras (CSP y otras), `server_tokens off`, sin modo de depuración en producción, IMDSv2, solo puertos 80 y 443, sin SSH |
| A06 Componentes vulnerables | Cubierto desde la 030 | `pip-audit` y `npm audit` en cada Pull Request y cada semana, versiones fijas |
| A07 Fallas de autenticación | Cubierto | Política de contraseñas, bloqueo, vencimiento de sesión, regeneración del identificador, OIDC con PKCE |
| A08 Integridad del software y los datos | Cubierto | Despliegue solo con la integración continua en verde, credenciales temporales por OIDC, huellas en Hedera |
| A09 Registro y monitoreo | Cubierto | Auditoría en la misma transacción, con IP y motivo; alertas por correo |
| A10 SSRF | Cubierto | No se descargan direcciones que elija la persona usuaria; WeasyPrint solo acepta `data:` |

## Detalle por riesgo

### A01 — Control de acceso
- **Permisos por caso**: el servicio de casos decide quién ve, edita o comparte un caso según su rol y la organización (RF23 a RF33). Las rutas no consultan la base de datos directamente; import-linter lo verifica en cada Pull Request (ADR-0006).
- **Rol de Administrador**: solo se otorga desde la configuración del servidor (`ADMINISTRADORES`), nunca desde la interfaz.
- **Archivos**: las imágenes y los PDF se entregan con enlaces firmados de S3 que vencen a los 5 minutos (RF35 CA2). El bucket bloquea todo acceso público.
- **Carga desde el celular (024)**: el token es de un solo caso, vence en 15 minutos y tiene 192 bits. Solo se guarda su SHA-256.
- **Verificación pública (026)**: muestra la huella, la fecha y la versión, nunca datos del caso.

### A02 — Fallas criptográficas
- TLS 1.2 y 1.3, redirección desde HTTP y HSTS de un año (RNF02 CA1).
- Contraseñas con bcrypt de costo 12 (RNF01 CA1).
- S3 con cifrado AES-256, disco de la EC2 cifrado.
- Secretos en SSM como `SecureString`: clave de Flask, base de datos, correo, clave de Hedera y secreto de Google.
- Enlaces de correo firmados con itsdangerous, con vencimiento y de un solo uso (RNF01 CA5).

### A03 — Inyección
- SQLAlchemy con consultas parametrizadas: no hay SQL armado con texto.
- Toda entrada pasa por esquemas de pydantic que rechazan campos desconocidos (`extra="forbid"`).
- Escape automático en las plantillas de correos y PDF (`select_autoescape`) y en React. No se usa `dangerouslySetInnerHTML`.
- ExifTool recibe la imagen por la entrada estándar, con una lista de argumentos y sin intérprete de comandos.

### A04 — Diseño inseguro
- El registro, la recuperación y el reenvío responden igual exista o no la cuenta (RF01 CA3, RF05 CA2).
- Bloqueo de la cuenta tras 5 contraseñas incorrectas durante 15 minutos (RNF01 CA3), y límites de pedidos por IP en Nginx (030).
- Contra el secuestro previo de cuentas: al vincular Google, una cuenta sin verificar pierde su contraseña (ADR-0019).
- Desarrollo guiado por especificaciones, con criterios de aceptación probados y decisiones registradas en ADR.

### A05 — Configuración insegura
- Cabeceras:
  - `Content-Security-Policy` sin scripts externos ni `unsafe-inline` en scripts;
  - `X-Frame-Options: DENY` y `frame-ancestors 'none'`;
  - `X-Content-Type-Options`;
  - `Referrer-Policy`;
  - `Permissions-Policy` y `Cross-Origin-Opener-Policy` (030).
- `server_tokens off`. En producción, el modo de depuración está apagado y faltar una variable obligatoria impide arrancar.
- EC2:
  - grupo de seguridad con solo 80 y 443;
  - sin SSH (administración por Systems Manager);
  - metadatos de instancia solo con IMDSv2 (`http_tokens = "required"`).
- La integración continua valida la configuración de Nginx (`nginx -t`) y de Terraform.

### A06 — Componentes vulnerables
- Versiones fijas en `requirements.txt` y `package-lock.json`.
- `pip-audit` y `npm audit --omit=dev --audit-level=high` en cada Pull Request y cada lunes. El despliegue depende de ese control (030).
- Resultado del 2026-10-28: sin vulnerabilidades en producción. En las dependencias de desarrollo se corrigieron vitest, undici y zod.

### A07 — Fallas de autenticación
- Política de contraseñas: 10 caracteres o más, letras y números, y fuera de la lista de contraseñas comunes (RNF01 CA2).
- Sesión en Redis: vence a los 30 minutos de inactividad y a las 8 horas de iniciada, y el identificador se regenera al iniciar sesión.
- Cookie `HttpOnly`, `Secure` y `SameSite=Lax`, con token CSRF en toda solicitud que modifica datos (ADR-0003, ADR-0019).
- Inicio con Google por OpenID Connect con `state`, `nonce` y PKCE; solo con correo verificado por Google (027).

### A08 — Integridad del software y los datos
- Solo se despliega lo que pasa la integración continua, con credenciales temporales de AWS por OIDC, sin claves guardadas en GitHub.
- Huella SHA-256 de cada imagen, informe y versión desplegada, sellada en Hedera (023, 026, 029).
- Ganchos de pre-commit, entre ellos `detect-private-key`.
- Búsqueda de secretos en todo el historial con detect-secrets (2026-10-28):
  - solo aparecieron credenciales de ejemplo del entorno local y listas públicas de C2PA;
  - nunca se subieron `.env`, `terraform.tfvars`, estado de Terraform ni modelos.

### A09 — Registro y monitoreo
- Tabla de auditoría escrita en la misma transacción que el cambio (ADR-0011). Registra la IP real (detrás de Nginx) y el motivo de cada rechazo, incluidos los inicios fallidos con Google.
- Alertas por correo y presupuesto de AWS con aviso.

### A10 — SSRF
- El backend solo se conecta a direcciones fijas de la configuración:
  - S3;
  - el *mirror node* de Hedera;
  - el *token endpoint* de Google;
  - SES.
- WeasyPrint no descarga recursos: solo `data:` (030). Así no puede pedir, por ejemplo, el servicio de metadatos de la EC2.

## Riesgos que quedan (aceptados o para trabajo futuro)

| Riesgo | Por qué se acepta | Mitigación futura |
|---|---|---|
| Sin doble factor con contraseña | Alcance del proyecto | TOTP; con Google, lo aporta la cuenta de Google |
| `style-src 'unsafe-inline'` en la CSP | Lo necesitan los estilos en línea de React | *Nonces* o quitar los estilos en línea |
| Límite por IP en oficinas con una sola IP pública | Los límites son amplios (20 accesos por minuto) | Límite por cuenta además de por IP |
| Sin firewall de aplicaciones (WAF) | Costo mensual frente a un volumen bajo | AWS WAF con reglas administradas |
| Un solo servidor | Costo; hay respaldos diarios | Alta disponibilidad |
| HSTS sin `preload` ni `includeSubDomains` | El dominio provisorio es `sslip.io` | Activarlo con el dominio propio |
