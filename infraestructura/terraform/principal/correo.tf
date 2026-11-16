# Amazon SES (RF47). Mientras la cuenta está en modo de prueba (sandbox), SES
# solo entrega a direcciones verificadas: al aplicar, cada correo de la lista
# recibe un enlace de verificación de AWS (CP-16).

# Con dominio propio, el remitente del dominio ya queda cubierto por la identidad
# del dominio (dns.tf) y no se le pide verificar la dirección por separado; las
# direcciones de destino siguen haciendo falta mientras SES esté en modo de prueba.
resource "aws_ses_email_identity" "correo" {
  for_each = toset([
    for correo in concat([var.correo_remitente], var.correos_verificados) : correo
    if var.dominio == "" || !endswith(lower(correo), "@${lower(var.dominio)}")
  ])
  email = each.value
}

# Usuario técnico solo para el SMTP de SES: la aplicación envía por SMTP
# (app/integraciones/correo.py). Su contraseña SMTP se guarda cifrada en
# Parameter Store y nunca en el repositorio (RNF03 CA3).
resource "aws_iam_user" "smtp" {
  name = "${var.proyecto}-ses-smtp"
}

resource "aws_iam_user_policy" "smtp" {
  name = "enviar-correos"
  user = aws_iam_user.smtp.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ses:SendRawEmail"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_access_key" "smtp" {
  user = aws_iam_user.smtp.name
}
