#!/usr/bin/env python3
"""Gancho del arnés: revisa el mensaje de cada commit del agente antes de crearlo.

Claude Code lo ejecuta antes de cada uso de Bash (``PreToolUse``). Si el comando
es un ``git commit`` con el mensaje en ``-m`` o en un *heredoc* (``-F -``),
bloquea el commit (código 2) cuando:

- el título no sigue ``tipo(ámbito): descripción`` con los tipos en español;
- el título pasa de 72 caracteres (la integración continua lo rechaza igual,
  pero tarde: ya con el Pull Request abierto, como pasó en el PR #93);
- falta la línea ``Co-Authored-By`` que identifica la asistencia de IA.

Realiza: regla de commits de CLAUDE.md (pedido de la autora, 2026-11-16);
RNF20 (Conventional Commits).
"""
import json
import re
import sys

TIPOS = (
    "funcionalidad", "correccion", "documentacion", "estilo", "refactorizacion",
    "rendimiento", "pruebas", "construccion", "integracion", "tarea", "revertir",
)
TITULO = re.compile(r"^(" + "|".join(TIPOS) + r")(\([^)]+\))?!?: \S")
LARGO_MAXIMO = 72
HEREDOC = re.compile(r"<<-?\s*'?\"?(\w+)'?\"?\n(.*?)\n\1", re.S)
OPCION_M = re.compile(r"""\s-m\s+(?:"((?:[^"\\]|\\.)*)"|'([^']*)')""")


# ``git commit`` como comando (al principio o después de &&, ;, || o |), no como
# texto dentro de un archivo que se está escribiendo.
COMANDO_COMMIT = re.compile(r"(?:^|&&|;|\|\|?)\s*git\s+commit\b[^\n]*", re.M)


def mensaje_del_comando(comando):
    """Devuelve el mensaje del ``git commit`` del comando, o None si no hay uno real."""
    # Los cuerpos de los heredoc son texto, no comandos: se quitan antes de buscar.
    sin_heredocs = HEREDOC.sub("", comando)
    linea = COMANDO_COMMIT.search(sin_heredocs)
    if linea is None or "--no-edit" in linea.group(0):
        return None
    if re.search(r"-F\s*-", linea.group(0)):
        heredoc = HEREDOC.search(comando[comando.find(linea.group(0).strip()):])
        return heredoc.group(2) if heredoc else None
    opcion = OPCION_M.search(linea.group(0))
    if opcion:
        return opcion.group(1) if opcion.group(1) is not None else opcion.group(2)
    return None


def problemas(mensaje):
    """Lista los problemas del mensaje de commit (vacía si está bien)."""
    lineas = mensaje.strip().splitlines()
    titulo = lineas[0].strip() if lineas else ""
    encontrados = []
    if not TITULO.match(titulo):
        encontrados.append(
            "el título no sigue «tipo(ámbito): descripción» con un tipo en español "
            f"({', '.join(TIPOS)})"
        )
    if len(titulo) > LARGO_MAXIMO:
        encontrados.append(
            f"el título tiene {len(titulo)} caracteres; el máximo es {LARGO_MAXIMO}"
        )
    if "Co-Authored-By:" not in mensaje:
        encontrados.append("falta la línea Co-Authored-By de la asistencia de IA")
    return encontrados


def main():
    """Lee el pedido de la herramienta y bloquea el commit si el mensaje no cumple."""
    try:
        pedido = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if pedido.get("tool_name") != "Bash":
        return 0
    mensaje = mensaje_del_comando(pedido.get("tool_input", {}).get("command", ""))
    if mensaje is None:
        return 0
    encontrados = problemas(mensaje)
    if not encontrados:
        return 0
    print(
        "Bloqueado por el arnés del proyecto (regla de commits de CLAUDE.md): "
        + "; ".join(encontrados) + ". Corregí el mensaje y volvé a intentar.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
