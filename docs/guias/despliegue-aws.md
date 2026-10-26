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

## Publicar cambios nuevos (por ejemplo, el rediseño 022)

La infraestructura ya está creada: para publicar alcanza con integrar en `main`.
1. Integrá los Pull Requests en orden hacia `desarrollo`: primero `funcionalidad/013-panel-y-notificaciones` y después `funcionalidad/022-rediseno-interfaz`, que sale de la 013.
2. Abrí el Pull Request de `desarrollo` hacia `main` e integralo. El trabajo **Despliegue en AWS** publica la versión sola, en unos 3 minutos.
3. La 022 cambia el remitente de los correos a «evidentIA». Se aplica una sola vez, después del despliegue del paso 2:

   **A. Actualizar el parámetro en AWS, desde tu WSL**

   ```bash
   cd ~/PFG-sistema-deteccion-IA
   git switch main && git pull
   cd infraestructura/terraform/principal
   terraform init -backend-config=backend.hcl   # solo si es otra computadora o se borró .terraform
   terraform plan    # tiene que decir: 1 to change (el parámetro REMITENTE_CORREO)
   terraform apply   # escribí "yes"
   ```

   Si `terraform plan` muestra algo que no sea ese parámetro, no apliques y pasame la salida.

   **B. Abrir la terminal del servidor (Session Manager)**

   1. Entrá a la consola de AWS, en la región **Irlanda (eu-west-1)**: el nombre arriba a la derecha.
   2. Buscá **EC2** → **Instances** → marcá `deteccion-imagenes-servidor` → botón **Connect**.
   3. Pestaña **Session Manager** → **Connect**. Se abre una terminal negra en el navegador.

   **C. Regenerar la configuración y reiniciar, en esa terminal**

   ```bash
   sudo bash /opt/plataforma/servidor/scripts/generar_entorno.sh
   sudo systemctl restart plataforma-web plataforma-trabajador
   sudo grep REMITENTE_CORREO /opt/plataforma/.env   # tiene que decir evidentIA <...>
   ```

   **D. Probar**: desde la plataforma, pedí «¿Olvidaste tu contraseña?» con tu correo. El correo llega con el remitente «evidentIA» y el diseño nuevo. Si no lo ves, revisá Spam.

   Para cerrar la terminal, escribí `exit` o tocá **Terminate**.

4. **Cuenta de prueba en el servidor**: no se crea en producción. Registrate normalmente; tu correo ya figura en `administradores`, así que al ingresar tenés el rol de Administrador.

## Activar el sello de tiempo en Hedera (funcionalidad 023)

La cuenta de Hedera se crea en https://portal.hedera.com con clave **ED25519**. El **Account ID** y el **Topic ID** no son secretos, pero no se suben al repositorio: van en `terraform.tfvars`. La **clave privada** no se escribe en ningún archivo: se pide sin mostrarla en pantalla y se guarda cifrada en SSM.

1. **Crear el tema (una sola vez por red)**, desde WSL, en la carpeta del backend con el entorno local activo (ver `levantar-en-local.md`):
   ```bash
   cd ~/PFG-sistema-deteccion-IA/backend && source .venv/bin/activate
   pip install -r requirements.txt
   flask --app wsgi sellos crear-tema --red testnet
   ```
   Pide el Account ID y la clave privada; esta última no se muestra mientras se escribe. Responde `Tema creado en testnet: 0.0.…`.
2. **Guardar la clave privada cifrada en SSM** (no queda en el historial de la terminal):
   ```bash
   read -rs CLAVE && aws ssm put-parameter --name /deteccion-imagenes/produccion/HEDERA_CLAVE \
     --type SecureString --value "$CLAVE" --overwrite --region eu-west-1 && unset CLAVE
   ```
   Se pega la clave, se aprieta Enter y no se ve nada: es normal. El prefijo `/deteccion-imagenes/produccion` es el de la variable `proyecto` de Terraform; si la cambiaste en `terraform.tfvars`, usá ese nombre.
3. **Completar `terraform.tfvars`**:
   ```hcl
   sello_tiempo  = "hedera"
   hedera_red    = "testnet"
   hedera_cuenta = "0.0.…"   # Account ID
   hedera_tema   = "0.0.…"   # Topic ID del paso 1
   ```
   Después: `terraform plan` (tiene que crear 3 parámetros y cambiar SELLO_TIEMPO) y `terraform apply`.
