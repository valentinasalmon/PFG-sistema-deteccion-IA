# Instalación del entorno de desarrollo en Windows

Guía paso a paso para preparar una computadora con Windows 10 (versión 22H2) o Windows 11. El backend se desarrolla dentro de **WSL2 con Ubuntu** ([ADR-0009](../arquitectura/decisiones/0009-desarrollo-en-wsl2.md)), porque varias herramientas del proyecto (Gunicorn, el trabajador de RQ, WeasyPrint y ExifTool) funcionan de forma nativa en Linux y el servidor de producción también es Linux.

> **Convención de esta guía**
> - Los bloques marcados **PowerShell (administrador)** se ejecutan en Windows: menú Inicio → escribir "PowerShell" → clic derecho → *Ejecutar como administrador*.
> - Los bloques marcados **Ubuntu** se ejecutan en la terminal de Ubuntu (WSL).

---

## Paso 1 — Instalar WSL2 con Ubuntu

**Qué es**: WSL (*Windows Subsystem for Linux*) permite ejecutar Linux dentro de Windows sin máquina virtual tradicional.

**PowerShell (administrador)**:

```powershell
wsl --install -d Ubuntu-24.04
```

1. Reiniciar la computadora cuando lo pida.
2. Al reiniciar se abre la ventana de Ubuntu: elegir un **nombre de usuario** (en minúsculas, sin espacios) y una **contraseña** (no se ve al escribirla; es normal). Esa contraseña se pide al usar `sudo`.

**Verificación (PowerShell)**:

```powershell
wsl -l -v
```

Debe mostrar `Ubuntu-24.04` con `VERSION 2`.

---

## Paso 2 — Instalar Windows Terminal (si no lo tenés)

Viene incluido en Windows 11. En Windows 10 se instala desde Microsoft Store buscando **Windows Terminal**. Permite abrir pestañas de PowerShell y de Ubuntu en la misma ventana.

---

## Paso 3 — Instalar Visual Studio Code y sus extensiones

1. Descargar e instalar desde <https://code.visualstudio.com>. En el instalador marcar:
   - *Agregar "Abrir con Code" al menú contextual*.
   - *Agregar a PATH*.
2. Abrir VS Code → ícono de extensiones (`Ctrl+Shift+X`) e instalar:

| Extensión | Identificador | Para qué |
|---|---|---|
| WSL | `ms-vscode-remote.remote-wsl` | Abrir el proyecto que vive dentro de Ubuntu (**imprescindible**) |
| Spanish Language Pack | `ms-ceintl.vscode-language-pack-es` | Interfaz en español |
| Python | `ms-python.python` | Soporte de Python |
| Pylance | `ms-python.vscode-pylance` | Autocompletado y análisis de tipos |
| Flake8 | `ms-python.flake8` | Marca errores de estilo mientras se escribe |
| Pylint | `ms-python.pylint` | Análisis estático |
| ESLint | `dbaeumer.vscode-eslint` | Análisis de JavaScript/React |
| Prettier | `esbenp.prettier-vscode` | Formato automático del frontend |
| Docker | `ms-azuretools.vscode-docker` | Ver y manejar contenedores |
| GitLens | `eamodio.gitlens` | Historial de Git dentro del editor |
| EditorConfig | `editorconfig.editorconfig` | Respeta las reglas de formato del repositorio |
| Markdown All in One | `yzhang.markdown-all-in-one` | Edición de la documentación |
| Excalidraw | `pomdtr.excalidraw-editor` | Abrir y editar los diagramas `.excalidraw` |

> Las extensiones de Python, ESLint y similares se instalan **también del lado de WSL**: cuando el proyecto esté abierto en WSL (paso 9), VS Code ofrece "Instalar en WSL: Ubuntu"; aceptar.

---

## Paso 4 — Instalar Docker Desktop

**Qué es**: ejecuta en contenedores los servicios que el sistema necesita en desarrollo (PostgreSQL, Redis, un S3 local y un servidor de correo de prueba), sin instalarlos en la computadora.

1. Descargar desde <https://www.docker.com/products/docker-desktop/> e instalar con la opción **Use WSL 2 instead of Hyper-V**.
2. Abrir Docker Desktop → *Settings* → *Resources* → *WSL integration* → activar **Ubuntu-24.04** → *Apply & restart*.

**Verificación (Ubuntu)**:

```bash
docker --version
docker run --rm hello-world
```

Debe imprimir *Hello from Docker!*.

---

## Opción automática para los pasos 5 a 7

El script [`infraestructura/scripts/preparar_entorno_wsl.sh`](../../infraestructura/scripts/preparar_entorno_wsl.sh) realiza los pasos 5, 6 y 7 de forma automática:

- Instala solo los paquetes que faltan (no desinstala ni borra nada).
- Agrega el usuario al grupo `docker`.
- Instala nvm y la versión LTS de Node.js.
- Configura Git sin sobrescribir valores existentes (pide nombre y correo si faltan).
- Verifica cada herramienta y muestra un resumen.
- Guarda todo lo realizado en `~/preparar_entorno.log`.

Se ejecuta desde Ubuntu, **sin** `sudo` (el script pide la contraseña cuando la necesita):

```bash
bash ~/preparar_entorno_wsl.sh
```

Al terminar quedan dos pasos manuales que el script indica: `gh auth login` y, si hizo falta agregar el grupo `docker`, `wsl --shutdown` desde PowerShell.

