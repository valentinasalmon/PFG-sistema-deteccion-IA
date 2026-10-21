#!/bin/bash
# Arma /opt/plataforma/.env con los parámetros de Parameter Store
# (/<proyecto>/produccion/*), creados por Terraform. Nunca se guardan secretos
# en el repositorio ni en la imagen del servidor (RNF03 CA3).
set -euo pipefail
source /etc/plataforma/aws.env
export AWS_DEFAULT_REGION

declare -A P
while IFS=$'\t' read -r nombre valor; do
  P["${nombre##*/}"]="$valor"
done < <(aws ssm get-parameters-by-path --path "$PREFIJO_PARAMETROS" --with-decryption \
  --query 'Parameters[].[Name,Value]' --output text)

temporal=$(mktemp)
cat > "$temporal" <<FIN
ENTORNO=produccion
CLAVE_SECRETA=${P[CLAVE_SECRETA]}
URL_BASE_DATOS=postgresql+psycopg://plataforma:${P[CONTRASENIA_BD]}@localhost:5432/plataforma
URL_REDIS=redis://localhost:6379/0
URL_FRONTEND=https://${P[DOMINIO]}
SERVIDOR_CORREO=${P[SERVIDOR_CORREO]}
PUERTO_CORREO=587
USAR_TLS_CORREO=si
USUARIO_CORREO=${P[USUARIO_CORREO]}
CONTRASENIA_CORREO=${P[CONTRASENIA_CORREO]}
REMITENTE_CORREO="${P[REMITENTE_CORREO]}"
ADMINISTRADORES=${P[ADMINISTRADORES]}
S3_BUCKET=${P[S3_BUCKET]}
S3_REGION=${P[S3_REGION]}
PROXIES_DE_CONFIANZA=1
SELLO_TIEMPO=${P[SELLO_TIEMPO]:-desactivado}
FIN
install -o plataforma -g plataforma -m 600 "$temporal" /opt/plataforma/.env
rm -f "$temporal"
echo "${P[DOMINIO]}" > /etc/plataforma/dominio
echo "${P[CORREO_ALERTAS]}" > /etc/plataforma/correo_alertas
