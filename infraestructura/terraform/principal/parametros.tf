# Configuración de la aplicación en Parameter Store (/<proyecto>/produccion/).
# La EC2 la lee al arrancar y en cada despliegue y arma su archivo .env
# (scripts/generar_entorno.sh). Los secretos se generan acá y van cifrados.
# Excepción: la clave privada de Hedera (HEDERA_CLAVE) la carga la autora a mano
# como SecureString, para que no quede en el estado de Terraform.

resource "random_password" "clave_secreta" {
  length  = 64
  special = false
}

resource "random_password" "base_de_datos" {
  length  = 32
  special = false
}

locals {
  prefijo_parametros = "/${var.proyecto}/produccion"
  dominio            = var.dominio != "" ? var.dominio : "${replace(aws_eip.servidor.public_ip, ".", "-")}.sslip.io"

  parametros_secretos = {
    CLAVE_SECRETA      = random_password.clave_secreta.result
    CONTRASENIA_BD     = random_password.base_de_datos.result
    USUARIO_CORREO     = aws_iam_access_key.smtp.id
    CONTRASENIA_CORREO = aws_iam_access_key.smtp.ses_smtp_password_v4
  }
  parametros = {
    DOMINIO          = local.dominio
    CORREO_ALERTAS   = var.correo_alertas
    REMITENTE_CORREO = "evidentIA <${var.correo_remitente}>"
    ADMINISTRADORES  = join(",", var.administradores)
    SERVIDOR_CORREO  = "email-smtp.${var.region}.amazonaws.com"
    S3_BUCKET        = aws_s3_bucket.bucket["imagenes"].bucket
    S3_REGION        = var.region
    BUCKET_OPERACION = aws_s3_bucket.bucket["operacion"].bucket
    SELLO_TIEMPO     = var.sello_tiempo
  }
  # SSM no admite valores vacíos: los datos de Hedera se crean solo cuando están completos.
  parametros_hedera = var.hedera_cuenta != "" && var.hedera_tema != "" ? {
    HEDERA_RED    = var.hedera_red
    HEDERA_CUENTA = var.hedera_cuenta
    HEDERA_TEMA   = var.hedera_tema
  } : {}
}

resource "aws_ssm_parameter" "secreto" {
  for_each = nonsensitive(toset(keys(local.parametros_secretos)))
  name     = "${local.prefijo_parametros}/${each.value}"
  type     = "SecureString"
  value    = local.parametros_secretos[each.value]
}

resource "aws_ssm_parameter" "valor" {
  for_each = merge(local.parametros, local.parametros_hedera)
  name     = "${local.prefijo_parametros}/${each.key}"
  type     = "String"
  value    = each.value
}