Probado en Ubuntu 24.04 limpio: primera ejecución completa sin errores y segunda ejecución sin cambios (idempotente).

## Paso 5 — Preparar Ubuntu: herramientas del sistema

**Ubuntu**:

```bash
# Actualizar la lista de paquetes y el sistema
sudo apt update && sudo apt upgrade -y

# Herramientas de compilación, Git y utilidades
sudo apt install -y build-essential git curl unzip ca-certificates

# Python 3.12 (incluido en Ubuntu 24.04), entornos virtuales y pip
sudo apt install -y python3 python3-venv python3-pip python3-dev

# ExifTool (capa 1 de análisis)
sudo apt install -y libimage-exiftool-perl

# Bibliotecas que necesita WeasyPrint para generar el PDF
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu

# Cliente de PostgreSQL (para consultar la base desde la terminal)
sudo apt install -y postgresql-client
```

**Verificación (Ubuntu)**:

```bash
python3 --version     # Python 3.12.x
exiftool -ver         # 12.x o superior
git --version
psql --version
```

---

## Paso 6 — Instalar Node.js con nvm

**Qué es**: Node.js ejecuta las herramientas del frontend (Vite, ESLint, Vitest). `nvm` permite instalar y cambiar versiones de Node sin permisos de administrador.

**Ubuntu**:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# Cerrar y volver a abrir la terminal de Ubuntu, luego:
nvm install --lts
nvm alias default 'lts/*'
```

**Verificación (Ubuntu)**:

```bash
node --version   # v24.x (versión LTS vigente)
npm --version
```

---

## Paso 7 — Configurar Git y GitHub

**Ubuntu**:

```bash
# Identidad para los commits (usar el mismo correo de la cuenta de GitHub)
git config --global user.name "Valentina Salmon"
git config --global user.email "tu-correo@ejemplo.com"

# Rama inicial por defecto y finales de línea de Linux
git config --global init.defaultBranch main
git config --global core.autocrlf input

# Editor para los mensajes de commit largos
git config --global core.editor "code --wait"
```

Instalar la CLI de GitHub para autenticarse y abrir Pull Requests desde la terminal:

```bash
sudo apt install -y gh
gh auth login
```

En `gh auth login` elegir: **GitHub.com** → **HTTPS** → **Yes** (autenticar Git) → **Login with a web browser**, y seguir las instrucciones.

**Verificación (Ubuntu)**:

```bash
gh auth status
```

---

## Paso 8 — Clonar el repositorio dentro de Ubuntu

> **Importante**: el proyecto se guarda en el disco de Ubuntu (`~/proyectos`) y **no** en `C:\` (`/mnt/c/...`). Dentro de `/mnt/c` todo funciona mucho más lento.

**Ubuntu**:

```bash
mkdir -p ~/proyectos && cd ~/proyectos
git clone https://github.com/valentinasalmon/PFG-sistema-deteccion-IA.git
cd PFG-sistema-deteccion-IA
```

---

## Paso 9 — Abrir el proyecto en VS Code

**Ubuntu** (desde la carpeta del proyecto):

```bash
code .
```

La primera vez instala un componente de VS Code dentro de Ubuntu. En la esquina inferior izquierda de VS Code debe verse **WSL: Ubuntu-24.04**. Desde ahora, la terminal integrada de VS Code (`Ctrl+ñ` o *Terminal → Nueva terminal*) ya es una terminal de Ubuntu.

---

## Paso 10 — Cuentas externas (más adelante)

No hacen falta para empezar; se crean al llegar a la funcionalidad indicada.

| Cuenta | Para qué | Funcionalidad |
|---|---|---|
| Google (Colab) o Kaggle | Entrenar la red neuronal con GPU gratuita | 010 |
| Amazon Web Services | Infraestructura de producción | 017 |
| Dominio propio | Dirección pública de la plataforma | 017 |

---

## Resumen de verificación

Ejecutar en la terminal de Ubuntu; todos deben responder con una versión:

```bash
python3 --version && node --version && npm --version && git --version \
  && docker --version && exiftool -ver && gh --version | head -1
```

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `wsl --install` dice que la virtualización está deshabilitada | Activar *Virtualization Technology* (Intel VT-x / AMD-V) en la BIOS. |
| `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` | El usuario de Ubuntu no pertenece al grupo `docker`. Ejecutar en Ubuntu `sudo groupadd docker 2>/dev/null; sudo usermod -aG docker $USER`, luego en PowerShell `wsl --shutdown`, verificar que Docker Desktop esté abierto y con la integración de Ubuntu-24.04 activada, y volver a abrir Ubuntu. Comprobar con `groups` que aparezca `docker`. |
| La terminal de Ubuntu abre en `/mnt/c/WINDOWS/system32` | Ocurre al abrir Ubuntu desde una consola de administrador. Ejecutar `cd ~` para ir a la carpeta personal de Ubuntu. |
| `docker: command not found` en Ubuntu | Verificar en Docker Desktop que la integración con Ubuntu-24.04 esté activada (paso 4). |
| `code .` no funciona | Reinstalar VS Code marcando *Agregar a PATH*, y reiniciar la terminal. |
| Los archivos aparecen todos modificados en Git | Revisar que `core.autocrlf` sea `input` (paso 7). |
