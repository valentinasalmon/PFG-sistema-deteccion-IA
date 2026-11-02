#!/usr/bin/env python3
"""Gancho del arnés: revisa el estilo del archivo que el agente acaba de editar.

Claude Code lo ejecuta después de cada Edit o Write (``PostToolUse``). Si el
archivo es Python del backend corre flake8, y si es JavaScript del frontend
corre ESLint, con la configuración del proyecto. Si hay errores sale con
código 2: Claude Code le muestra los errores al agente, que los corrige en el
momento, en lugar de enterarse recién en la integración continua.

Si la herramienta no está instalada en la máquina (por ejemplo, sin el
entorno virtual del backend), no hace nada: el control definitivo sigue
siendo la integración continua.

Realiza: funcionalidad 036 (CA3); RNF17 (calidad del código).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BACKEND = RAIZ / "backend"
FRONTEND = RAIZ / "frontend"
TIEMPO_MAXIMO = 60


def _primero_que_exista(*candidatos):
    """La primera ruta ejecutable que existe, o None."""
    for candidato in candidatos:
        if candidato and Path(candidato).is_file():
            return str(candidato)
    return None


def comando_para(ruta):
    """``(comando, carpeta)`` para revisar el archivo, o None si no corresponde."""
    try:
        relativa = ruta.resolve().relative_to(RAIZ)
    except ValueError:
        return None
    partes = relativa.parts
    if partes[:1] == ("backend",) and ruta.suffix == ".py":
        flake8 = _primero_que_exista(BACKEND / ".venv" / "bin" / "flake8", shutil.which("flake8"))
        return ([flake8, str(ruta)], BACKEND) if flake8 else None
    if partes[:2] == ("frontend", "src") and ruta.suffix in (".js", ".jsx"):
        eslint = _primero_que_exista(FRONTEND / "node_modules" / ".bin" / "eslint")
        return ([eslint, "--no-warn-ignored", str(ruta)], FRONTEND) if eslint else None
    return None


def main():
    """Revisa el archivo editado y devuelve los errores al agente (código 2)."""
    try:
        pedido = json.load(sys.stdin)
    except ValueError:
        return 0
    entrada = pedido.get("tool_input") or {}
    respuesta = pedido.get("tool_response") or {}
    archivo = entrada.get("file_path") or respuesta.get("filePath")
    if not archivo:
        return 0
    revision = comando_para(Path(archivo))
    if revision is None:
        return 0
    comando, carpeta = revision
    try:
        resultado = subprocess.run(
            comando, cwd=carpeta, capture_output=True, text=True, timeout=TIEMPO_MAXIMO,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 0
    if resultado.returncode == 0:
        return 0
    salida = (resultado.stdout + resultado.stderr).strip()
    print(
        f"El arnés revisó {Path(archivo).name} y encontró problemas de estilo; "
        f"corregilos antes de seguir:\n{salida}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
