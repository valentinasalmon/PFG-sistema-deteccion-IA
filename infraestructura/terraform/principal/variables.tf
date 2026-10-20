# Variables de la infraestructura. Los valores personales (correos) van en
# terraform.tfvars, que no se sube al repositorio (ver terraform.tfvars.ejemplo).

variable "region" {
  description = "Región de AWS: Irlanda, jurisdicción con protección adecuada (RNF08 CA6)."
  type        = string
  default     = "eu-west-1"
}

variable "proyecto" {
  description = "Prefijo de los nombres de los recursos."
  type        = string
  default     = "deteccion-imagenes"
}

variable "tipo_instancia" {
  description = "Tipo de EC2. t3.small (2 GB) alcanza para la aplicación, PostgreSQL y Redis."
  type        = string
  default     = "t3.small"
}

variable "tamanio_disco_gb" {
  description = "Disco de la EC2 (sistema, PostgreSQL y versiones desplegadas)."
  type        = number
  default     = 30
}

variable "dominio" {
  description = "Dominio propio. Vacío: se usa <ip>.sslip.io hasta comprar uno (CP-16)."
  type        = string
  default     = ""
}

variable "correo_remitente" {
  description = "Correo verificado en SES que figura como remitente de la plataforma."
  type        = string
}

variable "correos_verificados" {
  description = "Destinatarios que SES acepta mientras está en modo de prueba (sandbox)."
  type        = list(string)
  default     = []
}

variable "administradores" {
  description = "Correos que reciben el rol de Administrador (funcionalidad 021)."
  type        = list(string)
}

variable "correo_alertas" {
  description = "Correo que recibe las alertas de presupuesto y los avisos de Let's Encrypt."
  type        = string
}

variable "presupuesto_mensual_usd" {
  description = "Presupuesto mensual en dólares; avisa al 50 %, al 80 % y si se proyecta superarlo."
  type        = number
  default     = 30
}

variable "repositorio_github" {
  description = "Repositorio autorizado a desplegar desde la rama main (propietario/nombre)."
  type        = string
  default     = "valentinasalmon/PFG-sistema-deteccion-IA"
}
