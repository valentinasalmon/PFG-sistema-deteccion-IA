"""Comando semanal del catálogo de la SSN y su estado (funcionalidad 052).

Realiza: 052 CA1, CA5.
"""
# pylint: disable=redefined-outer-name,unused-argument
from unittest import mock

import pytest

from app.integraciones.fuente_ssn import FuenteSsnNoDisponible
from pruebas.unitarias.test_catalogo_ssn import _aseguradoras, _csv


@pytest.fixture
def carpeta(aplicacion, tmp_path):
    """Copia actualizada en una carpeta temporal."""
    anterior = aplicacion.config["CARPETA_CATALOGOS"]
    aplicacion.config["CARPETA_CATALOGOS"] = str(tmp_path)
    yield tmp_path
    aplicacion.config["CARPETA_CATALOGOS"] = anterior


def _correr(aplicacion, *argumentos):
    return aplicacion.test_cli_runner().invoke(
        args=["catalogos", "actualizar-aseguradoras", *argumentos]
    )


def test_actualiza_y_el_estado_lo_muestra(aplicacion, cliente, carpeta, correos):
    """El comando aplica el archivo nuevo; /api/salud y el catálogo lo reflejan."""
    with mock.patch("app.integraciones.fuente_ssn.FuenteSsn.descargar",
                    return_value=(_csv(_aseguradoras(200)),
                                  {"url": "https://ssn/x.csv", "actualizado": "2026-10-26"})):
        resultado = _correr(aplicacion)
    assert resultado.exit_code == 0, resultado.output
    assert "200 aseguradoras" in resultado.output
    estado = cliente.get("/api/salud").get_json()["catalogo_ssn"]
    assert estado["total"] == 200 and estado["actualizado_en_la_fuente"] == "2026-10-26"
    lista = cliente.get("/api/catalogos/aseguradoras").get_json()["aseguradoras"]
    assert len(lista) == 200


def test_portal_caido_sale_con_error(aplicacion, carpeta):
    """Sin portal, código 1 para que systemd lo marque como falla."""
    with mock.patch("app.integraciones.fuente_ssn.FuenteSsn.descargar",
                    side_effect=FuenteSsnNoDisponible("caído")):
        resultado = _correr(aplicacion)
    assert resultado.exit_code == 1


def test_correo_al_administrador(aplicacion, correos):
    """El aviso nombra las registradas para revisar y las revocaciones."""
    # pylint: disable=import-outside-toplevel
    from types import SimpleNamespace

    from app.repositorios.catalogo_aseguradoras import Aseguradora
    from app.servicios.fabrica import _correos

    revocada = Aseguradora(1, "SUR (Revocación autorización para operar no firme)",
                           "30000000001", "Vida")
    with aplicacion.app_context():
        servicio = _correos(aplicacion.config, aplicacion.extensions["enviador_correo"])
        servicio.enviar_aviso_catalogo_ssn(
            SimpleNamespace(correo="admin@ejemplo.com", nombre="Rita"),
            {"altas": [], "bajas": [], "modificadas": [revocada], "revocaciones": [revocada]},
            [SimpleNamespace(nombre="Seguros Sur", cuit="30000000001")], 192,
        )
    correo = correos[-1]
    assert correo.destinatario == "admin@ejemplo.com"
    assert "1 aseguradora(s) para revisar" in correo.asunto
    assert "Seguros Sur (CUIT 30000000001)" in correo.texto
    assert "revocación de la autorización en trámite (1)" in correo.texto.lower()
