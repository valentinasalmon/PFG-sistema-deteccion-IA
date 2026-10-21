# Configuración de la aplicación en Parameter Store (/<proyecto>/produccion/).
# La EC2 la lee al arrancar y en cada despliegue y arma su archivo .env
# (scripts/generar_entorno.sh). Los secretos se generan acá y van cifrados.

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
  }
}

resource "aws_ssm_parameter" "secreto" {
  for_each = nonsensitive(toset(keys(local.parametros_secretos)))
  name     = "${local.prefijo_parametros}/${each.value}"
  type     = "SecureString"
  value    = local.parametros_secretos[each.value]
}

resource "aws_ssm_parameter" "valor" {
  for_each = local.parametros
  name     = "${local.prefijo_parametros}/${each.key}"
  type     = "String"
  value    = each.value
}
