#!/bin/bash
# Arma /opt/plataforma/.env con los parámetros de Parameter Store
# (/<proyecto>/produccion/*), creados por Terraform. Nunca se guardan secretos
# en el repositorio ni en la imagen del servidor (RNF03 CA3).
# El modelo de la capa 4 se guarda fuera de cada versión desplegada, así no se
# vuelve a bajar en cada despliegue (funcionalidad 012).
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
VERIFICACION_IDENTIDAD=${P[VERIFICACION_IDENTIDAD]:-desactivado}
HEDERA_RED=${P[HEDERA_RED]:-testnet}
HEDERA_CUENTA=${P[HEDERA_CUENTA]:-}
HEDERA_TEMA=${P[HEDERA_TEMA]:-}
HEDERA_CLAVE=${P[HEDERA_CLAVE]:-}
GOOGLE_ID_CLIENTE=${P[GOOGLE_ID_CLIENTE]:-}
GOOGLE_SECRETO_CLIENTE=${P[GOOGLE_SECRETO_CLIENTE]:-}
MODELO_RED_NEURONAL_REGISTRO=${P[MODELO_RED_NEURONAL_REGISTRO]:-}
MODELO_RED_NEURONAL_VERSION=${P[MODELO_RED_NEURONAL_VERSION]:-}
HF_TOKEN=${P[HF_TOKEN]:-}
CARPETA_MODELOS_ONNX=/opt/plataforma/modelos_onnx
FIN
install -o plataforma -g plataforma -m 600 "$temporal" /opt/plataforma/.env
rm -f "$temporal"
echo "${P[DOMINIO]}" > /etc/plataforma/dominio
echo "${P[CORREO_ALERTAS]}" > /etc/plataforma/correo_alertas
