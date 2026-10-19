"""Pruebas de la línea de comandos (tarea T21)."""

import pytest

from clasificador.__main__ import (
    ETAPAS,
    _resumir,
    construir_analizador,
    crear_registro,
    principal,
)
from clasificador.datos.validacion import ResultadoValidacion
from clasificador.registro.registro_modelos import RegistroHuggingFace, RegistroLocal


def test_la_ayuda_lista_todas_las_etapas_en_espaniol(capsys):
    """--ayuda muestra las siete etapas y los títulos en español."""
    with pytest.raises(SystemExit) as salida:
        principal(["--ayuda"])
    texto = capsys.readouterr().out
    assert salida.value.code == 0
    assert all(etapa in texto for etapa in ETAPAS)
    assert "uso:" in texto and "opciones:" in texto
    assert "usage" not in texto


def test_un_argumento_faltante_se_informa_en_espaniol(capsys):
    """El error de argparse se traduce."""
    with pytest.raises(SystemExit) as salida:
        principal(["exportar", "--configuracion", "x.yaml"])
    assert salida.value.code == 2
    assert "faltan los argumentos obligatorios: --version" in capsys.readouterr().err


def test_una_configuracion_inexistente_devuelve_codigo_1(tmp_path, capsys):
    """Los errores esperables no muestran una traza: un mensaje y código 1."""
    codigo = principal(["validar", "--configuracion", str(tmp_path / "nada.yaml")])
    assert codigo == 1
    assert "Error en la etapa 'validar'" in capsys.readouterr().err


def test_publicar_exige_registro_y_version():
    """El analizador pide los argumentos propios de cada etapa."""
    argumentos = construir_analizador().parse_args(
        ["publicar", "--configuracion", "c.yaml", "--version", "1.0.0", "--registro", "local:x"]
    )
    assert argumentos.version == "1.0.0"
    assert argumentos.registro == "local:x"


def test_crear_registro_segun_la_especificacion(tmp_path, monkeypatch):
    """local:<ruta> y hugging_face:<repo> crean el registro correspondiente."""
    monkeypatch.setenv("HF_TOKEN", "t")
    assert isinstance(crear_registro(f"local:{tmp_path}"), RegistroLocal)
    assert isinstance(crear_registro("hugging_face:alguien/repo"), RegistroHuggingFace)


@pytest.mark.parametrize("especificacion", ["local", "s3:balde", ":x"])
def test_crear_registro_rechaza_especificaciones_invalidas(especificacion):
    """Un tipo desconocido o sin destino es un error claro."""
    with pytest.raises(ValueError, match="registro"):
        crear_registro(especificacion)


def test_resumir_resultados():
    """El resumen de consola es breve y omite el historial."""
    assert _resumir([1, 2, 3]) == "3 imágenes"
    assert "historial" not in _resumir({"auc": 0.9, "historial": [1, 2]})
    assert _resumir(None) == "None"
    assert _resumir(ResultadoValidacion(resumen={"clase": {"real": 1}})).startswith("sin errores")
