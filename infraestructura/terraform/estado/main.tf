# Bucket del estado de Terraform (funcionalidad 017).
#
# Se aplica UNA sola vez, con estado local, antes de la infraestructura
# principal. Guarda el estado de "principal/" en S3, cifrado y versionado, para
# que no dependa de la computadora de la autora (ver docs/guias/despliegue-aws.md).

terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.66"
    }
  }
}

variable "region" {
  description = "Región de AWS (Irlanda, RNF08 CA6)."
  type        = string
  default     = "eu-west-1"
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Proyecto = "deteccion-imagenes", Gestion = "terraform" }
  }
}

data "aws_caller_identity" "cuenta" {}

resource "aws_s3_bucket" "estado" {
  bucket = "deteccion-imagenes-tfstate-${data.aws_caller_identity.cuenta.account_id}"
}

resource "aws_s3_bucket_versioning" "estado" {
  bucket = aws_s3_bucket.estado.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "estado" {
  bucket = aws_s3_bucket.estado.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "estado" {
  bucket                  = aws_s3_bucket.estado.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "bucket_estado" {
  description = "Nombre del bucket para el archivo backend.hcl de principal/."
  value       = aws_s3_bucket.estado.bucket
}
