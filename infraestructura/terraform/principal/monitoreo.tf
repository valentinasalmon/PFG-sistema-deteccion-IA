# Monitoreo y alertas (funcionalidad 053).
#
# Pedido de la autora (2026-11-24): «agreguemos alguna herramienta de
# monitoreo». Se usa CloudWatch, de AWS, sin instalar agentes: el servidor
# publica sus métricas cada 15 minutos con scripts/medir_salud.sh y estas
# alarmas avisan por correo (SNS) cuando algo falla y cuando se recupera.
#
# Frecuencia: 15 minutos alcanzan para el MVP (pedido de la autora, 2026-11-26).
# En una operación comercial conviene 5: bajar PERIODO_MONITOREO y el temporizador
# plataforma-monitoreo.timer.
#
# Costo estimado: 5 métricas propias × USD 0,30 = USD 1,50 por mes (se cobra
# por métrica, no por medición); las alarmas entran en las 10 gratuitas.
#
# Si el hardware de AWS falla, la EC2 se recupera sola (recuperación automática
# simplificada, activa por defecto en las t3); la alarma de estado avisa igual.

resource "aws_sns_topic" "alertas" {
  name = "${var.proyecto}-alertas"
}

# AWS manda un correo para confirmar la suscripción: hay que aceptarlo una vez.
resource "aws_sns_topic_subscription" "alertas_correo" {
  topic_arn = aws_sns_topic.alertas.arn
  protocol  = "email"
  endpoint  = var.correo_alertas
}

locals {
  periodo_monitoreo = 900 # segundos: 15 minutos, igual que el temporizador
  espacio_metricas  = "evidentIA"
  acciones_alerta   = [aws_sns_topic.alertas.arn]

  # Métricas que publica medir_salud.sh: umbral, comparación y cómo tratar la falta de datos.
  alarmas_propias = {
    plataforma-caida = {
      metrica     = "Saludable"
      comparacion = "LessThanThreshold"
      umbral      = 1
      periodos    = 2
      estadistica = "Minimum"
      sin_datos   = "breaching" # si el servidor deja de publicar, también es una caída
      descripcion = "La plataforma no responde en https://${local.dominio}/api/salud desde hace 30 minutos."
    }
    tareas-fallidas = {
      metrica     = "TareasFallidas"
      comparacion = "GreaterThanOrEqualToThreshold"
      umbral      = 1
      periodos    = 1
      estadistica = "Maximum"
      sin_datos   = "missing"
      descripcion = "Una tarea programada (sellos, retención, respaldo o catálogo de la SSN) terminó con error. Ver: systemctl list-units 'plataforma-*' --failed"
    }
    disco-lleno = {
      metrica     = "DiscoUsado"
      comparacion = "GreaterThanThreshold"
      umbral      = 85
      periodos    = 1
      estadistica = "Maximum"
      sin_datos   = "missing"
      descripcion = "El disco del servidor está por encima del 85 %."
    }
    memoria-baja = {
      metrica     = "MemoriaDisponible"
      comparacion = "LessThanThreshold"
      umbral      = 150
      periodos    = 2
      estadistica = "Minimum"
      sin_datos   = "missing"
      descripcion = "Quedan menos de 150 MB de memoria disponible desde hace 30 minutos."
    }
    certificado-por-vencer = {
      metrica     = "DiasCertificado"
      comparacion = "LessThanThreshold"
      umbral      = 14
      periodos    = 1
      estadistica = "Minimum"
      sin_datos   = "missing"
      descripcion = "Al certificado HTTPS le quedan menos de 14 días: la renovación automática de Let's Encrypt falló."
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "propia" {
  for_each = local.alarmas_propias

  alarm_name          = "${var.proyecto}-${each.key}"
  alarm_description   = each.value.descripcion
  namespace           = local.espacio_metricas
  metric_name         = each.value.metrica
  statistic           = each.value.estadistica
  period              = local.periodo_monitoreo
  evaluation_periods  = each.value.periodos
  comparison_operator = each.value.comparacion
  threshold           = each.value.umbral
  treat_missing_data  = each.value.sin_datos
  alarm_actions       = local.acciones_alerta
  ok_actions          = local.acciones_alerta
}

# Métrica de la EC2 que publica AWS sin costo: falla de la máquina o del sistema operativo.
resource "aws_cloudwatch_metric_alarm" "servidor_estado" {
  alarm_name          = "${var.proyecto}-servidor-sin-respuesta"
  alarm_description   = "La EC2 no pasa los controles de estado de AWS desde hace 5 minutos."
  namespace           = "AWS/EC2"
  metric_name         = "StatusCheckFailed"
  dimensions          = { InstanceId = aws_instance.servidor.id }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 5
  comparison_operator = "GreaterThanOrEqualToThreshold"
  threshold           = 1
  treat_missing_data  = "breaching"
  alarm_actions       = local.acciones_alerta
  ok_actions          = local.acciones_alerta
}

resource "aws_cloudwatch_metric_alarm" "servidor_cpu" {
  alarm_name          = "${var.proyecto}-cpu-alta"
  alarm_description   = "La CPU de la EC2 está por encima del 85 % desde hace 15 minutos (puede agotar los créditos de la t3)."
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  dimensions          = { InstanceId = aws_instance.servidor.id }
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 3
  comparison_operator = "GreaterThanThreshold"
  threshold           = 85
  treat_missing_data  = "missing"
  alarm_actions       = local.acciones_alerta
  ok_actions          = local.acciones_alerta
}

# Tablero con las métricas de la plataforma y la CPU que publica AWS (CloudWatch → Dashboards).
resource "aws_cloudwatch_dashboard" "plataforma" {
  dashboard_name = var.proyecto
  dashboard_body = jsonencode({
    widgets = [
      for indice, metrica in ["Saludable", "TareasFallidas", "DiscoUsado", "MemoriaDisponible", "DiasCertificado"] : {
        type   = "metric"
        x      = (indice % 3) * 8
        y      = floor(indice / 3) * 6
        width  = 8
        height = 6
        properties = {
          title   = metrica
          region  = var.region
          metrics = [[local.espacio_metricas, metrica]]
          period  = local.periodo_monitoreo
          stat    = "Average"
          view    = "timeSeries"
        }
      }
    ]
  })
}
