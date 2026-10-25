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

variable "id_propietario_github" {
  description = "Número de la cuenta de GitHub dueña del repositorio (figura en la identidad OIDC)."
  type        = string
  default     = "141863784"
}

variable "id_repositorio_github" {
  description = "Número del repositorio en GitHub (figura en la identidad OIDC)."
  type        = string
  default     = "1410365187"
}

variable "sello_tiempo" {
  description = "Sello de tiempo de las imágenes en Hedera (funcionalidad 023, ADR-0018): hedera o desactivado."
  type        = string
  default     = "desactivado"

  validation {
    condition     = contains(["hedera", "desactivado"], var.sello_tiempo)
    error_message = "En producción el sello es hedera o desactivado: nunca simulado."
  }
}

variable "hedera_red" {
  description = "Red de Hedera: testnet para desarrollar, mainnet para la defensa (CP-26)."
  type        = string
  default     = "testnet"

  validation {
    condition     = contains(["testnet", "mainnet"], var.hedera_red)
    error_message = "La red de Hedera es testnet o mainnet."
  }
}

variable "hedera_cuenta" {
  description = "Account ID de Hedera que paga los sellos (0.0.…). La clave privada NO va acá: se carga a mano en SSM como SecureString."
  type        = string
  default     = ""
}

variable "hedera_tema" {
  description = "Topic ID de Hedera donde se publican las huellas (lo devuelve `flask sellos crear-tema`)."
  type        = string
  default     = ""
}
