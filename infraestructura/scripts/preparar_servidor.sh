#!/bin/bash
# Prepara la EC2 de producción (funcionalidad 017). Lo ejecuta el primer
# arranque (user_data) y se puede repetir sin romper nada.
#
# Instala los paquetes del sistema, crea la base de datos, arma el .env desde
# Parameter Store, configura Nginx y servicios y pide el certificado HTTPS.
set -euo pipefail
source /etc/plataforma/aws.env
export AWS_DEFAULT_REGION
SERVIDOR=/opt/plataforma/servidor

echo "== Paquetes del sistema"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q \
  python3 python3-venv python3-dev build-essential \
  postgresql redis-server nginx certbot \
  libimage-exiftool-perl libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
  fonts-dejavu-core jq

echo "== Memoria de intercambio (2 GB) para los picos de los análisis"
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  echo "/swapfile none swap sw 0 0" >> /etc/fstab
fi

echo "== Usuario y carpetas de la aplicación"
id plataforma >/dev/null 2>&1 || useradd --system --home /opt/plataforma --shell /usr/sbin/nologin plataforma
mkdir -p /opt/plataforma/versiones /var/www/certbot
chown plataforma:plataforma /opt/plataforma /opt/plataforma/versiones

echo "== Configuración de la aplicación"
bash "$SERVIDOR/scripts/generar_entorno.sh"
CONTRASENIA_BD=$(aws ssm get-parameter --with-decryption --name "$PREFIJO_PARAMETROS/CONTRASENIA_BD" --query Parameter.Value --output text)

echo "== PostgreSQL (solo escucha en la propia máquina)"
systemctl enable --now postgresql
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='plataforma'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE ROLE plataforma LOGIN PASSWORD '$CONTRASENIA_BD'"
fi
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='plataforma'" | grep -q 1 \
  || sudo -u postgres createdb -O plataforma plataforma

echo "== Redis (solo escucha en la propia máquina)"
systemctl enable --now redis-server

echo "== Nginx, servicios y respaldos"
bash "$SERVIDOR/scripts/instalar_configuracion.sh"

echo "== Certificado HTTPS de Let's Encrypt"
bash "$SERVIDOR/scripts/pedir_certificado.sh" || echo "AVISO: no se pudo obtener el certificado; reintentar con pedir_certificado.sh"

echo "== Listo. La aplicación se instala con el primer despliegue (desplegar.sh)."
