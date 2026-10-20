# ADR-0016: Despliegue con Terraform, Systems Manager y OIDC

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Requisitos relacionados**: RNF02, RNF03, RNF15, RNF20 (CA4), RNF22 (CA3); CP-06, CP-16

## Contexto

La plataforma se publica en la cuenta de AWS de la autora, con los créditos gratuitos y una sola EC2 en Irlanda (ADR-0005, RNF08 CA6). La entrega es en menos de un mes. La infraestructura tiene que poder recrearse desde el repositorio, y cada integración en `main` se tiene que desplegar sola (CP-06).

Hay tres restricciones:
- **Ningún secreto en el repositorio** (RNF03 CA3).
- **El dominio se compra al final** (CP-16).
- **La sesión exige HTTPS** (RNF02 CA2).

## Alternativas evaluadas

| Tema | Alternativa | Ventajas | Desventajas |
|---|---|---|---|
| Infraestructura | **Terraform** | Reproducible y revisable en Pull Requests; es el pedido de la autora | Requiere un bucket para el estado |
| | Consola de AWS | Rápido la primera vez | No se puede reproducir ni revisar |
| Acceso al servidor | **Systems Manager (SSM)** | Ningún puerto de administración abierto, sin claves SSH; deja registro de cada comando | Depende del agente de SSM, que la imagen de Ubuntu ya trae |
| | SSH con clave | Conocido | Puerto 22 abierto y una clave privada guardada en GitHub |
| Credenciales de GitHub Actions | **OIDC** con un rol limitado a la rama `main` | Credenciales temporales, nada guardado | Configuración inicial un poco más larga |
| | Claves de acceso de un usuario | Simple | Claves permanentes que pueden filtrarse |
| Código en el servidor | **Artefacto en S3** armado por GitHub Actions | La EC2 no necesita acceso al repositorio privado; la interfaz se compila en GitHub | Un bucket más (`operacion`) |
| | `git pull` en la EC2 | Simple | Requiere una credencial de GitHub en el servidor |
| Configuración | **Parameter Store**, con los secretos generados por Terraform | Cifrada, gratuita, sin secretos en el repositorio | Los secretos quedan en el estado de Terraform, que se guarda cifrado y privado |
| HTTPS sin dominio | **`<ip>.sslip.io`** con Let's Encrypt | Gratis; al comprar el dominio solo cambia una variable | Depende del servicio público sslip.io |

## Decisión

- Terraform en dos partes:
  - `infraestructura/terraform/estado`: el bucket del estado. Se aplica una sola vez.
  - `infraestructura/terraform/principal`:
    - red, EC2 con IP fija;
    - buckets `imagenes` y `operacion`;
    - SES, Parameter Store y presupuesto;
    - rol de la EC2 y rol de despliegue con OIDC.
- **La EC2 se prepara sola al crearse**, con `scripts/preparar_servidor.sh`:
  - instala PostgreSQL, Redis, Nginx, certbot y las bibliotecas de WeasyPrint y ExifTool;
  - crea la base de datos;
  - arma el `.env` desde Parameter Store;
  - pide el certificado.
- **Despliegue**:
  1. El trabajo `desplegar` de la integración continua corre después de las verificaciones, solo en `main`.
  2. Compila la interfaz y arma un artefacto.
  3. Lo sube a S3 con credenciales OIDC.
  4. Ejecuta `desplegar.sh` en la EC2 por Systems Manager.
- **`desplegar.sh`**:
  1. Instala la versión en una carpeta propia.
  2. Migra la base.
  3. Cambia el enlace `actual`.
  4. Verifica `/api/salud`. Si falla, vuelve a la versión anterior.
- Los respaldos diarios de PostgreSQL van a S3 y vencen a los 30 días (RNF15 CA2).

## Consecuencias

**Ventajas**
- La infraestructura completa se crea con dos `terraform apply`.
- Cada cambio integrado en `main` llega solo a producción, y una versión que no arranca no reemplaza a la anterior.
- No hay claves de AWS ni de SSH guardadas en el repositorio ni en GitHub.

**Lo que se resigna**
- Las migraciones de la base no se revierten automáticamente. Una migración destructiva requiere restaurar el respaldo (`restaurar_respaldo.sh`).
- Mientras no haya dominio propio, la dirección depende de sslip.io.
- Si Let's Encrypt no emite el certificado para esa dirección, no se puede iniciar sesión hasta tener el dominio.
- SES funciona en modo de prueba: solo se envían correos a direcciones verificadas.
