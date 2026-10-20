# Red: VPC por defecto de la cuenta y grupo de seguridad de la EC2.
# Solo se abren HTTP y HTTPS. No hay SSH: la administración y el despliegue
# usan AWS Systems Manager, sin puertos abiertos ni claves (RNF02).

data "aws_vpc" "por_defecto" {
  default = true
}

data "aws_subnets" "por_defecto" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.por_defecto.id]
  }
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

resource "aws_security_group" "servidor" {
  name        = "${var.proyecto}-servidor"
  description = "HTTP y HTTPS de la plataforma"
  vpc_id      = data.aws_vpc.por_defecto.id
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.servidor.id
  description       = "HTTP: certificados de Lets Encrypt y redireccion a HTTPS"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.servidor.id
  description       = "HTTPS de la plataforma"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

resource "aws_vpc_security_group_egress_rule" "salida" {
  security_group_id = aws_security_group.servidor.id
  description       = "Salida: paquetes, S3, SES, SSM y Lets Encrypt"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
