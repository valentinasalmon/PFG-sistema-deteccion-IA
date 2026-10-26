"""Pruebas del registro de versiones desplegadas en Hedera (funcionalidad 029).

En las pruebas el sello es el simulado: nunca se llama a la red real.
"""
# pylint: disable=unused-argument,redefined-outer-name
import io

import pytest
from PIL import Image

from pruebas.conftest import entradas_auditoria

COMMIT = "a" * 40
HUELLA = "b" * 64
CASO = {"espacio": "personal", "tipo": "laboral", "fecha_hecho": "2026-09-01",
        "lugar": "Planta industrial"}


def _registrar(aplicacion, commit=COMMIT, huella=HUELLA):
    return aplicacion.test_cli_runner().invoke(
        args=["sellos", "registrar-version", "--commit", commit, "--huella", huella]
    )


def test_registrar_la_version_desplegada_y_sellarla(aplicacion):
    """RF56 CA1: el despliegue registra el commit y la huella del artefacto, una sola vez."""
    resultado = _registrar(aplicacion)
    assert resultado.exit_code == 0, resultado.output
    assert "sello sellado" in resultado.output
    assert "sello sellado" in _registrar(aplicacion).output  # el mismo commit no se duplica
    assert len(entradas_auditoria(aplicacion, "version.despliegue")) == 1
    sello = entradas_auditoria(aplicacion, "imagen.sello")[-1]
    assert sello["detalle"]["tipo"] == "version" and sello["tipo_recurso"] == "version"


def test_datos_invalidos(aplicacion):
    """Un commit o una huella que no son hexadecimales se rechazan."""
    resultado = _registrar(aplicacion, commit="no-es-un-commit")
    assert resultado.exit_code != 0 and "no son válidos" in resultado.output


@pytest.fixture
def ana(cuenta):
    """Responsable del caso."""
    return cuenta("ana@ejemplo.com")


def test_la_verificacion_del_informe_muestra_la_version(aplicacion, ana):
    """RF56 CA2: el análisis guarda el commit y la verificación pública muestra su sello."""
    aplicacion.config["COMMIT"] = COMMIT
    _registrar(aplicacion)
    id_caso = ana.post("/api/casos", json=CASO).get_json()["caso"]["id"]
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), (9, 9, 9)).save(salida, "PNG")
    imagen = ana.post(
        f"/api/casos/{id_caso}/imagenes",
        data={"archivo": (io.BytesIO(salida.getvalue()), "a.png")},
        content_type="multipart/form-data",
    ).get_json()["imagen"]["id"]
    ana.post(f"/api/casos/{id_caso}/analisis", json={"imagenes": [imagen]})
    informe = ana.get(f"/api/casos/{id_caso}/informes").get_json()["informes"][0]

    datos = aplicacion.test_client().get(
        f"/api/verificacion?codigo={informe['codigo_verificacion']}"
    ).get_json()["informe"]

    assert datos["version"]["commit"] == COMMIT[:7]
    assert datos["version"]["huella"] == HUELLA
    assert datos["version"]["sello"]["estado"] == "sellado"
