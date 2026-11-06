"""Índice de Calidad del Software (QI) del proyecto (funcionalidad 018).

Calcula el QI que exige RNF19 CA2 (QI ≥ 0,75) con la fórmula propuesta en
``docs/calidad/indice-de-calidad.md`` (CP-04, pendiente de validar con el
tutor). Es un promedio ponderado de seis componentes normalizados entre 0 y 1:

==== ============================================== =====
Sím. Componente                                     Peso
==== ============================================== =====
Cb   Cobertura de líneas del backend (coverage.py)  0,20
Cf   Cobertura de líneas del frontend (Vitest)      0,15
E    Puntuación de pylint / 10                      0,15
K    Funciones con complejidad ciclomática ≤ 10     0,10
D    1 − proporción de líneas duplicadas            0,10
U    Puntaje SUS de la prueba de usabilidad / 100   0,30
==== ============================================== =====

Mientras no haya prueba de usabilidad, U se omite y los demás pesos se
reescalan para sumar 1; el resultado se informa como provisorio.

Uso, desde ``backend/``::

    pytest --cov=app --cov-report=json:coverage.json
    (cd ../frontend && npx vitest run --coverage --coverage.reporter=json-summary)
    python herramientas/indice_calidad.py --cobertura-backend coverage.json \\
        --cobertura-frontend ../frontend/coverage/coverage-summary.json [--sus 78.5]

No usa dependencias nuevas: la complejidad la mide flake8 (mccabe) y la
duplicación, el verificador de similitudes de pylint.

Realiza: RNF19 (CA2); CP-04.
"""
import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

PESOS = {"Cb": 0.20, "Cf": 0.15, "E": 0.15, "K": 0.10, "D": 0.10, "U": 0.30}
UMBRAL = 0.75
COMPLEJIDAD_MAXIMA = 10
NOMBRES = {
    "Cb": "Cobertura del backend",
    "Cf": "Cobertura del frontend",
    "E": "Análisis estático (pylint)",
    "K": "Complejidad ciclomática acotada",
    "D": "Código sin duplicar",
    "U": "Usabilidad (SUS)",
}


def calcular_indice(componentes, pesos=None):
    """QI a partir de componentes entre 0 y 1; los ausentes (None) no cuentan.

    Returns:
        dict con ``qi``, ``provisorio`` (falta algún componente), ``cumple``
        (qi ≥ 0,75) y los ``pesos`` efectivos usados.
    """
    pesos = pesos or PESOS
    presentes = {clave: valor for clave, valor in componentes.items() if valor is not None}
    for clave, valor in presentes.items():
        if not 0 <= valor <= 1:
            raise ValueError(f"El componente {clave} debe estar entre 0 y 1 (vale {valor}).")
    total = sum(pesos[clave] for clave in presentes)
    if total == 0:
        raise ValueError("No hay componentes para calcular el índice.")
    efectivos = {clave: pesos[clave] / total for clave in presentes}
    qi = sum(efectivos[clave] * valor for clave, valor in presentes.items())
    return {
        "qi": round(qi, 4),
        "provisorio": len(presentes) < len(pesos),
        "cumple": qi >= UMBRAL,
        "pesos": efectivos,
    }


def puntaje_sus(respuestas):
    """Puntaje SUS (0 a 100) de un participante a partir de sus 10 respuestas (1 a 5).

    Fórmula estándar de Brooke (1996): las preguntas impares aportan
    ``respuesta − 1`` y las pares ``5 − respuesta``; la suma se multiplica por 2,5.
    """
    if len(respuestas) != 10 or any(r not in (1, 2, 3, 4, 5) for r in respuestas):
        raise ValueError("El SUS tiene 10 respuestas, cada una de 1 a 5.")
    suma = sum(r - 1 if indice % 2 == 0 else 5 - r for indice, r in enumerate(respuestas))
    return suma * 2.5


def cobertura_backend(ruta):
    """Proporción de líneas cubiertas según el JSON de coverage.py."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return datos["totals"]["percent_covered"] / 100


def cobertura_frontend(ruta):
    """Proporción de líneas cubiertas según el ``coverage-summary.json`` de Vitest."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return datos["total"]["lines"]["pct"] / 100


def puntuacion_pylint(salida):
    """Puntuación de pylint (0 a 1) leída de su salida de texto."""
    coincidencia = re.search(r"rated at (-?[\d.]+)/10", salida)
    if coincidencia is None:
        raise ValueError("La salida de pylint no tiene la puntuación.")
    return max(0.0, float(coincidencia.group(1)) / 10)


