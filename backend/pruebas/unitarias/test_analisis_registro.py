"""Pruebas de la descripción de las capas (037): cada capa se describe sola."""
from app.analisis.registro import CLASES_DE_CAPAS, describir_capa


def test_cada_capa_activa_tiene_titulo_explicacion_y_tipo():
    """Una capa nueva sin título o sin explicación se mostraría vacía: la prueba lo frena."""
    for clase in CLASES_DE_CAPAS:
        descripcion = describir_capa(clase.nombre)
        assert descripcion["titulo"] and len(descripcion["que_significa"]) > 40
        assert descripcion["tipo"] in ("determinista", "probabilistico")


def test_una_capa_que_ya_no_existe_no_tiene_descripcion():
    """Resultados viejos de una capa retirada se muestran con su nombre, sin fallar."""
    assert describir_capa("capa_retirada") is None
