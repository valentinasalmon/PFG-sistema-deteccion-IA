"""Pruebas de la compuerta de promoción (tarea T19)."""

from dataclasses import replace

import pytest

from clasificador.registro.compuerta import (
    CandidatoPublicacion,
    ErrorCompuerta,
    evaluar_compuerta,
    exigir_aprobacion,
)
from clasificador.registro.ficha import generar_ficha
from pruebas.registro.utilidades import datos_ficha

APROBABLE = CandidatoPublicacion(
    auc_prueba=0.95,
    diferencia_onnx=1e-6,
    texto_ficha=generar_ficha(datos_ficha()),
    huella_manifiesto_declarada="a" * 64,
    huella_manifiesto_real="a" * 64,
    commit="c" * 40,
)


def _evaluar(candidato):
    return evaluar_compuerta(candidato, auc_minimo=0.90, tolerancia_onnx=1e-3)


def test_un_candidato_que_cumple_todo_se_aprueba():
    """Sin motivos de rechazo, el modelo puede publicarse."""
    resultado = _evaluar(APROBABLE)
    assert resultado.aprobado
    exigir_aprobacion(resultado)


@pytest.mark.parametrize(
    ("cambios", "motivo"),
    [
        ({"auc_prueba": 0.85}, "menor al mínimo"),
        ({"auc_prueba": None}, "no es calculable"),
        ({"diferencia_onnx": 0.01}, "ONNX difiere"),
        ({"texto_ficha": "# Ficha incompleta"}, "a la ficha le faltan"),
        ({"huella_manifiesto_real": "b" * 64}, "huella del manifiesto"),
        ({"commit": "c" * 40 + "-modificado"}, "no estaba confirmado"),
        ({"commit": "desconocido"}, "no estaba confirmado"),
    ],
)
def test_cada_criterio_incumplido_rechaza(cambios, motivo):
    """Cada criterio, por separado, alcanza para rechazar."""
    resultado = _evaluar(replace(APROBABLE, **cambios))
    assert not resultado.aprobado
    assert any(motivo in texto for texto in resultado.motivos_rechazo)


def test_se_informan_todos_los_motivos_juntos():
    """Con tres criterios incumplidos se informan los tres."""
    candidato = replace(APROBABLE, auc_prueba=0.5, diferencia_onnx=1.0, commit="desconocido")
    resultado = _evaluar(candidato)
    assert len(resultado.motivos_rechazo) == 3
    with pytest.raises(ErrorCompuerta, match="rechazó"):
        exigir_aprobacion(resultado)