def contar_funciones(directorio):
    """Cantidad de funciones y métodos en los .py del directorio."""
    total = 0
    for archivo in Path(directorio).rglob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        total += sum(
            isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) for nodo in ast.walk(arbol)
        )
    return total


def contar_lineas(directorio):
    """Líneas no vacías de los .py del directorio."""
    return sum(
        sum(1 for linea in archivo.read_text(encoding="utf-8").splitlines() if linea.strip())
        for archivo in Path(directorio).rglob("*.py")
    )


def complejidad_acotada(salida_flake8, total_funciones):
    """Proporción de funciones con complejidad ≤ 10 (cada línea C901 es una función compleja)."""
    if total_funciones == 0:
        return 1.0
    complejas = sum(1 for linea in salida_flake8.splitlines() if " C901 " in linea)
    return 1 - complejas / total_funciones


def sin_duplicar(salida_pylint, total_lineas):
    """1 − proporción de líneas duplicadas, según los avisos R0801 de pylint.

    Cada aviso lista los tramos repetidos como ``==modulo:[desde:hasta]``; se
    cuenta como duplicado el largo del tramo por cada copia además de la primera.
    """
    if total_lineas == 0:
        return 1.0
    duplicadas = 0
    for bloque in salida_pylint.split("Similar lines in")[1:]:
        tramos = re.findall(r"==[\w.]+:\[(\d+):(\d+)\]", bloque)
        if len(tramos) > 1:
            desde, hasta = (int(numero) for numero in tramos[0])
            duplicadas += (hasta - desde) * (len(tramos) - 1)
    return max(0.0, 1 - duplicadas / total_lineas)


def _ejecutar(comando):
    resultado = subprocess.run(comando, capture_output=True, text=True, check=False)
    return resultado.stdout + resultado.stderr


def medir(cobertura_back, cobertura_front=None, sus=None, directorio="app"):
    """Corre pylint y flake8 sobre el código y arma los seis componentes."""
    return {
        "Cb": cobertura_backend(cobertura_back),
        "Cf": cobertura_frontend(cobertura_front) if cobertura_front else None,
        "E": puntuacion_pylint(_ejecutar([sys.executable, "-m", "pylint", directorio])),
        "K": complejidad_acotada(
            _ejecutar([sys.executable, "-m", "flake8", "--select=C901",
                       f"--max-complexity={COMPLEJIDAD_MAXIMA}", directorio]),
            contar_funciones(directorio),
        ),
        "D": sin_duplicar(
            _ejecutar([sys.executable, "-m", "pylint", "--disable=all",
                       "--enable=duplicate-code", directorio]),
            contar_lineas(directorio),
        ),
        "U": sus / 100 if sus is not None else None,
    }


def informe(componentes, resultado):
    """Tabla de texto con cada componente, su peso efectivo y el QI."""
    filas = ["Componente                          Valor   Peso"]
    for clave, nombre in NOMBRES.items():
        valor = componentes.get(clave)
        if valor is None:
            filas.append(f"{nombre:<34}  —       (sin medir)")
        else:
            filas.append(f"{nombre:<34}  {valor:.3f}   {resultado['pesos'][clave]:.3f}")
    estado = "cumple" if resultado["cumple"] else "NO cumple"
    aclaracion = " (provisorio: faltan componentes)" if resultado["provisorio"] else ""
    filas.append(f"QI = {resultado['qi']:.3f} → {estado} el umbral {UMBRAL}{aclaracion}")
    return "\n".join(filas)


def main(argumentos=None):
    """Punto de entrada de la línea de comandos."""
    lector = argparse.ArgumentParser(description="Índice de Calidad del Software (RNF19).")
    lector.add_argument("--cobertura-backend", required=True)
    lector.add_argument("--cobertura-frontend")
    lector.add_argument("--sus", type=float, help="Puntaje SUS promedio (0 a 100)")
    lector.add_argument("--directorio", default="app")
    opciones = lector.parse_args(argumentos)
    componentes = medir(
        opciones.cobertura_backend, opciones.cobertura_frontend, opciones.sus, opciones.directorio
    )
    resultado = calcular_indice(componentes)
    print(informe(componentes, resultado))
    return 0 if resultado["cumple"] else 1


if __name__ == "__main__":
    sys.exit(main())
