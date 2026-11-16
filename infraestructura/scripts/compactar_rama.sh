#!/usr/bin/env bash
# Deja la rama actual en un solo commit sobre la última versión de desarrollo,
# lista para su Pull Request (funcionalidad 045, etapa 3).
#
# Por qué: en una rama de trabajo conviene guardar seguido (la sesión del
# agente puede cortarse), pero a desarrollo tiene que llegar un cambio por
# funcionalidad, sin commits mínimos ni merges de sincronización. La
# integración continua rechaza los Pull Requests que no cumplen esa regla.
#
# Qué hace:
#   1. trae desarrollo y rebasa la rama sobre él (si hay conflictos, se
#      detiene y no cambia nada);
#   2. junta todos los commits de la rama en uno, con el mensaje que se le
#      pasa y las líneas Co-Authored-By de los commits originales;
#   3. con --subir, sube la rama con --force-with-lease (solo pisa la rama si
#      nadie subió nada nuevo).
# Nunca toca main ni desarrollo.
#
# Uso:
#   infraestructura/scripts/compactar_rama.sh archivo-con-el-mensaje [--subir]
set -euo pipefail

REMOTO="${REMOTO:-origin}"
BASE="${BASE:-desarrollo}"
mensaje="${1:-}"
subir=0
[ "${2:-}" = "--subir" ] && subir=1

if [ -z "$mensaje" ] || [ ! -f "$mensaje" ]; then
  echo "Uso: $0 archivo-con-el-mensaje [--subir]" >&2
  exit 2
fi
rama=$(git rev-parse --abbrev-ref HEAD)
case "$rama" in
  main | "$BASE" | HEAD) echo "No se compacta $rama." >&2; exit 2 ;;
esac
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Hay cambios sin guardar: hacé commit o descartalos antes de compactar." >&2
  exit 2
fi

git fetch --quiet "$REMOTO" "$BASE"
if ! git rebase --quiet "$REMOTO/$BASE"; then
  git rebase --abort
  echo "El rebase sobre $BASE tiene conflictos: resolvelos con 'git rebase $REMOTO/$BASE' y volvé a correr el script." >&2
  exit 1
fi

cantidad=$(git rev-list --count "$REMOTO/$BASE..HEAD")
if [ "$cantidad" -eq 0 ]; then
  echo "La rama no tiene cambios respecto de $BASE."
  exit 0
fi

coautores=$(git log --format='%(trailers:key=Co-Authored-By,valueonly)' "$REMOTO/$BASE..HEAD" \
  | sed '/^$/d' | sort -u | sed 's/^/Co-Authored-By: /')
cuerpo=$(mktemp)
trap 'rm -f "$cuerpo"' EXIT
{
  sed '/^Co-Authored-By:/d' "$mensaje"
  if [ -n "$coautores" ]; then
    printf '\n%s\n' "$coautores"
  fi
} > "$cuerpo"

git reset --quiet --soft "$REMOTO/$BASE"
git commit --quiet -F "$cuerpo"
echo "Listo: $cantidad commits compactados en uno sobre $REMOTO/$BASE."

if [ "$subir" -eq 1 ]; then
  git push --force-with-lease "$REMOTO" "$rama"
fi
