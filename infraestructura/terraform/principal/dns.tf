# Dominio propio (funcionalidad 040, CP-16). Con la variable `dominio` vacía no
# se crea nada y la plataforma sigue en <ip>.sslip.io.
#
# Con dominio, Terraform administra todo el DNS en Route 53 para que nada se
# cargue a mano: el registro A al servidor, las tres claves DKIM de SES y la
# política DMARC. La autora solo delega el dominio en NIC Argentina a los
# servidores de nombres que devuelve la salida `servidores_de_nombres`.
# Route 53 cuesta US$ 0,50 por mes por zona.
#
# Realiza: RF47 (correos desde el dominio, fuera de Spam), RNF03 (HTTPS con el
# certificado del dominio).

locals {
  dominio_propio = var.dominio != ""
}

resource "aws_route53_zone" "dominio" {
  count   = local.dominio_propio ? 1 : 0
  name    = var.dominio
  comment = "Zona de la plataforma (Terraform)"
}

# La plataforma responde en el dominio raíz; el certificado se pide para él.
resource "aws_route53_record" "servidor" {
  count   = local.dominio_propio ? 1 : 0
  zone_id = aws_route53_zone.dominio[0].zone_id
  name    = var.dominio
  type    = "A"
  ttl     = 300
  records = [aws_eip.servidor.public_ip]
}

# Identidad de dominio en SES con Easy DKIM: cualquier dirección del dominio
# puede ser remitente sin verificarla una por una.
resource "aws_sesv2_email_identity" "dominio" {
  count          = local.dominio_propio ? 1 : 0
  email_identity = var.dominio
}

resource "aws_route53_record" "dkim" {
  count   = local.dominio_propio ? 3 : 0
  zone_id = aws_route53_zone.dominio[0].zone_id
  name    = "${aws_sesv2_email_identity.dominio[0].dkim_signing_attributes[0].tokens[count.index]}._domainkey.${var.dominio}"
  type    = "CNAME"
  ttl     = 1800
  records = ["${aws_sesv2_email_identity.dominio[0].dkim_signing_attributes[0].tokens[count.index]}.dkim.amazonses.com"]
}

# DMARC en modo observación: ayuda a que los correos no caigan en Spam sin
# rechazar nada mientras se ajusta el envío.
resource "aws_route53_record" "dmarc" {
  count   = local.dominio_propio ? 1 : 0
  zone_id = aws_route53_zone.dominio[0].zone_id
  name    = "_dmarc.${var.dominio}"
  type    = "TXT"
  ttl     = 3600
  records = ["v=DMARC1; p=none;"]
}
