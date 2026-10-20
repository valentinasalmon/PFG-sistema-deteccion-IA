#!/bin/bash
# Respaldo diario de PostgreSQL en S3 (RNF15 CA2). El bucket borra los
# respaldos a los 30 días, así los datos destruidos por retención no quedan
# para siempre en las copias (RF49 CA3).
set -euo pipefail
source /etc/plataforma/aws.env
export AWS_DEFAULT_REGION
FECHA=$(date -u +%Y-%m-%dT%H%M%SZ)
sudo -u postgres pg_dump --format=custom plataforma \
  | aws s3 cp - "s3://$BUCKET_OPERACION/respaldos/plataforma-$FECHA.dump" --sse AES256
echo "Respaldo plataforma-$FECHA.dump guardado."
