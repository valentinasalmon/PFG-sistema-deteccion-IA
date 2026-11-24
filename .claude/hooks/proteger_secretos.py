#!/usr/bin/env python3
"""Gancho del arnés: impide que el agente lea, escriba o suba archivos secretos.

Claude Code lo ejecuta antes de cada uso de Read, Edit, Write, NotebookEdit,
Grep, Glob y Bash (``PreToolUse``). Recibe por la entrada estándar el JSON de
la herramienta y, si el pedido toca un archivo secreto, sale con código 2:
Claude Code bloquea la acción y le muestra al agente el motivo.

Hace cumplir de forma automática una regla que antes era solo texto en
CLAUDE.md: «Nunca subir secretos, archivos .env, ... ni el estado de
Terraform» y «nunca compartas las claves de AWS, terraform.tfvars,
backend.hcl ni el estado de Terraform». Los archivos de ejemplo
(``.env.ejemplo``, ``terraform.tfvars.ejemplo``) sí se permiten.

Realiza: funcionalidad 036 (CA2); RNF02 (protección de secretos).
"""
import json
import re
import sys
from pathlib import PurePath

# Nombres de archivo secretos (sin los de ejemplo).
SECRETOS = (
    re.compile(r"^\.env(\.[\w-]+)?$"),
    re.compile(r"^terraform\.tfvars$"),
    re.compile(r"^backend\.hcl$"),
    re.compile(r".+\.tfstate(\.backup)?$"),
    re.compile(r".+\.(pem|key)$"),
    re.compile(r"^credentials$"),
)
PERMITIDOS = re.compile(r"\.(ejemplo|example|sample|plantilla)$")

# En un comando, un nombre secreto suelto como argumento (no dentro de una palabra).
EN_COMANDO = re.compile(
    r"(?:^|[\s'\"=<>/(])("
    r"\.env(?:\.[\w-]+)?|terraform\.tfvars|backend\.hcl|[\w.-]+\.tfstate(?:\.backup)?"
    r"|\.aws/credentials"
    r")(?=$|[\s'\";|&)<>])"
)


def es_secreto(ruta):
    """True si el nombre del archivo corresponde a un secreto y no a un ejemplo."""
    if not ruta:
        return False
    nombre = PurePath(ruta).name
    if PERMITIDOS.search(nombre):
        return False
    return any(patron.match(nombre) for patron in SECRETOS)


# Texto que no se ejecuta como ruta: cuerpos de heredoc y mensajes ``-m "..."``.
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$)", re.S)
MENSAJE = re.compile(r"(?:-m|--message)(?:\s+|=)(\"(?:[^\"\\]|\\.)*\"|'[^']*')")


def _sin_textos(comando):
    """El comando sin los cuerpos de heredoc ni los mensajes de commit.

    Ajuste aprobado por la autora el 2026-11-24 (propuesta del 2026-11-02):
    antes, la excepción para los mensajes solo valía si el comando empezaba
    con ``git commit``, y bloqueaba commits encadenados o documentos escritos
    con un heredoc que solo nombraban un archivo secreto. El destino de una
    escritura (``cat > secreto <<EOF``) queda fuera del cuerpo y se sigue
    bloqueando.
    """
    return MENSAJE.sub("-m ''", HEREDOC.sub("<<EOF", comando or ""))


def secreto_en_comando(comando):
    """Primer nombre secreto que aparece como argumento del comando, o None.

    No revisa el texto de los mensajes de commit ni de los heredocs, que
    pueden nombrar estos archivos sin abrirlos.
    """
    for coincidencia in EN_COMANDO.finditer(_sin_textos(comando)):
        nombre = coincidencia.group(1)
        if not PERMITIDOS.search(nombre):
            return nombre
    return None


def motivo(pedido):
    """Explicación del bloqueo, o None si el pedido no toca secretos."""
    entrada = pedido.get("tool_input") or {}
    herramienta = pedido.get("tool_name", "")
    if herramienta == "Bash":
        nombre = secreto_en_comando(entrada.get("command", ""))
    else:
        rutas = [entrada.get(clave) for clave in ("file_path", "notebook_path", "path")]
        nombre = next((PurePath(r).name for r in rutas if es_secreto(r)), None)
    if nombre is None:
        return None
    return (
        f"Bloqueado por el arnés del proyecto: «{nombre}» es un archivo secreto "
        "(CLAUDE.md: nunca leer, subir ni compartir .env, terraform.tfvars, "
        "backend.hcl ni el estado de Terraform). Si hace falta un valor, pedíselo "
        "a la autora para que lo cargue ella, o usá el archivo de ejemplo."
    )


def main():
    """Lee el pedido de Claude Code y bloquea (código 2) si toca un secreto."""
    try:
        pedido = json.load(sys.stdin)
    except ValueError:
        return 0
    razon = motivo(pedido)
    if razon:
        print(razon, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
