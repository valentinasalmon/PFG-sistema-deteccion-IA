"""Botón «Simular pago» con un proveedor real (funcionalidad 049, CA3).

Realiza: 049 CA3.
"""
from types import SimpleNamespace

import pytest

from app.integraciones.pagos import ESTILO_TRANSFERENCIA, ProveedorPagosSimulado
from app.servicios.errores import AccesoDenegado
from app.servicios.servicio_pagos import ServicioPagos

PROVEEDOR_REAL = SimpleNamespace(
    nombre="real", nombre_visible="Real", titular="evidentIA",
    estilo="redireccion", permite_simular=False,
)


def _servicio(proveedor, permitir):
    return ServicioPagos(
        None, proveedor, {"PERMITIR_SIMULAR_PAGO": permitir}, None
    )


def test_el_proveedor_simulado_siempre_permite_simular():
    """Sin proveedor real no hay otra forma de acreditar."""
    servicio = _servicio(ProveedorPagosSimulado(), False)
    assert servicio.permite_simular() is True
    assert ProveedorPagosSimulado.estilo == ESTILO_TRANSFERENCIA


@pytest.mark.parametrize("permitir", [True, False])
def test_con_proveedor_real_depende_de_la_configuracion(permitir):
    """Con un proveedor real, el botón sigue a PERMITIR_SIMULAR_PAGO."""
    assert _servicio(PROVEEDOR_REAL, permitir).permite_simular() is permitir


def test_simular_sin_permiso_se_rechaza():
    """Desactivado, la ruta de simular no acredita nada."""
    servicio = _servicio(PROVEEDOR_REAL, False)
    servicio._por_token = lambda token: SimpleNamespace()  # pylint: disable=protected-access
    with pytest.raises(AccesoDenegado):
        servicio.simular_acreditacion("cualquiera")
