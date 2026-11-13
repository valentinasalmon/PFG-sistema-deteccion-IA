# Datos que la autora necesita después de aplicar (ver la guía de despliegue).

output "url" {
  description = "Dirección de la plataforma."
  value       = "https://${local.dominio}"
}

output "ip_publica" {
  description = "IP fija del servidor (para el registro DNS del dominio propio)."
  value       = aws_eip.servidor.public_ip
}

output "servidores_de_nombres" {
  description = "Servidores de nombres de Route 53: se cargan en NIC Argentina, en Delegar (vacío sin dominio propio)."
  value       = local.dominio_propio ? aws_route53_zone.dominio[0].name_servers : []
}

output "id_instancia" {
  description = "EC2 del servidor (variable ID_INSTANCIA de GitHub)."
  value       = aws_instance.servidor.id
}

output "variables_github" {
  description = "Variables a cargar en GitHub > Settings > Secrets and variables > Actions > Variables."
  value = {
    AWS_REGION          = var.region
    AWS_ROLE_DESPLIEGUE = aws_iam_role.despliegue.arn
    BUCKET_OPERACION    = aws_s3_bucket.bucket["operacion"].bucket
    ID_INSTANCIA        = aws_instance.servidor.id
  }
}

output "bucket_imagenes" {
  description = "Bucket privado de las imágenes y los informes."
  value       = aws_s3_bucket.bucket["imagenes"].bucket
}
