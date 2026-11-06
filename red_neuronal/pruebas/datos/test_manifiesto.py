"""Pruebas del manifiesto de imágenes (tarea T06)."""

from dataclasses import replace

import pytest

from clasificador.datos.manifiesto import (
    ErrorManifiesto,
    RegistroImagen,
    escribir_manifiesto,
    huella_archivo,
    huella_manifiesto,
    leer_manifiesto,
)


def _registros():
    return [
        RegistroImagen("a" * 64, "real/1.jpg", 0, "propio", "real", "entrenamiento"),
        RegistroImagen("b" * 64, "gen/2.jpg", 1, "propio", "gemini", "prueba", "whatsapp"),
        RegistroImagen("c" * 64, "gen/3.jpg", 1, "openfake", "flux", "no_visto"),
    ]


def test_ida_y_vuelta_sin_perdida(tmp_path):
    """Lo que se escribe se lee igual, en orden canónico."""
    ruta = escribir_manifiesto(_registros(), tmp_path / "sub" / "manifiesto.csv")
    leidos = leer_manifiesto(ruta)
    assert sorted(leidos, key=str) == sorted(_registros(), key=str)


def test_la_huella_no_depende_del_orden():
    """Reordenar las filas no cambia la huella."""
    registros = _registros()
    assert huella_manifiesto(registros) == huella_manifiesto(list(reversed(registros)))


def test_la_huella_cambia_si_cambia_un_valor():
    """Mover una imagen de partición produce otra versión del conjunto."""
    registros = _registros()
    modificados = [replace(registros[0], particion="validacion")] + registros[1:]
    assert huella_manifiesto(registros) != huella_manifiesto(modificados)


def test_la_huella_del_archivo_es_sha256(tmp_path):
    """Coincide con el valor conocido de SHA-256 de 'abc'."""
    ruta = tmp_path / "abc.txt"
    ruta.write_bytes(b"abc")
    esperado = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert huella_archivo(ruta) == esperado


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"clase": 2}, "clase"),
        ({"particion": "otra"}, "partición"),
        ({"variante": "otra"}, "variante"),
    ],
)
def test_los_valores_invalidos_se_rechazan(cambios, mensaje):
    """No se puede construir un registro con valores fuera del dominio."""
    with pytest.raises(ErrorManifiesto, match=mensaje):
        replace(_registros()[0], **cambios)


def test_leer_un_manifiesto_inexistente_falla(tmp_path):
    """Se informa la ruta que falta."""
    with pytest.raises(ErrorManifiesto, match="no existe"):
        leer_manifiesto(tmp_path / "nada.csv")


def test_leer_un_manifiesto_con_columnas_faltantes_falla(tmp_path):
    """Un CSV ajeno no se interpreta como manifiesto."""
    ruta = tmp_path / "otro.csv"
    ruta.write_text("ruta,clase\nx.jpg,0\n", encoding="utf-8")
    with pytest.raises(ErrorManifiesto, match="faltan columnas"):
        leer_manifiesto(ruta)


def test_leer_una_clase_no_numerica_falla(tmp_path):
    """La línea con el error se informa."""
    ruta = escribir_manifiesto(_registros(), tmp_path / "m.csv")
    texto = ruta.read_text(encoding="utf-8").replace(",0,", ",cero,", 1)
    ruta.write_text(texto, encoding="utf-8")
    with pytest.raises(ErrorManifiesto, match="línea"):
        leer_manifiesto(ruta)
