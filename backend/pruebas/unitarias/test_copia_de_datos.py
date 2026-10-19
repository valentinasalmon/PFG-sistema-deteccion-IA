"""Pruebas del formato de fechas de la copia de datos personales (funcionalidad 019)."""
from app.informes.copia_de_datos import _formatear  # pylint: disable=protected-access


def test_formatea_fechas_con_y_sin_hora():
    """El PDF muestra las fechas como dd/mm/aaaa, con la hora si la tienen."""
    assert _formatear("2026-09-01") == "01/09/2026"
    assert _formatear("2026-10-19T13:45:12.123456") == "19/10/2026 13:45"
    assert _formatear(None) == "—"
