#!/bin/bash
# Despliega una versión de la plataforma (funcionalidad 017, CP-06).
#
# Uso: desplegar.sh <artefacto.tar.gz> <version>
# Lo ejecuta GitHub Actions por Systems Manager. Instala la versión en una
# carpeta nueva, migra la base, cambia el enlace "actual" y verifica la salud;
# si la verificación falla, vuelve a la versión anterior.
set -euo pipefail
ARTEFACTO=$1
VERSION=$2
BASE=/opt/plataforma
DESTINO=$BASE/versiones/$VERSION

echo "== Instalando la versión $VERSION"
rm -rf "$DESTINO"
mkdir -p "$DESTINO"
tar -xzf "$ARTEFACTO" -C "$DESTINO"
python3 -m venv "$DESTINO/venv"
"$DESTINO/venv/bin/pip" install -q --upgrade pip
"$DESTINO/venv/bin/pip" install -q -r "$DESTINO/backend/requirements.txt"
chown -R plataforma:plataforma "$DESTINO"

echo "== Configuración del servidor de esta versión"
rm -rf "$BASE/servidor"
mkdir -p "$BASE/servidor"
cp -r "$DESTINO/infraestructura/nginx" "$DESTINO/infraestructura/systemd" "$DESTINO/infraestructura/scripts" "$BASE/servidor/"
bash "$BASE/servidor/scripts/generar_entorno.sh"
bash "$BASE/servidor/scripts/instalar_configuracion.sh"

echo "== Migraciones de la base de datos"
cd "$DESTINO/backend"
sudo -u plataforma bash -c "set -a; source $BASE/.env; set +a; $DESTINO/venv/bin/flask --app wsgi db upgrade"

ANTERIOR=$(readlink -f "$BASE/actual" 2>/dev/null || true)
ln -sfn "$DESTINO" "$BASE/actual"
systemctl restart plataforma-web plataforma-trabajador

echo "== Verificación de salud"
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/api/salud >/dev/null; then
    echo "Versión $VERSION desplegada."
    # Se conservan las tres versiones más recientes para volver atrás.
    ls -1dt "$BASE"/versiones/*/ | tail -n +4 | xargs -r rm -rf
    exit 0
  fi
  sleep 2
done

echo "ERROR: la versión $VERSION no respondió; se vuelve a la anterior." >&2
journalctl -u plataforma-web -n 50 --no-pager >&2 || true
if [ -n "$ANTERIOR" ] && [ "$ANTERIOR" != "$DESTINO" ]; then
  ln -sfn "$ANTERIOR" "$BASE/actual"
  systemctl restart plataforma-web plataforma-trabajador
fi
exit 1
