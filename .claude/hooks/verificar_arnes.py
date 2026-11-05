#!/usr/bin/env python3
"""Sensor del arnés: verifica que la documentación declare lo que de verdad existe.

El arnés se apoya en documentos (``CLAUDE.md``, el mapa del arnés, los índices
de la bitácora y de los ADR, la tabla de funcionalidades). Si esos documentos
quedan desactualizados, el agente de la sesión siguiente trabaja con
información falsa. Este script compara lo declarado con lo real y avisa.

Controles:

- **Errores** (la integración continua falla): enlaces rotos entre documentos,
  comandos de ``CLAUDE.md`` sin archivo (o al revés), ganchos configurados que
  no existen, *skills* sin registro de origen, funcionalidades, entradas de
  bitácora o ADR que no figuran en su índice.
- **Avisos** (no bloquean): números del mapa del arnés desactualizados,
  cambios del arnés sin anotar en el registro de cambios, propuestas que
  esperan la aprobación de la autora y ramas integradas sin borrar.

Modos:

- sin argumentos: informe completo; sale con código 1 si hay errores;
- ``--actualizar``: además reescribe la tabla de números del mapa del arnés;
- ``--sesion``: resumen breve para el gancho ``SessionStart``; nunca bloquea.

Realiza: funcionalidad 038 (CA1 a CA5) y 039 (CA3); RNF19 (documentación al día).
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAPA_ARNES = RAIZ / "docs" / "arnes" / "README.md"
REGISTRO = RAIZ / "docs" / "arnes" / "registro-de-cambios.md"
CARPETAS_EXCLUIDAS = ("node_modules", ".claude/skills", ".agents", ".venv", ".git/")

# Archivos cuyo cambio es un cambio del arnés y debe anotarse en el registro.
RUTAS_DEL_ARNES = (
    "CLAUDE.md",
    ".claude/commands",
    ".claude/hooks",
    ".claude/settings.json",
    ".pre-commit-config.yaml",
    "commitlint.config.mjs",
    ".github/workflows",
)

ENLACE = re.compile(r"\]\(([^)\s]+)\)")
BLOQUE_CODIGO = re.compile(r"```.*?```", re.S)


class Informe:
    """Acumula los errores y los avisos de cada control."""

    def __init__(self):
        """Crea un informe vacío."""
        self.errores = []
        self.avisos = []

    def error(self, mensaje):
        """Registra un problema que hace fallar la verificación."""
        self.errores.append(mensaje)

    def aviso(self, mensaje):
        """Registra un problema que no bloquea, pero hay que atender."""
        self.avisos.append(mensaje)


def _git(*argumentos):
    """Salida de un comando de git en la raíz, o None si falla."""
    try:
        resultado = subprocess.run(
            ["git", *argumentos], cwd=RAIZ, capture_output=True, text=True,
            timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return resultado.stdout if resultado.returncode == 0 else None


def historial_completo():
    """True si la historia de HEAD llega hasta el primer commit del proyecto.

    En la integración continua el clon es parcial (un solo commit) y los
    números saldrían mal. Un clon parcial pero profundo, que igual llega al
    inicio, cuenta como completo: ninguna de sus raíces es un corte del clon.
    """
    raices = _git("rev-list", "--max-parents=0", "HEAD")
    if not raices:
        return False
    ruta_cortes = _git("rev-parse", "--git-path", "shallow")
    cortes_archivo = RAIZ / ruta_cortes.strip() if ruta_cortes else None
    if cortes_archivo is None or not cortes_archivo.is_file():
        return True
    cortes = set(cortes_archivo.read_text(encoding="utf-8").split())
    return not cortes & set(raices.split())


def documentos():
    """Todos los Markdown del proyecto, sin dependencias ni skills de terceros."""
    for ruta in sorted(RAIZ.rglob("*.md")):
        relativa = ruta.relative_to(RAIZ).as_posix()
        if not any(excluida in relativa for excluida in CARPETAS_EXCLUIDAS):
            yield ruta


def revisar_enlaces(informe):
    """Error por cada enlace relativo a un archivo que no existe."""
    for documento in documentos():
        texto = BLOQUE_CODIGO.sub("", documento.read_text(encoding="utf-8", errors="ignore"))
        for coincidencia in ENLACE.finditer(texto):
            destino = coincidencia.group(1).split("#")[0]
            if not destino or re.match(r"^[a-z][a-z0-9+.-]*:", destino):
                continue
            if not (documento.parent / destino).exists():
                informe.error(
                    f"Enlace roto en {documento.relative_to(RAIZ)}: {coincidencia.group(1)}"
                )


def revisar_comandos(informe):
    """Los comandos de la tabla de CLAUDE.md y los de .claude/commands coinciden."""
    texto = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
    declarados = set(re.findall(r"^\| `/([a-z-]+)", texto, re.M))
    existentes = {ruta.stem for ruta in (RAIZ / ".claude" / "commands").glob("*.md")}
    for nombre in sorted(declarados - existentes):
        informe.error(f"CLAUDE.md declara /{nombre}, pero no existe .claude/commands/{nombre}.md")
    for nombre in sorted(existentes - declarados):
        informe.error(
            f".claude/commands/{nombre}.md existe, pero no figura en la tabla de CLAUDE.md"
        )


def revisar_ganchos(informe):
    """Cada script que configura .claude/settings.json existe."""
    configuracion = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
    for grupos in configuracion.get("hooks", {}).values():
        for grupo in grupos:
            for gancho in grupo.get("hooks", []):
                for script in re.findall(r"\.claude/hooks/[\w.-]+\.py", gancho.get("command", "")):
                    if not (RAIZ / script).is_file():
                        informe.error(f".claude/settings.json usa {script}, que no existe")


def revisar_skills(informe):
    """Cada skill instalada tiene su origen registrado en skills-lock.json y viceversa."""
    registradas = set(json.loads((RAIZ / "skills-lock.json").read_text(encoding="utf-8"))["skills"])
    instaladas = {ruta.name for ruta in (RAIZ / ".claude" / "skills").iterdir() if ruta.is_dir()}
    for nombre in sorted(instaladas - registradas):
        informe.error(f"La skill {nombre} está instalada sin origen en skills-lock.json")
    for nombre in sorted(registradas - instaladas):
        informe.error(f"skills-lock.json registra {nombre}, pero no está instalada")


def revisar_funcionalidades(informe):
    """Cada carpeta de funcionalidad tiene especificación y figura en la tabla."""
    carpeta = RAIZ / "docs" / "funcionalidades"
    tabla = (carpeta / "README.md").read_text(encoding="utf-8")
    numeros = set(re.findall(r"^\| (\d{3}) \|", tabla, re.M))
    for funcionalidad in sorted(carpeta.glob("[0-9][0-9][0-9]-*")):
        if not (funcionalidad / "especificacion.md").is_file():
            informe.error(f"{funcionalidad.relative_to(RAIZ)} no tiene especificacion.md")
        if funcionalidad.name[:3] not in numeros:
            informe.error(
                f"La funcionalidad {funcionalidad.name} no figura en "
                "docs/funcionalidades/README.md"
            )


def revisar_indices(informe):
    """Cada entrada de bitácora y cada ADR figuran en su índice."""
    for carpeta, patron in (("docs/bitacora", "20*.md"), ("docs/arquitectura/decisiones", "0*.md")):
        directorio = RAIZ / carpeta
        indice = (directorio / "README.md").read_text(encoding="utf-8")
        for archivo in sorted(directorio.glob(patron)):
            if f"({archivo.name})" not in indice:
                informe.error(
                    f"{carpeta}/{archivo.name} no figura en el índice {carpeta}/README.md"
                )


def numeros_reales():
    """Indicadores del proceso calculados desde el repositorio, o None sin historial."""
    if not historial_completo():
        return None
    mensajes = _git("log", "--no-merges", "--format=%B%x00", "HEAD") or ""
    commits = [mensaje for mensaje in mensajes.split("\x00") if mensaje.strip()]
    firma_ia = re.compile(r"^Co-Authored-By: Claude", re.M | re.I)
    con_ia = sum(1 for mensaje in commits if firma_ia.search(mensaje))
    integraciones = _git("log", "--merges", "--format=%s", "HEAD") or ""
    funcionalidades = RAIZ / "docs" / "funcionalidades"
    pruebas_backend = sum(
        len(re.findall(r"^\s*def test_", ruta.read_text(encoding="utf-8"), re.M))
        for ruta in (RAIZ / "backend" / "pruebas").rglob("*.py")
    )
    pruebas_frontend = sum(
        len(re.findall(r"^\s*(?:it|test)\(", ruta.read_text(encoding="utf-8"), re.M))
        for ruta in (RAIZ / "frontend" / "src").rglob("*.test.js*")
    )
    porcentaje = round(100 * con_ia / len(commits)) if commits else 0
    return {
        "Commits (sin contar integraciones)": str(len(commits)),
        "Commits con co-autoría de IA": f"{con_ia} ({porcentaje} %)",
        "Pull Requests integrados": str(integraciones.count("Merge pull request")),
        "Especificaciones / planes": (
            f"{len(list(funcionalidades.glob('*/especificacion.md')))} / "
            f"{len(list(funcionalidades.glob('*/plan.md')))}"
        ),
        "Entradas de bitácora": str(len(list((RAIZ / "docs" / "bitacora").glob("20*.md")))),
        "ADR": str(len(list((RAIZ / "docs" / "arquitectura" / "decisiones").glob("0*.md")))),
        "Pruebas automáticas escritas": f"{pruebas_backend} backend + {pruebas_frontend} frontend",
    }


TABLA_NUMEROS = re.compile(
    r"## Números del proceso \(al (\d{4}-\d{2}-\d{2})\)\n\n"
    r"\| Indicador \| Valor \|\n\|---\|---\|\n((?:\|.*\|\n)+)"
)


def revisar_numeros(informe, actualizar=False, hoy=None):
    """Compara la tabla de números del mapa del arnés con los valores reales.

    Con ``actualizar`` reescribe la tabla y su fecha cuando difieren.
    """
    reales = numeros_reales()
    if reales is None:
        return
    texto = MAPA_ARNES.read_text(encoding="utf-8")
    coincidencia = TABLA_NUMEROS.search(texto)
    if coincidencia is None:
        informe.error("docs/arnes/README.md no tiene la tabla «Números del proceso»")
        return
    declarados = dict(re.findall(r"^\| (.+?) \| (.+?) \|$", coincidencia.group(2), re.M))
    if declarados == reales:
        return
    if not actualizar:
        diferencias = [
            f"{clave}: {declarados.get(clave, '—')} → {valor}"
            for clave, valor in reales.items() if declarados.get(clave) != valor
        ]
        informe.aviso(
            f"Los números de docs/arnes/README.md (al {coincidencia.group(1)}) están "
            f"desactualizados: {'; '.join(diferencias)}. Corré verificar_arnes.py --actualizar"
        )
        return
    fecha = (hoy or datetime.date.today()).isoformat()
    filas = "".join(f"| {clave} | {valor} |\n" for clave, valor in reales.items())
    nueva = f"## Números del proceso (al {fecha})\n\n| Indicador | Valor |\n|---|---|\n{filas}"
    actualizado = texto[:coincidencia.start()] + nueva + texto[coincidencia.end():]
    MAPA_ARNES.write_text(actualizado, encoding="utf-8")


def revisar_registro(informe):
    """Avisa si hubo cambios del arnés después de la última fecha del registro."""
    if not historial_completo():
        return
    fechas = re.findall(r"^\| (\d{4}-\d{2}-\d{2}) \|", REGISTRO.read_text(encoding="utf-8"), re.M)
    if not fechas:
        informe.error("docs/arnes/registro-de-cambios.md no tiene entradas")
        return
    ultima = max(fechas)
    salida = _git(
        "log", "--no-merges", "--format=%h %ad %s", "--date=short",
        f"--after={ultima} 23:59:59", "HEAD", "--", *RUTAS_DEL_ARNES,
    ) or ""
    for linea in salida.splitlines():
        informe.aviso(
            f"Cambio del arnés posterior al último registro ({ultima}) sin anotar: {linea}"
        )


def revisar_ramas(informe, base="origin/desarrollo", dias_gracia=1, ahora=None):
    """Avisa por las ramas remotas ya integradas en ``base`` que nadie borró.

    La guía de flujo de trabajo dice que una rama se borra al integrarla; sin
    este control quedaron 51 ramas vivas (funcionalidad 039). Se dejan
    ``dias_gracia`` días por si la rama sigue en uso. Sin la rama base en el
    clon (por ejemplo, en la integración continua) no revisa nada.
    """
    if _git("rev-parse", "--verify", "--quiet", base) is None:
        return
    remoto = base.split("/", 1)[0]
    salida = _git(
        "for-each-ref", "--merged", base, "--format=%(refname:short) %(committerdate:unix)",
        f"refs/remotes/{remoto}",
    ) or ""
    limite = (ahora or datetime.datetime.now().timestamp()) - dias_gracia * 86400
    conservar = {base, f"{remoto}/main", f"{remoto}/HEAD", remoto}
    viejas = [
        nombre for nombre, fecha in (linea.rsplit(" ", 1) for linea in salida.splitlines())
        if nombre not in conservar and int(fecha) < limite
    ]
    if viejas:
        informe.aviso(
            f"{len(viejas)} ramas remotas ya integradas en {base} siguen sin borrar "
            "(por ejemplo, " + ", ".join(sorted(viejas)[:3]) + "). "
            "Correr infraestructura/scripts/limpiar_ramas.sh --aplicar"
        )


def revisar_propuestas(informe):
    """Avisa por cada propuesta del arnés que espera la aprobación de la autora."""
    for propuesta in sorted((RAIZ / "docs" / "arnes").glob("propuesta-*.md")):
        primera = propuesta.read_text(encoding="utf-8").splitlines()[0]
        if "pendiente" in primera.lower():
            informe.aviso(f"Propuesta pendiente de la autora: docs/arnes/{propuesta.name}")


CONTROLES = (
    revisar_enlaces, revisar_comandos, revisar_ganchos, revisar_skills,
    revisar_funcionalidades, revisar_indices, revisar_registro, revisar_propuestas,
    revisar_ramas,
)


def verificar(actualizar=False):
    """Corre todos los controles y devuelve el informe."""
    informe = Informe()
    for control in CONTROLES:
        control(informe)
    revisar_numeros(informe, actualizar=actualizar)
    return informe


def main(argumentos=None):
    """Imprime el informe; en modo normal sale con 1 si hay errores."""
    lector = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    lector.add_argument(
        "--actualizar", action="store_true", help="reescribe los números del mapa del arnés"
    )
    lector.add_argument(
        "--sesion", action="store_true", help="resumen breve para el inicio de sesión"
    )
    opciones = lector.parse_args(argumentos)
    informe = verificar(actualizar=opciones.actualizar)
    if opciones.sesion:
        if informe.errores or informe.avisos:
            print("Estado del arnés al iniciar la sesión (verificar_arnes.py):")
            for mensaje in informe.errores:
                print(f"- ERROR: {mensaje}")
            for mensaje in informe.avisos:
                print(f"- Aviso: {mensaje}")
            print(
                "Corregí lo que corresponda al agente antes de cerrar la etapa "
                "(CLAUDE.md, «El arnés se revisa solo»)."
            )
        return 0
    for mensaje in informe.errores:
        print(f"ERROR: {mensaje}")
    for mensaje in informe.avisos:
        print(f"Aviso: {mensaje}")
    if not informe.errores and not informe.avisos:
        print("El arnés está al día: lo declarado coincide con lo real.")
    return 1 if informe.errores else 0


if __name__ == "__main__":
    sys.exit(main())
