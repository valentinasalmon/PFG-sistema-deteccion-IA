"""Pruebas de la separación del conjunto propio en evaluación fija y ajuste."""
from collections import Counter

import pytest

from clasificador.datos.particion_propia import (
    LADO_AJUSTE,
    LADO_EVALUACION,
    LADOS,
    TABLA_FIJA,
    generar_tabla,
    lado_de,
    leer_tabla,
)


def test_tabla_fija_cubre_la_lista_maestra_mitad_y_mitad():
    """Los 89 prompts tienen lado; cada escena queda partida a la mitad."""
    tabla = leer_tabla()
    assert len(tabla) == 89 and set(tabla.values()) == set(LADOS)
    with TABLA_FIJA.open(encoding="utf-8") as archivo:
        filas = [linea.strip().split(",") for linea in archivo][1:]
    por_escena = Counter((escena, lado) for _, _, escena, lado in filas)
    for escena in {fila[2] for fila in filas}:
        diferencia = por_escena[(escena, LADO_EVALUACION)] - por_escena[(escena, LADO_AJUSTE)]
        assert abs(diferencia) <= 1


def test_la_tabla_fija_coincide_con_la_regla():
    """Regenerar la tabla da lo mismo: nadie la editó a mano."""
    tabla = leer_tabla()
    with TABLA_FIJA.open(encoding="utf-8") as archivo:
        filas = [linea.strip().split(",") for linea in archivo][1:]
    tonos = ["muy clara", "clara", "trigueña", "morena", "marrón oscura", "negra"]
    prompts = [
        {"numero": int(n), "archivo": a, "escena": e,
         "tono": tonos[(int(n) - 39) % 6] if e == "lesion" else ""}
        for n, a, e, _ in filas
    ]
    assert {fila["numero"]: fila["lado"] for fila in generar_tabla(prompts)} == tabla


def test_todas_las_herramientas_y_variantes_de_un_prompt_van_juntas():
    """El lado depende del número, no de la carpeta ni de la extensión (sin fuga)."""
    lados = {
        lado_de(ruta) for ruta in (
            "sintetica/chatgpt/original/01-choque-007.png",
            "sintetica/gemini/captura/01-choque-007.jpg",
            "SINTETICA/COPILOT/ORIGINAL/01-choque-007.png",
        )
    }
    assert len(lados) == 1


def test_un_prefijo_de_escena_equivocado_no_cambia_el_lado():
    """01-rayon-017 y 02-rayon-017 son el mismo prompt: mismo lado."""
    assert lado_de("01-rayon-017.png") == lado_de("02-rayon-017.png")


def test_ediciones_siguen_a_su_foto_de_origen():
    """Una edición va del lado de la foto real de la que sale."""
    origen = "01-choque-301.jpg"
    assert lado_de("01-choque-201.png", foto_de_origen=origen) == lado_de(origen)


def test_reales_y_archivos_sin_formato_tienen_lado_estable():
    """Fuera de la lista maestra, el lado sale de una huella: siempre el mismo."""
    assert lado_de("01-choque-305.jpg") == lado_de("01-choque-305.jpg") in LADOS
    contenido = b"foto de cardd"
    assert lado_de("000123.jpg", contenido=contenido) == lado_de("otro.jpg", contenido=contenido)
    with pytest.raises(ValueError, match="hace falta el contenido"):
        lado_de("000123.jpg")


def test_reales_se_reparten_cerca_de_la_mitad():
    """Con muchas fotos reales, cada lado se lleva alrededor de la mitad."""
    cantidad = Counter(lado_de(f"01-choque-{numero}.jpg") for numero in range(300, 700))
    assert 160 <= cantidad[LADO_EVALUACION] <= 240
