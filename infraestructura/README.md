# Infraestructura

Infraestructura como código y configuración de operación para AWS, región Irlanda (`eu-west-1`): instancia EC2 con Nginx, Gunicorn, PostgreSQL y Redis; bucket S3 privado y cifrado; Amazon SES para correo.

- `terraform/`: recursos de AWS. Se rehace desde cero (el Terraform del repositorio anterior usaba RDS; ver [ADR-0005](../docs/arquitectura/decisiones/0005-postgresql-en-ec2.md)).
- `nginx/`, `systemd/`, `scripts/`: configuración del servidor, servicios y respaldos.

> Se completa en la funcionalidad 017.
