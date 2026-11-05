"""Pruebas de las cifras del proyecto calculadas desde el repositorio (funcionalidad 037)."""
from herramientas import cifras_del_proyecto as cifras


def test_las_cifras_son_coherentes():
    """Los conteos son positivos y la coautoría no supera el total de commits."""
    datos = cifras.calcular()
    assert datos["commits"] > 0 and 0 <= datos["commits_con_ia"] <= datos["commits"]
    assert datos["pruebas_total"] == datos["pruebas_backend"] + datos["pruebas_frontend"]
    assert datos["adr"] > 0 and datos["requisitos"]["funcionales"] > 0


def test_la_tabla_usa_coma_decimal():
    """La salida en Markdown usa la coma decimal del español."""
    texto = cifras.a_markdown(cifras.calcular())
    assert "| Commits con coautoría de IA |" in texto and "." not in texto.split("(")[2][:6]
