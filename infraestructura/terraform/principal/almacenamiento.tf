# Buckets de S3 (RNF03 CA1): privados, cifrados y versionados.
# - imagenes: imágenes e informes de los casos (ADR-0012).
# - operacion: scripts del servidor, artefactos de despliegue y respaldos de
#   la base, que vencen a los 30 días (RNF15 CA2, RF49 CA3).

resource "random_id" "sufijo" {
  byte_length = 3
}

locals {
  buckets = {
    imagenes  = "${var.proyecto}-imagenes-${random_id.sufijo.hex}"
    operacion = "${var.proyecto}-operacion-${random_id.sufijo.hex}"
  }
}

resource "aws_s3_bucket" "bucket" {
  for_each = local.buckets
  bucket   = each.value
}

resource "aws_s3_bucket_public_access_block" "bucket" {
  for_each                = aws_s3_bucket.bucket
  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "bucket" {
  for_each = aws_s3_bucket.bucket
  bucket   = each.value.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bucket" {
  for_each = aws_s3_bucket.bucket
  bucket   = each.value.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "bucket" {
  for_each = aws_s3_bucket.bucket
  bucket   = each.value.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Las versiones anteriores de las imágenes no se conservan indefinidamente: la
# aplicación borra todas las versiones al eliminar (RN21) y esta regla limpia
# lo que quede.
resource "aws_s3_bucket_lifecycle_configuration" "imagenes" {
  bucket = aws_s3_bucket.bucket["imagenes"].id
  rule {
    id     = "versiones-anteriores"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "operacion" {
  bucket = aws_s3_bucket.bucket["operacion"].id
  rule {
    id     = "respaldos-30-dias"
    status = "Enabled"
    filter {
      prefix = "respaldos/"
    }
    expiration {
      days = 30
    }
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }
  rule {
    id     = "artefactos-30-dias"
    status = "Enabled"
    filter {
      prefix = "artefactos/"
    }
    expiration {
      days = 30
    }
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }
}

# Scripts y configuración que la EC2 descarga al crearse. En cada despliegue
# se reemplazan por los del artefacto, así que esto solo cubre el arranque.
locals {
  archivos_servidor = merge(
    { for f in fileset("${path.module}/../../scripts", "*.sh") : "scripts/${f}" => "${path.module}/../../scripts/${f}" },
    { for f in fileset("${path.module}/../../nginx", "*.conf") : "nginx/${f}" => "${path.module}/../../nginx/${f}" },
    { for f in fileset("${path.module}/../../systemd", "*") : "systemd/${f}" => "${path.module}/../../systemd/${f}" },
  )
}

resource "aws_s3_object" "servidor" {
  for_each = local.archivos_servidor
  bucket   = aws_s3_bucket.bucket["operacion"].id
  key      = "servidor/${each.key}"
  source   = each.value
  etag     = filemd5(each.value)
}
