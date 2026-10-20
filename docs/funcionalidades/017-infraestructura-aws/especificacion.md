# Especificación: 017 — Infraestructura y despliegue en AWS

- **Rama**: `funcionalidad/017-infraestructura-aws`
- **Estado**: En curso. El código está terminado; falta que la autora aplique la infraestructura en su cuenta (ver la [guía](../../guias/despliegue-aws.md))
- **Requisitos que realiza**: RNF02 (CA1, CA2, CA4), RNF03 (CA1 a CA4), RNF15 (CA2, CA3), RNF20 (CA4), RNF22 (CA3); RNF08 CA6 (región de Irlanda)
- **Decisiones**: CP-06 y CP-16 (2026-10-19), [ADR-0005](../../arquitectura/decisiones/0005-postgresql-en-ec2.md), [ADR-0016](../../arquitectura/decisiones/0016-despliegue-con-terraform-y-systems-manager.md)

## Problema

La plataforma solo corre en la computadora de desarrollo. Para la entrega tiene que estar publicada:
- con HTTPS;
- con los datos en un bucket privado y cifrado;
- con respaldos;
- con despliegue automático.

Todo, en la cuenta de AWS de la autora y con los créditos gratuitos.

## Alcance

### Incluido

- **Infraestructura como código** con Terraform, en la región de Irlanda:
  - una EC2 con IP fija que corre Nginx, Gunicorn, el trabajador de análisis, PostgreSQL y Redis;
  - buckets S3 privados, cifrados y versionados;
  - Amazon SES;
  - la configuración y los secretos en Parameter Store;
  - un presupuesto con alertas de costo.
- **Preparación automática** del servidor al crearse.
- **HTTPS** con Let's Encrypt:
  - usa la dirección provisoria `<ip>.sslip.io` hasta que se compre el dominio;
  - redirige de HTTP a HTTPS;
  - envía las cabeceras HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy` y `X-Frame-Options`.
- **Despliegue automático** en cada integración en `main` que pase las verificaciones, sin claves guardadas en GitHub. Vuelve a la versión anterior si la nueva no responde.
- **IP real del cliente** en la auditoría detrás de Nginx, sin aceptar cabeceras falsificadas.
- **Respaldo diario** de la base en S3, que vence a los 30 días, y un procedimiento de restauración.
- **Guía paso a paso** para la autora.

### Excluido

- **Dominio propio**: se compra al final. La guía explica cómo cambiarlo.
- **Salida del modo de prueba de SES**: es opcional y requiere el dominio.
- **Alta disponibilidad** con varias instancias o balanceador: no corresponde al alcance (RNF15 CA1, 99 %).
- **Capa 4**: el modelo ONNX se copiará al servidor cuando la autora termine la funcionalidad 010.

## Criterios de aceptación

- [x] **CA1**: `terraform validate` y `terraform fmt` pasan en los dos módulos, y la integración continua los verifica, junto con los scripts del servidor (shellcheck).
- [x] **CA2**: El bucket de imágenes es privado, tiene bloqueado el acceso público, cifrado y versionado (RNF03 CA1).
- [x] **CA3**: Los permisos son mínimos (RNF03 CA4):
  - la EC2 solo accede a sus buckets y a sus parámetros;
  - el rol de despliegue solo sube artefactos y ejecuta comandos en esa EC2;
  - el rol de despliegue solo se puede asumir desde la rama `main` del repositorio, identificado por nombre y por número.
- [x] **CA4**: Ningún secreto está en el repositorio: se generan en Terraform y se leen de Parameter Store (RNF03 CA3).
- [x] **CA5**: Nginx sirve la interfaz y la API con TLS 1.2 o superior, redirige de HTTP a HTTPS y envía las cabeceras de seguridad (RNF02 CA1, CA4). Se verificó con `nginx -t`.
- [x] **CA6**: Detrás de Nginx, la auditoría registra la IP real del cliente y la cookie de sesión se marca `Secure` (RNF02 CA2, RNF06 CA2).
- [x] **CA7**: Cada envío a `main` que pasa las verificaciones se despliega solo; si la versión nueva no responde, se restablece la anterior (RNF20 CA4).
- [x] **CA8**: La base se respalda todos los días en S3, los respaldos vencen a los 30 días y la restauración está documentada (RNF15 CA2, CA3).
- [ ] **CA9**: La autora aplica la infraestructura y la plataforma responde por HTTPS en la dirección publicada (pendiente de la autora).
- [ ] **CA10**: Se prueba la restauración de un respaldo antes de la entrega (RNF15 CA3).
