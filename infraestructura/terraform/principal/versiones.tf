# Proveedores y estado remoto de la infraestructura principal (funcionalidad 017).
#
# El bucket del estado se indica en backend.hcl (no se sube: ver
# backend.hcl.ejemplo) y se crea antes con ../estado.

terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.66"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.8"
    }
  }
  backend "s3" {
    key          = "principal/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Proyecto = var.proyecto, Gestion = "terraform" }
  }
}

data "aws_caller_identity" "cuenta" {}
