#!/usr/bin/env bash
# =============================================================================
# preparar_entorno_wsl.sh
#
# Prepara Ubuntu 24.04 (WSL2) con todas las herramientas de desarrollo del
# proyecto. Automatiza los pasos 5 a 7 de docs/guias/instalacion-entorno-windows.md.
#
# Principios del script:
#   - Idempotente: puede ejecutarse varias veces; solo instala lo que falta.
#   - No destructivo: no desinstala, no borra y no sobrescribe configuraciones
#     existentes de Git.
#   - Trazable: todo lo que hace queda en ~/preparar_entorno.log.
#
# Uso (desde la terminal de Ubuntu, como usuario normal, NO con sudo):
#   bash preparar_entorno_wsl.sh
#
# Requisitos previos: WSL2 con Ubuntu 24.04 y Docker Desktop con la integración
# de WSL activada (pasos 1 a 4 de la guía).
#
# Relacionado: ADR-0009 (desarrollo en WSL2), RNF22.
# =============================================================================

set -euo pipefail

ARCHIVO_REGISTRO="${HOME}/preparar_entorno.log"
VERSION_NVM="v0.40.1"

# Paquetes del sistema agrupados por propósito (se instalan solo si faltan).
PAQUETES_BASE=(build-essential git curl unzip ca-certificates)
PAQUETES_PYTHON=(python3 python3-venv python3-pip python3-dev)
PAQUETES_ANALISIS=(libimage-exiftool-perl)
PAQUETES_PDF=(libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu)
PAQUETES_HERRAMIENTAS=(postgresql-client gh)

# -----------------------------------------------------------------------------
# Funciones auxiliares de salida
# -----------------------------------------------------------------------------

titulo() {
    # Imprime el encabezado de una etapa.
    printf '\n\033[1;34m==> %s\033[0m\n' "$1"
}

ok() {
    # Informa una acción completada.
    printf '\033[0;32m  [OK]\033[0m %s\n' "$1"
}

aviso() {
    # Informa algo que requiere atención pero no detiene el script.
    printf '\033[0;33m  [AVISO]\033[0m %s\n' "$1"
}

# -----------------------------------------------------------------------------
# Etapa 0: comprobaciones previas
# -----------------------------------------------------------------------------

comprobar_entorno() {
    # Verifica que el script corre en Ubuntu, sin sudo y con conexión.
    titulo "Comprobando el entorno"

    if [[ "${EUID}" -eq 0 && "${PERMITIR_ROOT:-0}" != "1" ]]; then
        echo "Ejecutá el script como usuario normal (sin sudo). Él mismo pide la contraseña cuando la necesita."
        exit 1
    fi

    if ! grep -qi "ubuntu" /etc/os-release; then
        echo "Este script está pensado para Ubuntu. Sistema detectado:"
        grep PRETTY_NAME /etc/os-release
        exit 1
    fi
    ok "Sistema: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"

    if grep -qi microsoft /proc/version 2>/dev/null; then
        ok "Ejecutando dentro de WSL"
    else
        aviso "No parece WSL; el script continúa igual."
    fi

    if ! curl -sS --max-time 10 -o /dev/null https://github.com; then
        echo "No hay conexión a Internet (no se pudo acceder a github.com)."
        exit 1
    fi
    ok "Conexión a Internet disponible"

    # Pide la contraseña de sudo una sola vez al inicio.
    sudo -v
    ok "Permisos de administrador confirmados"
}

# -----------------------------------------------------------------------------
# Etapa 1: paquetes del sistema
# -----------------------------------------------------------------------------

