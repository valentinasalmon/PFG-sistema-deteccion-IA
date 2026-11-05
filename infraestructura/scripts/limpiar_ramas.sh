#!/usr/bin/env bash
# Limpieza de ramas remotas en desuso (funcionalidad 039).
#
# Clasifica cada rama del remoto contra `desarrollo`:
#   - INTEGRADA: no tiene commits que no estén en desarrollo -> se borra.
#   - SUPERADA: sus commits ya están en desarrollo por otra vía (mismo cambio,
#     otro commit, según `git cherry`) -> se borra.
#   - CON CONTENIDO PROPIO: tiene cambios que no están en desarrollo -> no se
#     borra, salvo con --archivar: primero se guarda en la etiqueta
#     `archivo/<rama>` y después se borra.
# Nunca toca `main` ni `desarrollo`, ni las ramas con actividad reciente
# (trabajo en curso de la autora o de otra sesión del agente): un día para las
# integradas (DIAS_INTEGRADA) y tres para las que no lo están (DIAS_ACTIVA).
#
# Uso:
#   infraestructura/scripts/limpiar_ramas.sh             # solo muestra qué haría
#   infraestructura/scripts/limpiar_ramas.sh --aplicar   # borra integradas y superadas
#   infraestructura/scripts/limpiar_ramas.sh --aplicar --archivar  # y archiva el resto
#
# Variables: REMOTO (origin), BASE (desarrollo), DIAS_ACTIVA (3), DIAS_INTEGRADA (1),
# CONSERVAR (lista de ramas extra que no se tocan, separadas por espacios).
set -euo pipefail

REMOTO="${REMOTO:-origin}"
BASE="${BASE:-desarrollo}"
DIAS_ACTIVA="${DIAS_ACTIVA:-3}"
DIAS_INTEGRADA="${DIAS_INTEGRADA:-1}"
CONSERVAR="main ${BASE} ${CONSERVAR:-}"
APLICAR=0
ARCHIVAR=0
for argumento in "$@"; do
  case "$argumento" in
    --aplicar) APLICAR=1 ;;
    --archivar) ARCHIVAR=1 ;;
    *) echo "Argumento desconocido: $argumento" >&2; exit 2 ;;
  esac
done

git fetch --quiet --prune "$REMOTO"
limite_activa=$(date -d "-${DIAS_ACTIVA} days" +%s)
limite_integrada=$(date -d "-${DIAS_INTEGRADA} days" +%s)
borrar=()
archivar=()

while read -r referencia; do
  rama="${referencia#"$REMOTO"/}"
  case " $CONSERVAR " in *" $rama "*) continue ;; esac
  ultima=$(git log -1 --format=%ct "$referencia")
  propios=$(git rev-list --count "$REMOTO/$BASE..$referencia")
  if { [ "$propios" -eq 0 ] && [ "$ultima" -ge "$limite_integrada" ]; } \
      || { [ "$propios" -gt 0 ] && [ "$ultima" -ge "$limite_activa" ]; }; then
    echo "ACTIVA        $rama (se conserva: tiene actividad reciente)"
    continue
  fi
  if [ "$propios" -eq 0 ]; then
    echo "INTEGRADA     $rama"
    borrar+=("$rama")
  elif ! git cherry "$REMOTO/$BASE" "$referencia" | grep -q '^+'; then
    echo "SUPERADA      $rama (sus cambios ya están en $BASE por otra vía)"
    borrar+=("$rama")
  elif mapfile -t cambiados < <(git diff --name-only "$REMOTO/$BASE...$referencia") \
      && git diff --quiet "$REMOTO/$BASE" "$referencia" -- "${cambiados[@]}"; then
    echo "SUPERADA      $rama (los archivos que cambió ya están iguales en $BASE)"
    borrar+=("$rama")
  else
    echo "PROPIA        $rama ($propios commits que no están en $BASE)"
    archivar+=("$rama")
  fi
done < <(git for-each-ref --format='%(refname:short)' "refs/remotes/$REMOTO" | grep -v "^$REMOTO/HEAD$" | grep -v "^$REMOTO$")

echo
echo "Para borrar: ${#borrar[@]}. Con contenido propio: ${#archivar[@]}."
if [ "$APLICAR" -eq 0 ]; then
  echo "Simulación: no se borró nada. Agregá --aplicar para borrar (y --archivar para las propias)."
  exit 0
fi

if [ "$ARCHIVAR" -eq 1 ]; then
  for rama in "${archivar[@]}"; do
    etiqueta="archivo/${rama//\//-}"
    git tag -a "$etiqueta" "$REMOTO/$rama" -m "Archivo de la rama $rama, borrada el $(date +%F) por limpiar_ramas.sh."
    git push "$REMOTO" "refs/tags/$etiqueta"
    borrar+=("$rama")
  done
fi

if [ "${#borrar[@]}" -gt 0 ]; then
  git push "$REMOTO" --delete "${borrar[@]}"
fi
echo "Listo. Ramas restantes en $REMOTO: $(git ls-remote --heads "$REMOTO" | wc -l)."
