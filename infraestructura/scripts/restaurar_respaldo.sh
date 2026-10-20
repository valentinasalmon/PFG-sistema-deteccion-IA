#!/bin/bash
# Restaura un respaldo de la base (RNF15 CA3). Detiene la aplicación,
# reemplaza la base y la vuelve a levantar.
# Uso: restaurar_respaldo.sh plataforma-AAAA-MM-DDTHHMMSSZ.dump
set -euo pipefail
source /etc/plataforma/aws.env
export AWS_DEFAULT_REGION
ARCHIVO=$1
aws s3 cp "s3://$BUCKET_OPERACION/respaldos/$ARCHIVO" /tmp/restaurar.dump
systemctl stop plataforma-web plataforma-trabajador
sudo -u postgres dropdb --if-exists plataforma
sudo -u postgres createdb -O plataforma plataforma
sudo -u postgres pg_restore --no-owner --role=plataforma -d plataforma /tmp/restaurar.dump
rm -f /tmp/restaurar.dump
systemctl start plataforma-web plataforma-trabajador
echo "Base restaurada desde $ARCHIVO."
