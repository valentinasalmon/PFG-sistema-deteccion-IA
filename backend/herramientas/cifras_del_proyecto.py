"""Cifras del proyecto calculadas desde el repositorio (funcionalidad 037).

El informe cita números del proceso (commits, coautoría de IA, pull requests,
pruebas, especificaciones, decisiones de arquitectura). Escritos a mano, se
desactualizan en días. Esta herramienta los cuenta desde git y desde los
archivos, con la fecha del cálculo, para que el texto siempre diga lo mismo
que el repositorio.

Uso, desde la raíz del repositorio o desde ``backend/``::

    python backend/herramientas/cifras_del_proyecto.py [--json]

Realiza: RNF19 (trazabilidad del proceso); funcionalidad 037.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def git(*argumentos):
    """Ejecuta git en la raíz del repositorio y devuelve la salida."""
    resultado = subprocess.run(["git", *argumentos], cwd=RAIZ, capture_output=True,
                               text=True, check=True)
    return resultado.stdout


def contar_commits():
    """Commits sin contar las integraciones, y cuántos llevan coautoría de IA."""
    mensajes = git("log", "--no-merges", "--format=%H%x00%B%x01").split("\x01")
    mensajes = [m for m in mensajes if m.strip()]
    patron = re.compile(r"Co-Authored-By:.*(Claude|anthropic)", re.IGNORECASE)
    con_ia = sum(1 for m in mensajes if patron.search(m))
    return len(mensajes), con_ia


def contar_pull_requests():
    """Pull requests integrados (commits de integración de GitHub)."""
    return len(re.findall(r"Merge pull request #\d+", git("log", "--merges", "--format=%s")))


def contar_pruebas():
    """Pruebas automáticas declaradas en el backend y en la interfaz."""
    backend = sum(len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M))
                  for p in (RAIZ / "backend" / "pruebas").rglob("test_*.py"))
    frontend = 0
    for patron in ("*.test.js", "*.test.jsx"):
        for archivo in (RAIZ / "frontend" / "src").rglob(patron):
            frontend += len(re.findall(r"^\s*(?:it|test)\(", archivo.read_text(encoding="utf-8"),
                                       re.M))
    return backend, frontend


def contar_funcionalidades():
    """Funcionalidades del plan, por estado, según docs/funcionalidades/README.md."""
    tabla = (RAIZ / "docs" / "funcionalidades" / "README.md").read_text(encoding="utf-8")
    filas = re.findall(r"^\| (\d{3}) \|.*\| ([^|]+) \|\s*$", tabla, re.M)
    estados = {}
    for _, estado in filas:
        clave = re.split(r"[ (:;,.]", estado.strip())[0].lower()
        estados[clave] = estados.get(clave, 0) + 1
    especificadas = len(list((RAIZ / "docs" / "funcionalidades").glob("*/especificacion.md")))
    return len(filas), especificadas, estados


def contar_requisitos():
    """Requisitos funcionales, no funcionales y reglas de negocio de la especificación."""
    carpeta = RAIZ / "docs" / "especificacion"
    texto = "".join(p.read_text(encoding="utf-8") for p in carpeta.glob("*.md"))
    return {
        "funcionales": len(set(re.findall(r"\bRF(\d{2})\b", texto))),
        "no_funcionales": len(set(re.findall(r"\bRNF(\d{2})\b", texto))),
        "reglas_de_negocio": len(set(re.findall(r"\bRN(\d{2})\b", texto))),
        "casos_de_uso": len(set(re.findall(r"\bCU(\d{2})\b", texto))),
        "cuestiones_abiertas": len(set(re.findall(r"\bCP-(\d{2})\b", texto))),
    }


def calcular():
    """Reúne todas las cifras con la fecha y el commit del cálculo."""
    commits, con_ia = contar_commits()
    backend, frontend = contar_pruebas()
    total, especificadas, estados = contar_funcionalidades()
    carpeta_adr = RAIZ / "docs" / "arquitectura" / "decisiones"
    return {
        "fecha": datetime.date.today().isoformat(),
        "commit": git("rev-parse", "--short", "HEAD").strip(),
        "commits": commits,
        "commits_con_ia": con_ia,
        "porcentaje_con_ia": round(100 * con_ia / commits, 1) if commits else 0,
        "pull_requests": contar_pull_requests(),
        "pruebas_backend": backend,
        "pruebas_frontend": frontend,
        "pruebas_total": backend + frontend,
        "funcionalidades": total,
        "funcionalidades_especificadas": especificadas,
        "funcionalidades_por_estado": estados,
        "adr": len(list(carpeta_adr.glob("0*.md"))),
        "bitacora": len(list((RAIZ / "docs" / "bitacora").glob("2*.md"))),
        "requisitos": contar_requisitos(),
    }


def a_markdown(cifras):
    """Tabla en Markdown, lista para copiar a los hechos del sistema."""
    filas = [
        ("Commits (sin integraciones)", cifras["commits"]),
        ("Commits con coautoría de IA",
         f"{cifras['commits_con_ia']} ({str(cifras['porcentaje_con_ia']).replace('.', ',')} %)"),
        ("Pull requests integrados", cifras["pull_requests"]),
        ("Pruebas automatizadas", f"{cifras['pruebas_total']} ({cifras['pruebas_backend']} "
                                  f"del backend y {cifras['pruebas_frontend']} de la interfaz)"),
        ("Funcionalidades en el plan", cifras["funcionalidades"]),
        ("Funcionalidades con especificación", cifras["funcionalidades_especificadas"]),
        ("Registros de decisiones de arquitectura (ADR)", cifras["adr"]),
        ("Entradas de bitácora", cifras["bitacora"]),
    ]
    for clave, valor in cifras["requisitos"].items():
        filas.append((clave.replace("_", " ").capitalize(), valor))
    lineas = [f"Cifras al {cifras['fecha']} (commit {cifras['commit']}).", "",
              "| Indicador | Valor |", "|---|---|"]
    lineas += [f"| {nombre} | {valor} |" for nombre, valor in filas]
    return "\n".join(lineas) + "\n"


def main(argumentos=None):
    """Punto de entrada por línea de comandos."""
    analizador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analizador.add_argument("--json", action="store_true", help="Salida en JSON")
    opciones = analizador.parse_args(argumentos)
    cifras = calcular()
    sys.stdout.write(json.dumps(cifras, ensure_ascii=False, indent=2) + "\n"
                     if opciones.json else a_markdown(cifras))
    return 0


if __name__ == "__main__":
    sys.exit(main())
