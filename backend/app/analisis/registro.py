"""Capas de análisis activas, en el orden en que se ejecutan.

Una capa nueva (C2PA en la 009, ELA en la 011, red neuronal en la 012) se
agrega a esta lista sin modificar las existentes (ADR-0006, RNF18).

Realiza: RF39; RNF18 (CA1).
"""
from app.analisis.credenciales_c2pa import CapaC2PA
from app.analisis.ela import CapaELA
from app.analisis.metadatos import CapaMetadatos
from app.analisis.red_neuronal import CapaRedNeuronal


def crear_capas(configuracion):
    """Instancias de las capas activas según la configuración."""
    return [
        CapaMetadatos(configuracion["RUTA_EXIFTOOL"]),
        CapaC2PA(configuracion["CARPETA_CONFIANZA_C2PA"]),
        CapaELA(),
        CapaRedNeuronal(configuracion),
    ]


# Clases de las capas activas: describen cada capa sin crear instancias (037).
CLASES_DE_CAPAS = (CapaMetadatos, CapaC2PA, CapaELA, CapaRedNeuronal)


def describir_capa(nombre):
    """Título, explicación y tipo de una capa, para mostrar su resultado (037).

    La pantalla y el informe los toman de la propia capa: una capa nueva se
    describe sola. Devuelve None si la capa ya no está activa.
    """
    for clase in CLASES_DE_CAPAS:
        if clase.nombre == nombre:
            return {"titulo": clase.titulo, "que_significa": clase.que_significa,
                    "tipo": clase.tipo_de_resultado}
    return None
