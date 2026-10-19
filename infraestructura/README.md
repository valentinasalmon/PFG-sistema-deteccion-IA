# Infraestructura

Infraestructura como código y configuración de operación para AWS, región Irlanda (`eu-west-1`): una EC2 con Nginx, Gunicorn, el trabajador de análisis, PostgreSQL y Redis; buckets S3 privados y cifrados; Amazon SES para el correo. Ver la [funcionalidad 017](../docs/funcionalidades/017-infraestructura-aws/plan.md) y el [ADR-0016](../docs/arquitectura/decisiones/0016-despliegue-con-terraform-y-systems-manager.md).

| Carpeta | Contenido |
|---|---|
| `terraform/estado/` | Bucket del estado de Terraform (se aplica una sola vez) |
| `terraform/principal/` | Todos los recursos de AWS |
| `scripts/` | Preparación del servidor, despliegue, certificado y respaldos (más el script del entorno de WSL) |
| `nginx/`, `systemd/` | Configuración del servidor web y de los servicios |

Paso a paso para la autora: [docs/guias/despliegue-aws.md](../docs/guias/despliegue-aws.md).
