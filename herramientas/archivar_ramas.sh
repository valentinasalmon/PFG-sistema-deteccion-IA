#!/bin/bash
# Archiva como etiqueta cada rama ya integrada en main y la borra de GitHub (ADR-0023).
#
# Por qué: con GitHub Flow, la lista de ramas muestra solo el trabajo en curso.
# Las ramas viejas no se pierden: cada una queda como etiqueta
# archivo/<área>/<nombre> en el mismo commit (se consulta con
# `git switch --detach archivo/...`), y su Pull Request sigue en GitHub.
#
# Uso, desde la raíz del repositorio y con main al día:
#   bash herramientas/archivar_ramas.sh            # muestra qué haría, sin cambiar nada
#   bash herramientas/archivar_ramas.sh --aplicar  # crea las etiquetas y borra las ramas
#
# Solo revisa las ramas del modelo anterior (funcionalidad/, correccion/,
# documentacion/, recursos/ y desarrollo). Nunca toca main, las ramas nuevas
# por área (interfaz/, hedera/...; GitHub las borra solo al integrarlas), las de
# otras sesiones del agente (claude/) ni las que tienen commits que no están en
# main (trabajo sin integrar, como las de la red neuronal).
set -euo pipefail

APLICAR=0
[ "${1:-}" = "--aplicar" ] && APLICAR=1

git fetch --prune --quiet origin

# Área de cada rama vieja según su nombre (ver docs/guias/mapa-de-ramas.md).
area_de() {
  case "$1" in
    *012-capa-4*) echo red-neuronal ;;
    *016*|*023*|*026*|*029*|*hedera*|*sello*) echo hedera ;;
    *017*|*030*|*040*|*integracion-continua*|infraestructura/*) echo infraestructura ;;
    *027*|*031*|*032*|*035*|integraciones/*) echo integraciones ;;
    *018*|*036*|*042*|*decisiones*|documentacion/*) echo documentacion ;;
    *022*|*028*|*033*|*034*|*037*|*038*|*039*|*041*|*043*|*044*|*marca*|interfaz/*) echo interfaz ;;
    desarrollo) echo integracion ;;
    *) echo plataforma ;;
  esac
}

for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin); do
  rama=${ref#origin/}
  case "$rama" in
    desarrollo|funcionalidad/*|correccion/*|documentacion/*|recursos/*) ;;
    *) continue ;;
  esac
  # Solo las ramas cuyo trabajo ya está en main (por contenido, también tras un squash).
  if git cherry origin/main "$ref" | grep -q '^+'; then
    echo "conservo (tiene trabajo sin integrar): $rama"
    continue
  fi
  nombre=${rama#*/}
  case "$rama" in correccion/*|documentacion/*|recursos/*) nombre=${rama//\//-} ;; esac
  etiqueta="archivo/$(area_de "$rama")/$nombre"
  if [ "$APLICAR" = 1 ]; then
    git tag -f "$etiqueta" "$ref" >/dev/null
    git push --quiet origin "refs/tags/$etiqueta"
    git push --quiet origin --delete "$rama"
    echo "archivada: $rama -> $etiqueta"
  else
    echo "archivaría: $rama -> $etiqueta"
  fi
done
