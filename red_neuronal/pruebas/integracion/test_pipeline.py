"""Prueba de integración del pipeline completo (tarea T22).

Recorre todas las etapas con la línea de comandos, como lo hará el cuaderno
de Kaggle, sobre un conjunto pequeño generado en memoria y en CPU:

    obtener → validar → preparar → entrenar → exportar → evaluar → publicar

Verifica que cada etapa deja sus salidas y que la versión queda publicada
en un registro local con su ficha.
"""

import json
from pathlib import Path

import pytest
import yaml

from clasificador import pipeline
from clasificador.__main__ import principal
from clasificador.inferencia.predictor import PredictorOnnx
from clasificador.registro.registro_modelos import RegistroLocal
from pruebas.conftest import crear_imagen_real, crear_imagen_sintetica

CANTIDAD_POR_GRUPO = 24


def _crear_conjunto(raiz: Path) -> None:
    """Conjunto con la estructura <clase>/<generador>/<variante>/."""
    for indice in range(2 * CANTIDAD_POR_GRUPO):
        carpeta = raiz / "real" / "camara" / "original"
        carpeta.mkdir(parents=True, exist_ok=True)
        crear_imagen_real(260, 240, semilla=indice).save(carpeta / f"r{indice:03d}.png")
    for generador in ("generador_a", "generador_b"):
        carpeta = raiz / "sintetica" / generador / "original"
        carpeta.mkdir(parents=True, exist_ok=True)
        for indice in range(CANTIDAD_POR_GRUPO):
            semilla = 5000 + indice + (100 if generador == "generador_b" else 0)
            crear_imagen_sintetica(250, 250, semilla).save(carpeta / f"s{indice:03d}.webp")


@pytest.fixture
def configuracion_pipeline(tmp_path, monkeypatch):
    """Configuración YAML mínima para correr el pipeline en CPU."""
    # El árbol de Git local puede tener cambios sin confirmar durante el
    # desarrollo; en la integración continua y en Kaggle siempre está limpio.
    monkeypatch.setattr(pipeline, "commit_actual", lambda: "c" * 40)
    _crear_conjunto(tmp_path / "fuente")
    contenido = {
        "nombre": "integracion",
        "semilla": 3,
        "directorio_trabajo": str(tmp_path / "trabajo"),
        "datos": {
            "fuentes": [
                {
                    "nombre": "propio", "tipo": "carpeta_local", "ruta": str(tmp_path / "fuente"),
                    "cantidad_reales": 2 * CANTIDAD_POR_GRUPO,
                    "cantidad_sinteticas": 2 * CANTIDAD_POR_GRUPO,
                    "licencia": "imágenes generadas para pruebas",
                }
            ],
            "lado_menor": [224, 240],
            "desbalance_tolerado": 0.2,  # grupos chicos: el redondeo desbalancea
        },
        "entrenamiento": {
            "preentrenado": False, "epocas": 5, "tamanio_lote": 16, "tasa_aprendizaje": 0.002,
            "tamanio_recorte": 64, "trabajadores_carga": 0,
        },
        # La prueba verifica que las etapas se conecten, no la calidad del
        # modelo diminuto: esa se mide en Kaggle con el umbral real de 0,90.
        "compuerta": {"auc_minimo": 0.6},
    }
    ruta = tmp_path / "configuracion.yaml"
    ruta.write_text(yaml.safe_dump(contenido, allow_unicode=True), encoding="utf-8")
    return ruta, tmp_path


def test_el_pipeline_completo_publica_una_version(configuracion_pipeline):
    """Todas las etapas terminan bien y la versión 0.1.0 queda publicada."""
    ruta, raiz = configuracion_pipeline
    trabajo = raiz / "trabajo"
    configuracion = ["--configuracion", str(ruta)]

    for etapa in ("obtener", "validar", "preparar", "entrenar"):
        assert principal([etapa, *configuracion]) == 0, etapa
    assert (trabajo / "preparado" / "manifiesto.csv").is_file()
    entrenamiento = json.loads((trabajo / "entrenamiento" / "resultado.json").read_text("utf-8"))
    assert entrenamiento["temperatura"] > 0
    assert (trabajo / "mlruns" / "mlflow.db").is_file()

    assert principal(["exportar", *configuracion, "--version", "0.1.0"]) == 0
    assert PredictorOnnx(trabajo / "exportacion" / "modelo.onnx").version == "0.1.0"

    conjunto_propio = ["--conjunto-propio", str(raiz / "fuente")]
    assert principal(["evaluar", *configuracion, *conjunto_propio]) == 0
    metricas = json.loads((trabajo / "evaluacion" / "prueba" / "metricas.json").read_text("utf-8"))
    assert metricas["total"]["auc"] >= 0.6
    assert (trabajo / "evaluacion" / "condiciones_reales" / "metricas.json").is_file()

    registro = f"local:{raiz / 'registro'}"
    publicar = ["publicar", *configuracion, "--version", "0.1.0", "--registro", registro]
    assert principal(publicar) == 0
    assert RegistroLocal(raiz / "registro").versiones() == ["0.1.0"]
    ficha = (raiz / "registro" / "v0.1.0" / "ficha.md").read_text(encoding="utf-8")
    assert "# Ficha del modelo 0.1.0" in ficha
    assert "### Condiciones reales de uso" in ficha
    assert (raiz / "registro" / "v0.1.0" / "mlruns.zip").is_file()

    # Una versión publicada es inmutable.
    assert principal(publicar) == 1


def test_publicar_con_otra_version_que_la_exportada_falla(configuracion_pipeline, capsys):
    """La versión del ONNX y la publicada deben coincidir."""
    ruta, raiz = configuracion_pipeline
    configuracion = ["--configuracion", str(ruta)]
    trabajo = raiz / "trabajo"
    (trabajo / "exportacion").mkdir(parents=True)
    (trabajo / "entrenamiento").mkdir(parents=True)
    (trabajo / "entrenamiento" / "resultado.json").write_text("{}", encoding="utf-8")
    (trabajo / "exportacion" / "exportacion.json").write_text(
        json.dumps({"version": "0.1.0"}), encoding="utf-8"
    )
    codigo = principal(
        ["publicar", *configuracion, "--version", "0.2.0", "--registro", f"local:{raiz / 'r'}"]
    )
    assert codigo == 1
    assert "volver a exportar" in capsys.readouterr().err
