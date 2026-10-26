#!/bin/bash
# Instala la configuración de Nginx y los servicios de systemd desde
# /opt/plataforma/servidor. Se ejecuta al preparar el servidor y en cada
# despliegue, así los cambios de configuración viajan con el código.
set -euo pipefail
SERVIDOR=/opt/plataforma/servidor
DOMINIO=$(cat /etc/plataforma/dominio)

# Con certificado se usa la configuración HTTPS; sin él, la provisoria en HTTP.
if [ -f "/etc/letsencrypt/live/$DOMINIO/fullchain.pem" ]; then
  plantilla="$SERVIDOR/nginx/plataforma.conf"
else
  plantilla="$SERVIDOR/nginx/plataforma-sin-tls.conf"
fi
# Límites de pedidos (zonas en el bloque http) y rutas de la API (030).
install -m 644 "$SERVIDOR/nginx/limites.conf" /etc/nginx/conf.d/plataforma-limites.conf
install -d /etc/nginx/snippets
install -m 644 "$SERVIDOR/nginx/api.conf" /etc/nginx/snippets/plataforma-api.conf
sed "s/__DOMINIO__/$DOMINIO/g" "$plantilla" > /etc/nginx/sites-available/plataforma
ln -sfn /etc/nginx/sites-available/plataforma /etc/nginx/sites-enabled/plataforma
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl reload nginx || systemctl restart nginx

install -m 644 "$SERVIDOR"/systemd/* /etc/systemd/system/
systemctl daemon-reload
systemctl enable plataforma-web plataforma-trabajador plataforma-respaldo.timer plataforma-retencion.timer plataforma-sellos.timer
systemctl start plataforma-respaldo.timer plataforma-retencion.timer plataforma-sellos.timer

# Recarga Nginx cuando certbot renueva el certificado.
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
printf '#!/bin/sh\nsystemctl reload nginx\n' > /etc/letsencrypt/renewal-hooks/deploy/recargar-nginx.sh
chmod +x /etc/letsencrypt/renewal-hooks/deploy/recargar-nginx.sh
