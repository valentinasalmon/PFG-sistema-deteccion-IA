# Servidor: una EC2 con Ubuntu 24.04 que corre Nginx, Gunicorn, el trabajador
# de RQ, PostgreSQL y Redis (ADR-0005, RNF22 CA3).

# Imagen vigente de Ubuntu 24.04 publicada por Canonical. Se toma del
# parámetro público que Canonical mantiene en cada región, más estable que
# buscar la imagen por su nombre.
data "aws_ssm_parameter" "ubuntu" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

# La IP fija se crea antes que la EC2 porque el dominio provisorio
# (<ip>.sslip.io) se deriva de ella y la EC2 lo lee al arrancar.
resource "aws_eip" "servidor" {
  domain = "vpc"
  tags   = { Name = "${var.proyecto}-servidor" }
}

resource "aws_instance" "servidor" {
  ami                    = nonsensitive(data.aws_ssm_parameter.ubuntu.value)
  instance_type          = var.tipo_instancia
  subnet_id              = data.aws_subnets.por_defecto.ids[0]
  vpc_security_group_ids = [aws_security_group.servidor.id]
  iam_instance_profile   = aws_iam_instance_profile.servidor.name

  root_block_device {
    volume_type = "gp3"
    volume_size = var.tamanio_disco_gb
    encrypted   = true
  }

  # IMDSv2 obligatorio: evita que una falla SSRF lea las credenciales del rol.
  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  user_data = templatefile("${path.module}/inicio.sh.tftpl", {
    region             = var.region
    bucket_operacion   = aws_s3_bucket.bucket["operacion"].bucket
    prefijo_parametros = local.prefijo_parametros
  })
  user_data_replace_on_change = false

  # La EC2 necesita sus scripts y su configuración apenas arranca.
  depends_on = [aws_s3_object.servidor, aws_ssm_parameter.valor, aws_ssm_parameter.secreto]

  tags = { Name = "${var.proyecto}-servidor" }

  lifecycle {
    # Una AMI nueva de Ubuntu no debe reemplazar el servidor (y su base de datos).
    ignore_changes = [ami, user_data]
  }
}

resource "aws_eip_association" "servidor" {
  allocation_id = aws_eip.servidor.id
  instance_id   = aws_instance.servidor.id
}
