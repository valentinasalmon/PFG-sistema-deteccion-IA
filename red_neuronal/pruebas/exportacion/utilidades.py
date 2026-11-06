"""Datos compartidos por las pruebas de exportación e inferencia."""

from clasificador.inferencia.predictor import MetadatosModelo, ParametrosEntrada

METADATOS = MetadatosModelo(
    version="0.0.1",
    arquitectura="efficientnet_b0",
    temperatura=1.5,
    entrada=ParametrosEntrada(tamanio_recorte=64),
    huella_manifiesto="a" * 64,
    commit="prueba",
)