instalar_paquetes() {
    # Actualiza el sistema e instala solo los paquetes que no estén presentes.
    titulo "Actualizando Ubuntu (puede tardar varios minutos)"
    sudo apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
    ok "Sistema actualizado"

    titulo "Instalando paquetes del sistema"
    local todos=("${PAQUETES_BASE[@]}" "${PAQUETES_PYTHON[@]}" "${PAQUETES_ANALISIS[@]}"
                 "${PAQUETES_PDF[@]}" "${PAQUETES_HERRAMIENTAS[@]}")
    local faltantes=()
    for paquete in "${todos[@]}"; do
        if dpkg -s "${paquete}" > /dev/null 2>&1; then
            ok "${paquete} ya estaba instalado"
        else
            faltantes+=("${paquete}")
        fi
    done

    if [[ ${#faltantes[@]} -gt 0 ]]; then
        echo "  Instalando: ${faltantes[*]}"
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "${faltantes[@]}"
        ok "Paquetes instalados: ${faltantes[*]}"
    fi
}

# -----------------------------------------------------------------------------
# Etapa 2: permisos de Docker
# -----------------------------------------------------------------------------

configurar_docker() {
    # Agrega el usuario al grupo docker para usar Docker sin sudo.
    titulo "Configurando permisos de Docker"
    if ! getent group docker > /dev/null; then
        sudo groupadd docker
        ok "Grupo docker creado"
    fi

    if id -nG "${USER}" | grep -qw docker; then
        ok "${USER} ya pertenece al grupo docker"
    else
        sudo usermod -aG docker "${USER}"
        ok "${USER} agregado al grupo docker (se aplica tras reiniciar WSL)"
        REQUIERE_REINICIO=1
    fi
}

# -----------------------------------------------------------------------------
# Etapa 3: Node.js con nvm
# -----------------------------------------------------------------------------

instalar_node() {
    # Instala nvm (si falta) y la versión LTS vigente de Node.js.
    titulo "Instalando Node.js (versión LTS) con nvm"
    export NVM_DIR="${HOME}/.nvm"

    if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
        ok "nvm ya estaba instalado"
    else
        curl -fsSo- "https://raw.githubusercontent.com/nvm-sh/nvm/${VERSION_NVM}/install.sh" | bash
        ok "nvm ${VERSION_NVM} instalado"
    fi

    # nvm no es compatible con 'set -u'; se desactiva solo durante su uso.
    set +u
    # shellcheck source=/dev/null
    . "${NVM_DIR}/nvm.sh" || true  # devuelve 3 si aún no hay versión de Node
    nvm install --lts
    nvm alias default 'lts/*'
    set -u
    ok "Node.js $(node --version) y npm $(npm --version)"
}

# -----------------------------------------------------------------------------
# Etapa 4: configuración de Git
# -----------------------------------------------------------------------------

configurar_git_valor() {
    # Define una opción global de Git solo si todavía no tiene valor.
    local clave="$1" valor="$2"
    if git config --global --get "${clave}" > /dev/null; then
        ok "git ${clave} ya configurado: $(git config --global --get "${clave}")"
    else
        git config --global "${clave}" "${valor}"
        ok "git ${clave} = ${valor}"
    fi
}

configurar_git() {
    # Configura la identidad y las preferencias de Git sin pisar lo existente.
    titulo "Configurando Git"

    if ! git config --global --get user.name > /dev/null; then
        read -r -p "  Tu nombre para los commits (ej. Valentina Salmon): " nombre
        git config --global user.name "${nombre}"
    fi
    if ! git config --global --get user.email > /dev/null; then
        read -r -p "  Tu correo de GitHub: " correo
        git config --global user.email "${correo}"
    fi
    ok "Identidad: $(git config --global user.name) <$(git config --global user.email)>"

    configurar_git_valor init.defaultBranch main
    configurar_git_valor core.autocrlf input
    configurar_git_valor core.editor "code --wait"
}

# -----------------------------------------------------------------------------
# Etapa 5: verificación final
# -----------------------------------------------------------------------------

verificar() {
    # Muestra una tabla con el estado de cada herramienta.
    titulo "Verificación final"
    local fallos=0

    comprobar() {
        local nombre="$1"; shift
        local version
        if version="$("$@" 2>/dev/null | head -n 1)" && [[ -n "${version}" ]]; then
            printf '  \033[0;32m✔\033[0m %-12s %s\n' "${nombre}" "${version}"
        else
            printf '  \033[0;31m✘\033[0m %-12s no disponible\n' "${nombre}"
            fallos=$((fallos + 1))
        fi
    }

    comprobar "Python" python3 --version
    comprobar "pip" python3 -m pip --version
    comprobar "Node.js" node --version
    comprobar "npm" npm --version
    comprobar "Git" git --version
    comprobar "ExifTool" exiftool -ver
    comprobar "psql" psql --version
    comprobar "GitHub CLI" gh --version
    comprobar "Docker" docker --version

    echo
    if docker info > /dev/null 2>&1; then
        ok "Docker responde sin sudo"
    else
        aviso "Docker todavía no responde sin sudo: hacé el paso 'wsl --shutdown' indicado abajo."
    fi

    if gh auth status > /dev/null 2>&1; then
        ok "GitHub CLI autenticado"
    else
        aviso "GitHub CLI sin autenticar: ejecutá 'gh auth login' (ver pasos finales)."
    fi

    return "${fallos}"
}

# -----------------------------------------------------------------------------
# Programa principal
# -----------------------------------------------------------------------------

main() {
    REQUIERE_REINICIO=0
    comprobar_entorno
    instalar_paquetes
    configurar_docker
    instalar_node
    configurar_git

    local resultado=0
    verificar || resultado=$?

    titulo "Pasos finales (manuales)"
    echo "  1. Autenticarse en GitHub:   gh auth login"
    echo "     Elegir: GitHub.com → HTTPS → Yes → Login with a web browser"
    if [[ "${REQUIERE_REINICIO}" -eq 1 ]] || ! docker info > /dev/null 2>&1; then
        echo "  2. Cerrar Ubuntu y en PowerShell ejecutar:   wsl --shutdown"
        echo "     Volver a abrir Ubuntu y probar:   docker run --rm hello-world"
    fi
    echo
    echo "  Registro completo de esta ejecución: ${ARCHIVO_REGISTRO}"

    if [[ "${resultado}" -gt 0 ]]; then
        aviso "${resultado} herramienta(s) no quedaron disponibles; revisá el registro."
        exit 1
    fi
    ok "Entorno listo"
}

# Toda la salida se muestra en pantalla y se guarda en el archivo de registro.
main 2>&1 | tee "${ARCHIVO_REGISTRO}"
