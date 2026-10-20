#!/bin/bash
# Pide el certificado HTTPS a Let's Encrypt para el dominio configurado y
# pasa Nginx a HTTPS. También sirve al cambiar al dominio propio.
set -euo pipefail
DOMINIO=$(cat /etc/plataforma/dominio)
CORREO=$(cat /etc/plataforma/correo_alertas)
certbot certonly --webroot -w /var/www/certbot -d "$DOMINIO" \
  --email "$CORREO" --agree-tos --non-interactive --keep-until-expiring
bash /opt/plataforma/servidor/scripts/instalar_configuracion.sh
