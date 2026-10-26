# 2026-10-19 — Funcionalidad 017: infraestructura y despliegue en AWS (código)

## Qué se hizo

Queda lista toda la infraestructura como código para publicar la plataforma en la cuenta de AWS de la autora, con los créditos gratuitos (decisión del 2026-10-19). Falta que la autora la aplique siguiendo la [guía paso a paso](../guias/despliegue-aws.md).

Documentos: [especificación](../funcionalidades/017-infraestructura-aws/especificacion.md), [plan](../funcionalidades/017-infraestructura-aws/plan.md), [tareas](../funcionalidades/017-infraestructura-aws/tareas.md) y [ADR-0016](../arquitectura/decisiones/0016-despliegue-con-terraform-y-systems-manager.md).

- **Terraform**, en la región de Irlanda:
  - un bucket para el estado;
  - una EC2 `t3.small` con IP fija y disco cifrado;
  - buckets S3 privados, cifrados y versionados para las imágenes y la operación, con respaldos que vencen a los 30 días;
  - SES;
  - Parameter Store, con los secretos generados por Terraform;
  - roles de mínimo privilegio;
  - un presupuesto con alertas.
- **El servidor se prepara solo al crearse**:
  - instala PostgreSQL, Redis, Nginx, certbot y las bibliotecas de WeasyPrint y ExifTool;
  - crea la base de datos;
  - arma el `.env` desde Parameter Store;
  - pide el certificado HTTPS para `<ip>.sslip.io` hasta que se compre el dominio.
- **Despliegue automático**: cada envío a `main` que pasa la integración continua se despliega en la EC2.
  1. Se compila la interfaz y se sube un artefacto a S3, con credenciales OIDC sin claves guardadas.
  2. Systems Manager ejecuta `desplegar.sh`.
  3. El script migra la base, cambia de versión y verifica la salud. Si la versión nueva no responde, vuelve a la anterior.
- **Integración continua**: trabajo nuevo que verifica el formato y la validez del Terraform y los scripts del servidor.
- **Aplicación**:
  - `ProxyFix`, para registrar en la auditoría la IP real detrás de Nginx;
  - la región por defecto pasa a Irlanda;
  - se agrega Gunicorn.

## Verificación

- `terraform validate` y `terraform fmt`: correctos en los dos módulos, con el proveedor AWS 6.66.
- `shellcheck`: sin advertencias en los scripts.
- `nginx -t`: correcto en las dos configuraciones, con un certificado de prueba.
- Gunicorn levanta la aplicación con la configuración de producción.
- Backend: 389 pruebas, más 2 que solo corren con las imágenes del TIF; cobertura del 99 %, pylint 10/10 y contratos de capas cumplidos.
- No se pudo ejecutar `terraform apply`: el entorno del asistente no tiene acceso a la cuenta de AWS, y es la autora quien la usa. Queda como CA9.

## Decisiones tomadas por el asistente

- **Systems Manager en lugar de SSH**: ningún puerto de administración abierto y ninguna clave privada que guardar.
- **OIDC para GitHub Actions**: el rol de despliegue solo se puede asumir desde la rama `main` de este repositorio.
- **Artefacto en S3 en lugar de `git pull`**: el servidor no necesita acceso al repositorio privado.
- **`sslip.io` hasta tener dominio**: permite HTTPS desde el primer día. La sesión lo exige (RNF02 CA2).
- **El despliegue se omite mientras no estén las variables de AWS en GitHub**, así la integración continua no falla antes de crear la infraestructura.
- **`t3.small` con swap de 2 GB**: alcanza para todo el sistema en una sola máquina y cuesta unos USD 22 por mes. El presupuesto avisa al pasar el 50 % y el 80 % de USD 30.

## Pendientes

- **Autora**:
  - Pasos 1 a 7 de la guía: cuenta, herramientas, `terraform apply`, verificación de los correos en SES y variables de GitHub.
  - Integrar `desarrollo` en `main` (hito v0.1), que dispara el primer despliegue.
- **Asistente y autora**: revisar el primer despliegue y probar la restauración de un respaldo (RNF15 CA3).
- **Al final**: dominio propio.

## Puesta en marcha (2026-10-20)

La autora aplicó la infraestructura en su cuenta. Problemas encontrados y resueltos:

| Problema | Solución |
|---|---|
| El usuario de Terraform no tenía permisos | Se le asignó `AdministratorAccess` |
| La búsqueda de la imagen de Ubuntu por nombre no devolvía resultados | Se toma del parámetro público de Canonical en Systems Manager |
| EC2 rechazó el apóstrofo en la descripción de las reglas de seguridad | Descripciones sin ese carácter |
| Cuatro mensajes de commit pasaban los 100 caracteres | Se acortaron y se rehízo el historial de la rama |
| GitHub no podía asumir el rol de despliegue (`AssumeRoleWithWebIdentity`) | Un flujo temporal de diagnóstico mostró que GitHub identifica al repositorio con los números de la cuenta y del repositorio (`repo:valentinasalmon@141863784/PFG-sistema-deteccion-IA@1410365187:...`). El rol acepta ese formato y el anterior, siempre solo desde `main` |

Se agregó `crear_infraestructura_aws.sh`, que aplica todo con un solo comando y explica qué falta si algo no está listo.

Con el rol corregido, el despliegue automático instaló la versión de `main` y la plataforma responde en `https://18-200-199-40.sslip.io` (CA9).