4. **Desplegar** (PR de `desarrollo` a `main`). El despliegue regenera el `.env` del servidor con los datos de Hedera.
5. **Probar**: cargar una imagen en un caso. En unos segundos (o en la próxima pasada del temporizador, cada 15 minutos) tiene que aparecer "Registrada en Hedera" con el enlace "Verificar en HashScan".

**Pasar a la red real (*mainnet*)**: crear una cuenta de *mainnet* con HBAR, repetir los pasos 1 a 3 con `--red mainnet` y la cuenta nueva, y desplegar. Los sellos de *testnet* no se migran (CP-26).

## Activar el inicio con Google (funcionalidad 027)

El cliente se crea con tu cuenta de Google en https://console.cloud.google.com. El **ID de cliente** no es secreto. El **secreto del cliente** sí lo es: no se escribe en ningún archivo ni se pega en el chat.

1. **Proyecto**: arriba a la izquierda, selector de proyectos, **Proyecto nuevo**, nombre `evidentIA`, **Crear**. Después, seleccionalo.
2. **Pantalla de consentimiento**: menú, **APIs y servicios**, **Pantalla de consentimiento de OAuth** (o **Google Auth Platform**), **Comenzar**. Completá:
   - **Nombre de la aplicación**: `evidentIA`.
   - **Correo de asistencia**: tu correo.
   - **Público**: **Externo**.
   - **Correo de contacto**: tu correo.

   Aceptá la política y tocá **Crear**. No subas logo por ahora: con logo, Google pide verificar la aplicación.
3. **Usuarios de prueba**: en **Público**, la aplicación queda **En prueba**. En **Usuarios de prueba**, agregá los correos que van a probar, incluido el tuyo. Admite hasta 100.
4. **Cliente**: en **Clientes**, **Crear cliente**, tipo **Aplicación web**, nombre `evidentIA web`. En **URIs de redireccionamiento autorizados** agregá:
   - `http://localhost:5173/api/google/retorno` (local);
   - `https://<ip-con-guiones>.sslip.io/api/google/retorno` (producción, con la misma dirección que abrís en el navegador).

   **Crear**. Google muestra el **ID de cliente** y el **secreto**: dejá la ventana abierta.
   Si Google rechaza la dirección `sslip.io`, probá solo en local hasta comprar el dominio (CP-30). Con el dominio, agregás `https://tu-dominio/api/google/retorno`.
5. **En local**: en `backend/.env` agregá `GOOGLE_ID_CLIENTE=...` y `GOOGLE_SECRETO_CLIENTE=...` y reiniciá `flask run`. El archivo `.env` no se sube.
   - Para comprobarlo: `curl -s http://localhost:5000/api/google/estado` tiene que responder `{"habilitado": true}`.
   - Si responde `false`, revisá que las dos claves tengan valor sin mostrarlas:
     ```bash
     python -c "from dotenv import dotenv_values; v=dotenv_values('.env'); print({k: len(v.get(k) or '') for k in ('GOOGLE_ID_CLIENTE','GOOGLE_SECRETO_CLIENTE')})"
     ```
     El ID tiene unos 72 caracteres y el secreto, unos 35.
   - Si las dos tienen valor y sigue en `false`, quedó abierto un backend viejo que arrancó antes de cargar las claves: el modo de depuración se reinicia cuando cambia el código, no cuando cambia el `.env`. Cerralo con `pkill -f "flask --app wsgi run"`, comprobá que `ss -ltnp | grep 5000` no muestre nada y volvé a arrancarlo.
6. **En producción**:
   - Guardá el secreto cifrado en SSM (pegalo y apretá Enter; no se ve nada):
     ```bash
     read -rs SECRETO && aws ssm put-parameter --name /deteccion-imagenes/produccion/GOOGLE_SECRETO_CLIENTE \
       --type SecureString --value "$SECRETO" --overwrite --region eu-west-1 && unset SECRETO
     ```
   - En `terraform.tfvars` agregá `google_id_cliente = "....apps.googleusercontent.com"`.
   - Ejecutá `terraform plan`, que crea 1 parámetro, y después `terraform apply`.
   - Desplegá (PR de `desarrollo` a `main`).
7. **Probar**:
   - En **Iniciar sesión** aparece **Continuar con Google**.
   - Con un correo sin cuenta, pide completar el rubro y entra.
   - La segunda vez entra directo.
   - Con tu correo de administradora, se vincula a tu cuenta existente.

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
