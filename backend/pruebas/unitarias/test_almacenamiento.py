"""Pruebas de las implementaciones de almacenamiento (funcionalidad 006).

S3 se prueba con moto, que simula el servicio en memoria: las pruebas no
usan una cuenta de AWS ni la red.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import time
from urllib.parse import parse_qs, urlparse

import boto3
import pytest
from moto import mock_aws

from app.integraciones.almacenamiento import (
    AlmacenamientoLocal,
    AlmacenamientoS3,
    ArchivoNoDisponible,
    crear_almacenamiento,
)

BUCKET = "imagenes-prueba"


@pytest.fixture
def s3(monkeypatch):
    """Bucket versionado en un S3 simulado."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "prueba")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "prueba")
    with mock_aws():
        cliente = boto3.client("s3", region_name="sa-east-1")
        cliente.create_bucket(
            Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "sa-east-1"}
        )
        cliente.put_bucket_versioning(
            Bucket=BUCKET, VersioningConfiguration={"Status": "Enabled"}
        )
        yield cliente


def test_s3_guarda_cifrado_y_lee_sin_modificar(s3):
    """RF34 CA1 y RNF03 CA1: el archivo se guarda tal cual y cifrado."""
    almacenamiento = AlmacenamientoS3(s3, BUCKET, "AES256")
    almacenamiento.guardar("imagenes/abc", b"contenido", "image/png")
    assert almacenamiento.leer("imagenes/abc") == b"contenido"
    cabecera = s3.head_object(Bucket=BUCKET, Key="imagenes/abc")
    assert cabecera["ServerSideEncryption"] == "AES256"
    assert cabecera["ContentType"] == "image/png"


def test_s3_elimina_todas_las_versiones(s3):
    """RF36 CA1: no quedan versiones anteriores ni otros archivos afectados."""
    almacenamiento = AlmacenamientoS3(s3, BUCKET)
    almacenamiento.guardar("imagenes/abc", b"uno", "image/png")
    almacenamiento.guardar("imagenes/abc", b"dos", "image/png")
    almacenamiento.guardar("imagenes/abcd", b"otro", "image/png")

    almacenamiento.eliminar("imagenes/abc")

    versiones = s3.list_object_versions(Bucket=BUCKET)
    claves = {v["Key"] for v in versiones.get("Versions", []) + versiones.get("DeleteMarkers", [])}
    assert claves == {"imagenes/abcd"}


def test_s3_enlace_prefirmado_de_corta_duracion(s3):
    """RF35 CA2: URL prefirmada con vencimiento y nombre de descarga."""
    almacenamiento = AlmacenamientoS3(s3, BUCKET)
    enlace = almacenamiento.enlace("imagenes/abc", 300, nombre_descarga="foto ñ.png")
    assert BUCKET in enlace and "imagenes/abc" in enlace
    parametros = parse_qs(urlparse(enlace).query)
    if "X-Amz-Expires" in parametros:  # firma versión 4
        assert parametros["X-Amz-Expires"] == ["300"]
    else:  # firma versión 2: momento de vencimiento
        assert abs(int(parametros["Expires"][0]) - (time.time() + 300)) < 30
    assert "response-content-disposition" in enlace


def test_crear_almacenamiento_elige_la_implementacion(tmp_path, monkeypatch):
    """La configuración elige S3 o la carpeta local (patrón Strategy)."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "prueba")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "prueba")
    configuracion = {
        "ALMACENAMIENTO": "s3", "S3_REGION": "sa-east-1", "S3_ENDPOINT": "",
        "S3_BUCKET": BUCKET, "S3_CIFRADO": "AES256",
        "DIRECTORIO_ALMACENAMIENTO": str(tmp_path), "SECRET_KEY": "clave",
    }
    assert isinstance(crear_almacenamiento(configuracion), AlmacenamientoS3)
    configuracion["ALMACENAMIENTO"] = "local"
    assert isinstance(crear_almacenamiento(configuracion), AlmacenamientoLocal)


def test_local_rechaza_claves_fuera_de_la_carpeta(tmp_path):
    """Una clave no puede escaparse de la carpeta del almacenamiento."""
    almacenamiento = AlmacenamientoLocal(tmp_path / "datos", "clave")
    with pytest.raises(ArchivoNoDisponible):
        almacenamiento.guardar("../afuera", b"x", "image/png")


def test_local_enlace_de_archivo_eliminado(tmp_path):
    """Un enlace vigente a un archivo que ya no existe no entrega nada."""
    almacenamiento = AlmacenamientoLocal(tmp_path, "clave")
    almacenamiento.guardar("imagenes/abc", b"x", "image/png")
    assert almacenamiento.leer("imagenes/abc") == b"x"
    enlace = almacenamiento.enlace("imagenes/abc", 300).rsplit("/", 1)[1]
    assert almacenamiento.abrir_enlace(enlace) == (b"x", None)
    almacenamiento.eliminar("imagenes/abc")
    almacenamiento.eliminar("imagenes/abc")  # eliminar dos veces no falla
    with pytest.raises(ArchivoNoDisponible):
        almacenamiento.abrir_enlace(enlace)
