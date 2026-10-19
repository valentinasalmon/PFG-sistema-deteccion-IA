"""Pruebas de la validación de datos (tarea T07)."""

import shutil
from dataclasses import replace

import pytest

from clasificador.datos.manifiesto import RegistroImagen, huella_archivo
from clasificador.datos.validacion import ErrorValidacionDatos, exigir_valido, validar


@pytest.fixture
def conjunto(directorio_imagenes, tmp_path):
    """Manifiesto balanceado y válido construido sobre las imágenes de prueba."""
    registros = []
    for indice, imagen in enumerate(directorio_imagenes):
        particion = ("entrenamiento", "validacion", "prueba")[indice // 2 % 3]
        registros.append(
            RegistroImagen(
                huella_sha256=huella_archivo(imagen.ruta),
                ruta_relativa=str(imagen.ruta.relative_to(tmp_path)),
                clase=imagen.clase,
                fuente="prueba",
                generador=imagen.generador,
                particion=particion,
            )
        )
    return registros, tmp_path


def test_un_conjunto_correcto_es_valido(conjunto):
    """Sin errores, la validación pasa y resume los conteos."""
    registros, raiz = conjunto
    resultado = validar(registros, raiz)
    assert resultado.es_valido, resultado.errores
    assert resultado.resumen["clase"] == {"real": 20, "sintetica": 20}
    exigir_valido(resultado)


def test_un_manifiesto_vacio_no_es_valido(tmp_path):
    """No se puede entrenar sin datos."""
    assert not validar([], tmp_path).es_valido


def test_detecta_una_imagen_corrupta(conjunto, imagen_corrupta):
    """Un archivo que no es imagen se informa."""
    registros, raiz = conjunto
    corrupta = RegistroImagen(
        huella_archivo(imagen_corrupta), imagen_corrupta.name, 0, "prueba", "real", "prueba"
    )
    resultado = validar(registros + [corrupta], raiz, desbalance_tolerado=0.5)
    assert any("corrupta" in error for error in resultado.errores)


def test_detecta_una_imagen_inexistente(conjunto):
    """Una fila que apunta a un archivo que no está se informa."""
    registros, raiz = conjunto
    faltante = replace(registros[0], ruta_relativa="no/existe.jpg", huella_sha256="f" * 64)
    resultado = validar(registros + [faltante], raiz, desbalance_tolerado=0.5)
    assert any("inexistente" in error for error in resultado.errores)


def test_detecta_un_archivo_modificado(conjunto):
    """Si la imagen cambió después de registrarla, la huella no coincide."""
    registros, raiz = conjunto
    alterado = replace(registros[0], huella_sha256="0" * 64)
    resultado = validar([alterado] + registros[1:], raiz)
    assert any("huella no coincide" in error for error in resultado.errores)


def test_detecta_un_duplicado_en_la_misma_particion(conjunto):
    """Una misma imagen copiada con otro nombre es un duplicado."""
    registros, raiz = conjunto
    original = registros[0]
    copia_ruta = raiz / "copia.jpg"
    shutil.copy(raiz / original.ruta_relativa, copia_ruta)
    copia = replace(original, ruta_relativa="copia.jpg")
    resultado = validar(registros + [copia], raiz, desbalance_tolerado=0.5)
    assert any("duplicada" in error for error in resultado.errores)


def test_detecta_un_solapamiento_entre_particiones(conjunto):
    """La misma imagen en entrenamiento y en prueba es una fuga."""
    registros, raiz = conjunto
    original = next(r for r in registros if r.particion == "entrenamiento")
    shutil.copy(raiz / original.ruta_relativa, raiz / "fuga.jpg")
    fuga = replace(original, ruta_relativa="fuga.jpg", particion="prueba")
    resultado = validar(registros + [fuga], raiz, desbalance_tolerado=0.5)
    assert any("solapamiento" in error for error in resultado.errores)


def test_detecta_un_generador_reservado_en_entrenamiento(conjunto):
    """El generador reservado como no visto no puede usarse para entrenar."""
    registros, raiz = conjunto
    resultado = validar(registros, raiz, generadores_reservados=["generador_a"])
    assert any("reservado 'generador_a'" in error for error in resultado.errores)


def test_detecta_un_desbalance(conjunto):
    """Una partición con muchas más imágenes de una clase se rechaza."""
    registros, raiz = conjunto
    sin_sinteticas_de_prueba = [
        r for r in registros if not (r.particion == "prueba" and r.clase == 1)
    ]
    resultado = validar(sin_sinteticas_de_prueba, raiz)
    assert any("desbalance en 'prueba'" in error for error in resultado.errores)


def test_se_puede_validar_sin_los_archivos(conjunto, tmp_path):
    """La estructura se valida aunque las imágenes no estén descargadas."""
    registros, _ = conjunto
    vacio = tmp_path / "vacio"
    vacio.mkdir()
    assert validar(registros, vacio, verificar_archivos=False).es_valido


def test_exigir_valido_detiene_el_pipeline_con_todos_los_errores(conjunto):
    """Todos los errores se informan juntos en la excepción."""
    registros, raiz = conjunto
    alterados = [replace(r, huella_sha256=str(i) * 64) for i, r in enumerate(registros[:2])]
    resultado = validar(alterados + registros[2:], raiz)
    with pytest.raises(ErrorValidacionDatos, match="2 errores"):
        exigir_valido(resultado)
