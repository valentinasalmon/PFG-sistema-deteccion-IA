# Guía de despliegue en AWS

Pasos para publicar la plataforma en la cuenta de AWS de la autora, con los créditos gratuitos (funcionalidad 017, [ADR-0016](../arquitectura/decisiones/0016-despliegue-con-terraform-y-systems-manager.md)). Los comandos se ejecutan en la terminal de Ubuntu (WSL), desde la raíz del repositorio.

> **Nunca compartas ni subas** las claves de acceso de AWS, el archivo `terraform.tfvars`, el archivo `backend.hcl` ni el estado de Terraform. El asistente no necesita ninguna credencial: solo los resultados de los comandos y los mensajes de error, si aparecen.

## Qué se crea y cuánto cuesta

| Recurso | Para qué | Costo aproximado por mes |
|---|---|---|
| EC2 `t3.small` (2 GB) con disco de 30 GB | Nginx, API, trabajador de análisis, PostgreSQL y Redis | USD 18 |
| IP fija (Elastic IP) | Dirección estable del servidor | USD 3,60 |
| Buckets S3 (`imagenes`, `operacion` y el del estado) | Imágenes, informes, respaldos y artefactos | Centavos |
| SES, Parameter Store, Systems Manager y presupuesto | Correos, configuración, despliegue y alertas | Gratis con este uso |

Son unos **USD 22 por mes**, que salen de los créditos. El presupuesto creado por Terraform avisa por correo al pasar el 50 % y el 80 % de USD 30, y cuando AWS proyecta superarlo.

## Paso 1. Crear la cuenta de AWS (una sola vez)

1. Entrá a <https://aws.amazon.com/free> y creá la cuenta. Elegí el **plan gratuito (Free plan)**, que incluye créditos.
2. Activá la **verificación en dos pasos (MFA)** del usuario raíz: menú de la cuenta, *Security credentials*, *Assign MFA device*.
3. Creá un usuario para trabajar, así no usás el raíz:
   1. Andá a *IAM*, *Users* y *Create user*. Llamalo `terraform-autora`.
   2. Asignale el permiso **AdministratorAccess**.
   3. En el usuario, abrí *Security credentials* y *Create access key*. Elegí el caso *Command Line Interface (CLI)*.
   4. Copiá la *Access key* y la *Secret access key*. Se muestran **una sola vez**.
4. Si en algún paso AWS dice que un servicio no está disponible en el plan gratuito, pasá la cuenta al plan pago (*Billing*, *Upgrade plan*). Los créditos se siguen usando igual.

## Paso 2. Instalar las herramientas en WSL (una sola vez)

```bash
# AWS CLI
curl -sSo /tmp/awscli.zip https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip
unzip -q /tmp/awscli.zip -d /tmp && sudo /tmp/aws/install

# Terraform (repositorio oficial de HashiCorp)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y terraform

# Credenciales del usuario terraform-autora; región eu-west-1, formato json
aws configure
aws sts get-caller-identity   # debe mostrar tu número de cuenta
```

## Atajo: un solo comando para los pasos 3 y 4

Con las herramientas instaladas y `aws configure` hecho, este script hace los pasos 3 y 4 desde cualquier carpeta. Verifica las credenciales, crea el bucket del estado si falta, arma `backend.hcl` y controla `terraform.tfvars`. Si falta algo, explica qué hacer.

```bash
cd ~/PFG-sistema-deteccion-IA
git checkout funcionalidad/017-infraestructura-aws && git pull
bash infraestructura/scripts/crear_infraestructura_aws.sh
```

## Paso 3. Crear el bucket del estado de Terraform (una sola vez)

```bash
cd infraestructura/terraform/estado
terraform init
terraform apply          # revisá el plan y escribí "yes"
terraform output bucket_estado
```

## Paso 4. Crear la infraestructura

```bash
cd ../principal
cp backend.hcl.ejemplo backend.hcl
# editá backend.hcl y poné el nombre que mostró "terraform output bucket_estado"
cp terraform.tfvars.ejemplo terraform.tfvars
# editá terraform.tfvars con tu correo y los de los tutores

terraform init -backend-config=backend.hcl
terraform plan           # muestra lo que se va a crear (unas 60 piezas)
terraform apply          # escribí "yes"; tarda unos 5 minutos
terraform output
```

Guardá la salida: tiene la dirección de la plataforma (`url`) y las variables para GitHub.

## Paso 5. Verificar los correos en SES

Cada dirección de `correo_remitente` y `correos_verificados` recibe un correo de *Amazon Web Services – Email Address Verification Request*. Hay que abrir el enlace en cada uno: los tutores también tienen que hacerlo.

- Mientras SES está en modo de prueba, la plataforma **solo envía correos a esas direcciones**.
- Para registrar a otra persona en la demo, agregá su correo a `correos_verificados`, ejecutá `terraform apply` y pedile que confirme el enlace.

