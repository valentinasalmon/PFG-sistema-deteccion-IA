#!/bin/bash
# Mide la salud de la plataforma y la publica en CloudWatch (funcionalidad 053; RNF15, RNF16).
#
# Lo ejecuta plataforma-monitoreo.timer cada 15 minutos. Publica en el espacio
# «evidentIA» cinco métricas que vigilan las alarmas de monitoreo.tf:
#   Saludable          1 si https://DOMINIO/api/salud responde 200 (pasa por
#                      Nginx, el certificado, Gunicorn, la base y Redis), si no 0
#   TareasFallidas     servicios plataforma-* en estado «failed» (sellos,
#                      retención, respaldo, catálogo de la SSN)
#   DiscoUsado         porcentaje usado del disco raíz
#   MemoriaDisponible  megabytes de memoria disponible
#   DiasCertificado    días que le quedan al certificado HTTPS (si se pudo leer)
# La CPU no se mide acá: la publica AWS sin costo y la vigila otra alarma.
# Si el servidor se cae, deja de publicar: la alarma de «Saludable» trata la
# falta de datos como falla.
set -uo pipefail

: "${DOMINIO:?Falta DOMINIO}"
REGION=${S3_REGION:-eu-west-1}

if curl -fsS --max-time 15 -o /dev/null "https://$DOMINIO/api/salud"; then
  SALUDABLE=1
else
  SALUDABLE=0
fi
TAREAS_FALLIDAS=$(systemctl list-units 'plataforma-*' --state=failed --no-legend --plain | wc -l)
DISCO_USADO=$(df --output=pcent / | tail -1 | tr -dc '0-9')
MEMORIA_DISPONIBLE=$(awk '/^MemAvailable:/ {printf "%d", $2 / 1024}' /proc/meminfo)
VENCE=$(echo | timeout 15 openssl s_client -servername "$DOMINIO" -connect "$DOMINIO:443" 2>/dev/null \
  | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
METRICAS=(
  "MetricName=Saludable,Value=$SALUDABLE,Unit=Count"
  "MetricName=TareasFallidas,Value=$TAREAS_FALLIDAS,Unit=Count"
  "MetricName=DiscoUsado,Value=$DISCO_USADO,Unit=Percent"
  "MetricName=MemoriaDisponible,Value=$MEMORIA_DISPONIBLE,Unit=Megabytes"
)
# Si no se pudo leer el certificado, no se publica ese dato: un 0 dispararía una
# alarma falsa, y si el sitio no responde ya avisa la alarma de «Saludable».
DIAS_CERTIFICADO="sin dato"
if [ -n "$VENCE" ]; then
  DIAS_CERTIFICADO=$(( ($(date -d "$VENCE" +%s) - $(date +%s)) / 86400 ))
  METRICAS+=("MetricName=DiasCertificado,Value=$DIAS_CERTIFICADO,Unit=Count")
fi

aws cloudwatch put-metric-data --region "$REGION" --namespace evidentIA --metric-data "${METRICAS[@]}"

echo "salud=$SALUDABLE tareas_fallidas=$TAREAS_FALLIDAS disco=$DISCO_USADO% memoria=${MEMORIA_DISPONIBLE}MB certificado=$DIAS_CERTIFICADO"
