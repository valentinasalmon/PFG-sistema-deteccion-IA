"""Pruebas de la redacción de la actividad reciente del panel (funcionalidad 013)."""
from types import SimpleNamespace

import pytest

from app.servicios import auditoria
from app.servicios.servicio_panel import redactar_actividad

ANA = SimpleNamespace(nombre="Ana", apellido="López")


def _entrada(accion, **detalle):
    return SimpleNamespace(accion=accion, detalle={"numero": "CASO-2026-000007", **detalle})


@pytest.mark.parametrize(("detalle", "esperado"), [
    ({"solicitud": True, "destinatario": 3}, "Ana López pidió transferir el caso CASO-2026-000007"),
    ({"cancelada": True}, "Ana López canceló la transferencia del caso CASO-2026-000007"),
    ({"respuesta": "aceptada"}, "Ana López aceptó la transferencia del caso CASO-2026-000007"),
    ({"respuesta": "rechazada"}, "Ana López rechazó la transferencia del caso CASO-2026-000007"),
    ({"anterior": 1, "nuevo": 2}, "Ana López transfirió el caso CASO-2026-000007"),
])
def test_variantes_de_la_transferencia(detalle, esperado):
    """Cada paso de la transferencia tiene su propio texto (RF48 CA2)."""
    assert redactar_actividad(_entrada(auditoria.CASO_TRANSFERENCIA, **detalle), ANA) == esperado


def test_estado_desconocido_y_cuenta_eliminada():
    """Sin la operación se usa el texto general; sin usuario, "Una cuenta eliminada"."""
    entrada = _entrada(auditoria.CASO_CAMBIO_ESTADO)

    assert redactar_actividad(entrada, None) == (
        "Una cuenta eliminada cambió el estado del caso CASO-2026-000007"
    )