> **Correos en Spam:** mientras se use un Gmail como remitente sin dominio propio, Gmail suele mandar los correos de la plataforma a **Spam**. Marcalos como "No es spam" y avisales a los tutores. Con el dominio propio y su verificación en SES (con DKIM), los correos llegan a la bandeja de entrada.

## Paso 6. Cargar las variables en GitHub

En el repositorio, entrá a *Settings*, *Secrets and variables*, *Actions* y la pestaña **Variables** (no *Secrets*). Creá estas cuatro con los valores de `terraform output variables_github`:

| Variable | Ejemplo |
|---|---|
| `AWS_REGION` | `eu-west-1` |
| `AWS_ROLE_DESPLIEGUE` | `arn:aws:iam::123456789012:role/deteccion-imagenes-despliegue` |
| `BUCKET_OPERACION` | `deteccion-imagenes-operacion-a1b2c3` |
| `ID_INSTANCIA` | `i-0123456789abcdef0` |

No son secretos: el rol solo se puede usar desde la rama `main` de este repositorio. Mientras `ID_INSTANCIA` no exista, el despliegue se omite sin fallar.

## Paso 7. Esperar la preparación del servidor

Después del `apply`, la EC2 se prepara sola en unos 10 minutos: instala los paquetes, crea la base y pide el certificado HTTPS. Para ver el avance:

1. En la consola, andá a *EC2*, *Instances*, elegí `deteccion-imagenes-servidor` y tocá *Connect*.
2. Elegí la pestaña *Session Manager* y tocá *Connect*.
3. En la terminal que se abre, escribí:

```bash
sudo tail -f /var/log/plataforma-inicio.log
```

Termina con `Listo. La aplicación se instala con el primer despliegue`.

Si dice `AVISO: no se pudo obtener el certificado`, ejecutá `sudo bash /opt/plataforma/servidor/scripts/pedir_certificado.sh` en esa misma terminal y pasame el mensaje.

## Paso 8. Primer despliegue

El despliegue corre solo con cada envío a `main` que pasa la integración continua. El primero coincide con el **hito v0.1**:
1. Abrí el Pull Request de `desarrollo` hacia `main` e integralo.
2. En la pestaña *Actions* vas a ver el trabajo **Despliegue en AWS**, que tarda unos 5 minutos la primera vez.
3. Si falla, copiame el registro del paso *Desplegar en la EC2 con Systems Manager*. Una versión que no responde no reemplaza a la anterior.

Para repetir un despliegue sin cambios: en *Actions*, abrí la última ejecución sobre `main` y usá *Re-run all jobs*.

## Paso 9. Probar la plataforma

1. Abrí la `url` de la salida, por ejemplo `https://3-250-10-20.sslip.io`.
2. Registrate con un correo verificado en SES y confirmá el correo.
3. Iniciá sesión. Tu correo figura en `administradores`, así que tenés el rol de Administrador.

## Cuando compres el dominio

1. En `terraform.tfvars`, poné `dominio = "tu-dominio.com.ar"` y ejecutá `terraform apply`.
2. En el proveedor del dominio (por ejemplo, NIC Argentina), creá un registro **A** que apunte a la `ip_publica`.
3. Esperá a que el dominio resuelva. Lo comprobás con `nslookup tu-dominio.com.ar`.
4. En la terminal de Session Manager, ejecutá:

```bash
sudo bash /opt/plataforma/servidor/scripts/generar_entorno.sh
sudo bash /opt/plataforma/servidor/scripts/pedir_certificado.sh
sudo systemctl restart plataforma-web plataforma-trabajador
```

5. Opcional: para que cualquier persona reciba correos, verificá el dominio en SES y pedí la salida del modo de prueba (*SES*, *Account dashboard*, *Request production access*). AWS responde en alrededor de un día.

## Operación

| Tarea | Comando, en Session Manager |
|---|---|
| Ver los registros de la API | `sudo journalctl -u plataforma-web -f` |
| Ver los registros de los análisis | `sudo journalctl -u plataforma-trabajador -f` |
| Hacer un respaldo ahora | `sudo systemctl start plataforma-respaldo` |
| Restaurar un respaldo | `sudo bash /opt/plataforma/servidor/scripts/restaurar_respaldo.sh plataforma-AAAA-MM-DDTHHMMSSZ.dump` |
| Ver las versiones desplegadas | `ls -lt /opt/plataforma/versiones` |

Los respaldos se hacen todos los días a las 03:30 de Argentina y se borran a los 30 días.

## Al terminar el proyecto

Para no gastar créditos:
1. Vaciá los buckets `imagenes` y `operacion` desde la consola de S3.
2. Ejecutá `terraform destroy` en `principal`.
3. Ejecutá `terraform destroy` en `estado` (antes vaciá también su bucket).
4. Borrá la clave de acceso del usuario `terraform-autora`.
