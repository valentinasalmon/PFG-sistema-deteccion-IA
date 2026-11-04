"""Pruebas de la ficha del modelo (tarea T18)."""

import pytest

from clasificador.registro.ficha import (
    LEYENDA,
    SECCIONES_OBLIGATORIAS,
    ErrorFicha,
    generar_ficha,
    secciones_faltantes,
)
from pruebas.registro.utilidades import datos_ficha, metricas


def test_la_ficha_tiene_todas_las_secciones_y_la_leyenda():
    """Cumple CA17: ninguna sección obligatoria falta."""
    texto = generar_ficha(datos_ficha())
    assert secciones_faltantes(texto) == []
    assert all(seccion in texto for seccion in SECCIONES_OBLIGATORIAS)
    assert LEYENDA in texto


def test_la_ficha_declara_las_limitaciones():
    """Las limitaciones de RF42 CA2 aparecen siempre (CA11)."""
    texto = generar_ficha(datos_ficha())
    assert "No detecta ediciones parciales" in texto
    assert "generadores no vistos" in texto


def test_la_ficha_incluye_datos_licencias_y_metricas():
    """La ficha muestra la licencia, la huella y el AUC de prueba."""
    texto = generar_ficha(datos_ficha())
    assert "| propio |" in texto and "propia" in texto
    assert "a" * 64 in texto
    assert "| 4 | 1.0000 |" in texto
    assert "gemini" in texto  # generador reservado


def test_las_secciones_opcionales_aparecen_si_hay_datos():
    """Los generadores no vistos y el conjunto propio se agregan si se evaluaron."""
    texto = generar_ficha(
        datos_ficha(metricas_no_visto=metricas(), metricas_condiciones_reales=metricas())
    )
    assert "### Generadores no vistos" in texto
    assert "### Condiciones reales de uso" in texto
    assert "_Sin datos._" in texto  # por_variante vacío


def test_sin_metricas_de_prueba_falla():
    """No se puede generar una ficha sin métricas."""
    with pytest.raises(ErrorFicha, match="métricas"):
        generar_ficha(datos_ficha(metricas_prueba={}))


def test_sin_auc_calculable_falla():
    """Un conjunto de prueba con una sola clase no sirve para aprobar el modelo."""
    sin_auc = metricas()
    sin_auc["total"] = {**sin_auc["total"], "auc": None}
    with pytest.raises(ErrorFicha, match="AUC"):
        generar_ficha(datos_ficha(metricas_prueba=sin_auc))


def test_secciones_faltantes_detecta_una_ficha_incompleta():
    """Una ficha editada a mano sin secciones se detecta."""
    faltantes = secciones_faltantes("# Ficha\n## 1. Identificación\n")
    assert "## 6. Métricas" in faltantes
    assert "leyenda de indicio (RN27)" in faltantes


def test_los_valores_logicos_se_muestran_en_espaniol():
    """La ficha no muestra True/False sino sí/no."""
    texto = generar_ficha(datos_ficha())
    assert "| preentrenado | sí |" in texto
    assert "True" not in texto
