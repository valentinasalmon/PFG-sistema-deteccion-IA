"""Pruebas del seguimiento de experimentos (tarea T17)."""

import mlflow

from clasificador.seguimiento.experimentos import (
    RegistradorMlflow,
    RegistradorNulo,
    aplanar,
    commit_actual,
    describir_entorno,
)


def test_aplanar_convierte_claves_anidadas():
    """Las secciones anidadas se unen con puntos."""
    assert aplanar({"a": {"b": 1, "c": {"d": True}}, "e": "x"}) == {
        "a.b": "1", "a.c.d": "True", "e": "x",
    }


def test_commit_actual_en_el_repositorio():
    """Dentro del repositorio devuelve un hash de 40 caracteres (con o sin sufijo)."""
    assert len(commit_actual().split("-")[0]) == 40


def test_commit_actual_fuera_de_un_repositorio(tmp_path):
    """Fuera de Git no falla: informa 'desconocido'."""
    assert commit_actual(tmp_path) == "desconocido"


def test_describir_entorno_incluye_versiones():
    """Se registran Python, PyTorch y el dispositivo."""
    entorno = describir_entorno()
    assert {"python", "torch", "dispositivo", "plataforma"} <= set(entorno)


def test_el_registrador_nulo_guarda_todo_en_memoria(tmp_path):
    """Permite verificar en las pruebas qué se registró."""
    registrador = RegistradorNulo()
    identificador = registrador.iniciar("prueba", {"entrenamiento": {"epocas": 2}})
    registrador.registrar_metricas({"auc": 0.9}, paso=1)
    registrador.registrar_artefacto(tmp_path / "ficha.md")
    registrador.finalizar(exitosa=False)
    assert identificador == "nulo-prueba"
    assert registrador.parametros == {"entrenamiento.epocas": "2"}
    assert registrador.metricas == [(1, {"auc": 0.9})]
    assert registrador.estado == "fallida"


def test_el_registrador_mlflow_crea_la_ejecucion(tmp_path):
    """La ejecución queda en el almacén de archivos con parámetros, métricas y artefactos."""
    artefacto = tmp_path / "nota.txt"
    artefacto.write_text("hola", encoding="utf-8")
    registrador = RegistradorMlflow(tmp_path / "mlruns")
    identificador = registrador.iniciar("prueba", {"semilla": 42, "datos": {"fuente": "x"}})
    registrador.registrar_metricas({"auc_validacion": 0.75}, paso=0)
    registrador.registrar_artefacto(artefacto)
    registrador.finalizar()

    ejecucion = mlflow.get_run(identificador)
    assert ejecucion.info.status == "FINISHED"
    assert ejecucion.data.params == {"semilla": "42", "datos.fuente": "x"}
    assert ejecucion.data.metrics["auc_validacion"] == 0.75
    artefactos = mlflow.artifacts.list_artifacts(run_id=identificador)
    assert [a.path for a in artefactos] == ["nota.txt"]
