# Plan técnico: 017 — Infraestructura y despliegue en AWS

Referencias: [especificacion.md](especificacion.md) · [ADR-0016](../../arquitectura/decisiones/0016-despliegue-con-terraform-y-systems-manager.md) · [guía de despliegue](../../guias/despliegue-aws.md)

## Resumen de la solución

```
GitHub Actions (main) ──OIDC──▶ rol de despliegue ──▶ S3 operacion/artefactos
        │                                               │
        └──── Systems Manager: desplegar.sh ───────────▶ EC2 t3.small (Irlanda)
                                                         ├─ Nginx :443 (Let's Encrypt)
                                                         │   ├─ /        interfaz compilada
                                                         │   └─ /api/    Gunicorn :8000
                                                         ├─ trabajador RQ
                                                         ├─ PostgreSQL y Redis (solo locales)
                                                         └─ respaldo diario ─▶ S3 operacion/respaldos
Navegador ◀── enlaces firmados (5 min) ── S3 imagenes (privado, cifrado, versionado)
```

## Archivos

| Ubicación | Contenido |
|---|---|
| `infraestructura/terraform/estado/` | Bucket del estado de Terraform; se aplica una sola vez |
| `infraestructura/terraform/principal/` | `versiones.tf`, `variables.tf`, `red.tf`, `almacenamiento.tf`, `correo.tf`, `parametros.tf`, `permisos.tf`, `servidor.tf`, `presupuesto.tf`, `salidas.tf`, `inicio.sh.tftpl` y los ejemplos `terraform.tfvars.ejemplo` y `backend.hcl.ejemplo` |
| `infraestructura/scripts/` | Ver la tabla de scripts más abajo |
| `infraestructura/nginx/` | `plataforma.conf` (HTTPS) y `plataforma-sin-tls.conf` (provisoria, para pedir el certificado) |
| `infraestructura/systemd/` | `plataforma-web` (Gunicorn), `plataforma-trabajador` (RQ), y `plataforma-respaldo` con su temporizador |
| `.github/workflows/integracion-continua.yml` | Trabajos `infraestructura` (fmt, validate, shellcheck) y `desplegar` |
| `docs/guias/despliegue-aws.md` | Guía paso a paso de la autora |

Scripts del servidor:

| Script | Qué hace |
|---|---|
| `preparar_servidor.sh` | Prepara la EC2 al crearse |
| `generar_entorno.sh` | Arma el `.env` desde Parameter Store |
| `instalar_configuracion.sh` | Instala la configuración de Nginx y systemd |
| `pedir_certificado.sh` | Pide el certificado a Let's Encrypt |
| `desplegar.sh` | Instala una versión nueva |
| `respaldar.sh` y `restaurar_respaldo.sh` | Hacen y restauran los respaldos de la base |

## Decisiones de diseño

- **Una sola EC2 `t3.small` con 2 GB de swap.**
  - Alcanza para 2 procesos de Gunicorn, el trabajador, PostgreSQL y Redis, con margen para la capa 4.
  - Cuesta unos USD 22 por mes, que salen de los créditos.
- **Default VPC**: sin NAT ni subredes propias, que costarían y no aportan para una sola instancia.
- **Sin SSH**: el grupo de seguridad solo abre los puertos 80 y 443. La administración usa Session Manager y el despliegue, Run Command.
- **IMDSv2 obligatorio**: una falla de SSRF en la aplicación no puede leer las credenciales del rol.
- **El dominio provisorio** `<ip>.sslip.io` se arma con la IP fija. Por eso la IP se crea antes que la EC2 y se asocia después.
- **Las versiones conviven en `/opt/plataforma/versiones/<commit>`**, y `actual` es un enlace a la que está en uso. Volver atrás es cambiar el enlace. Se conservan las tres más recientes.
- **La configuración del servidor viaja con cada versión**: Nginx, systemd y scripts se reinstalan desde el artefacto en cada despliegue. Así un cambio en ellos pasa por Pull Request y por la integración continua.
- **SES por SMTP** con un usuario técnico que solo puede enviar (`ses:SendRawEmail`). La aplicación ya envía por SMTP, así que no hubo que cambiar el código.

## Cambios en la aplicación

- `ProxyFix`, con `PROXIES_DE_CONFIANZA`:
  - vale 0 en desarrollo y 1 en producción;
  - toma la IP real del cliente para la auditoría y el esquema HTTPS, sin aceptar cabeceras agregadas por clientes.
- La región por defecto del bucket pasa a `eu-west-1`, la de la especificación (RNF08 CA6). Antes era `sa-east-1`.
- `gunicorn==23.0.0` en las dependencias de producción.

## Estrategia de verificación

- `terraform validate` y `terraform fmt` sobre los dos módulos, con el proveedor AWS 6.66. Corren en la integración continua.
- `shellcheck` de los scripts, en la integración continua.
- `nginx -t` de las dos configuraciones con un certificado de prueba.
- Gunicorn con la configuración de producción: carga `wsgi:aplicacion`, y `/api/salud` informa el estado de la base y de Redis.
- Pruebas del backend:
  - la configuración de producción usa un proxy y la región de Irlanda;
  - detrás del proxy, la IP y el esquema son los del cliente.
- Sin acceso a la cuenta de AWS desde el entorno del asistente, `terraform apply` y el primer despliegue los ejecuta la autora con la guía (CA9).

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Let's Encrypt no emite el certificado para `sslip.io` (límites de uso) | `pedir_certificado.sh` se puede repetir; con el dominio propio el problema desaparece |
| El plan gratuito de AWS no habilita algún servicio | Pasar la cuenta al plan pago; los créditos se siguen usando |
| La memoria no alcanza con la capa 4 | Swap de 2 GB y variable `tipo_instancia` para subir de tamaño sin perder datos |
| Una migración destructiva falla en producción | Respaldo diario y `restaurar_respaldo.sh`; antes de una migración riesgosa, `systemctl start plataforma-respaldo` |
