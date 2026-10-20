#!/bin/bash
# Crea o actualiza toda la infraestructura de AWS con un solo comando
# (funcionalidad 017). Se ejecuta en la computadora de la autora, desde
# cualquier carpeta:
#
#   bash infraestructura/scripts/crear_infraestructura_aws.sh
#
# Verifica las credenciales, crea el bucket del estado si falta, arma
# backend.hcl, controla terraform.tfvars y aplica la infraestructura principal.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ESTADO="$RAIZ/infraestructura/terraform/estado"
PRINCIPAL="$RAIZ/infraestructura/terraform/principal"

fallar() { echo; echo "ERROR: $1" >&2; exit 1; }
paso() { echo; echo "==> $1"; }

paso "Herramientas"
command -v aws >/dev/null || fallar "Falta la AWS CLI (paso 2 de la guía)."
command -v terraform >/dev/null || fallar "Falta Terraform (paso 2 de la guía)."
[ -f "$PRINCIPAL/servidor.tf" ] || fallar "No están los archivos de Terraform. Ejecutá: git checkout funcionalidad/017-infraestructura-aws && git pull"

paso "Credenciales de AWS"
chmod 700 ~/.aws 2>/dev/null || true
chmod 600 ~/.aws/credentials ~/.aws/config 2>/dev/null || true
identidad=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null) \
  || fallar "Las credenciales no funcionan. Ejecutá 'aws configure' con la clave del usuario terraform-autora."
echo "Usuario: $identidad"
[[ "$identidad" == *":root" ]] && fallar "Estás usando el usuario raíz. Configurá la clave de terraform-autora con 'aws configure'."
cuenta=$(aws sts get-caller-identity --query Account --output text)
bucket_estado="deteccion-imagenes-tfstate-$cuenta"

paso "Bucket del estado de Terraform ($bucket_estado)"
if aws s3api head-bucket --bucket "$bucket_estado" 2>/dev/null; then
  echo "Ya existe."
else
  terraform -chdir="$ESTADO" init -input=false
  terraform -chdir="$ESTADO" apply -auto-approve
fi
echo "bucket = \"$bucket_estado\"" > "$PRINCIPAL/backend.hcl"

paso "Variables (terraform.tfvars)"
if [ ! -f "$PRINCIPAL/terraform.tfvars" ]; then
  cp "$PRINCIPAL/terraform.tfvars.ejemplo" "$PRINCIPAL/terraform.tfvars"
  fallar "Se creó $PRINCIPAL/terraform.tfvars. Abrilo con 'nano $PRINCIPAL/terraform.tfvars', poné tus correos y los de los tutores, guardá y volvé a ejecutar este script."
fi
if grep -v "^[[:space:]]*#" "$PRINCIPAL/terraform.tfvars" | grep -q "ejemplo.com"; then
  fallar "terraform.tfvars todavía tiene correos de ejemplo. Editalo con 'nano $PRINCIPAL/terraform.tfvars' y volvé a ejecutar este script."
fi
grep -E "^(correo|administradores)" "$PRINCIPAL/terraform.tfvars"

paso "Infraestructura principal"
terraform -chdir="$PRINCIPAL" init -input=false -reconfigure -backend-config=backend.hcl
terraform -chdir="$PRINCIPAL" plan -input=false -out=plan.tfplan
echo
read -r -p "¿Crear estos recursos en AWS? Escribí 'si' para continuar: " respuesta
[ "$respuesta" = "si" ] || fallar "Cancelado; no se creó nada."
terraform -chdir="$PRINCIPAL" apply -input=false plan.tfplan
rm -f "$PRINCIPAL/plan.tfplan"

paso "Listo. Pasale esta salida al asistente y seguí con el paso 6 de la guía:"
terraform -chdir="$PRINCIPAL" output
