# Amazon SES (RF47). Mientras la cuenta está en modo de prueba (sandbox), SES
# solo entrega a direcciones verificadas: al aplicar, cada correo de la lista
# recibe un enlace de verificación de AWS (CP-16).

resource "aws_ses_email_identity" "correo" {
  for_each = toset(concat([var.correo_remitente], var.correos_verificados))
  email    = each.value
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
