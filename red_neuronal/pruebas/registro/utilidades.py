"""Datos de ejemplo para las pruebas de ficha, compuerta y registro."""

from clasificador.configuracion import Configuracion
from clasificador.evaluacion.metricas import calcular_metricas, metricas_por_generador
from clasificador.registro.ficha import DatosFicha

CONFIGURACION = Configuracion.model_validate(
    {
        "nombre": "prueba",
        "datos": {
            "fuentes": [
                {
                    "nombre": "propio", "tipo": "carpeta_local", "ruta": "/tmp/propio",
                    "cantidad_reales": 2, "cantidad_sinteticas": 2, "licencia": "propia",
                }
            ],
            "generadores_reservados": ["gemini"],
        },
    }
)

_ETIQUETAS = [0, 0, 1, 1]
_PROBABILIDADES = [0.1, 0.3, 0.8, 0.95]
_GENERADORES = ["real", "real", "sdxl", "flux"]


def metricas(auc_alto: bool = True) -> dict:
    """Métricas de prueba con AUC 1 o con AUC 0."""
    probabilidades = _PROBABILIDADES if auc_alto else list(reversed(_PROBABILIDADES))
    return {
        "total": calcular_metricas(_ETIQUETAS, probabilidades),
        "por_generador": metricas_por_generador(_ETIQUETAS, probabilidades, _GENERADORES),
        "por_variante": {},
    }


def datos_ficha(**cambios) -> DatosFicha:
    """Datos completos de una ficha válida."""
    valores = {
        "version": "1.0.0",
        "fecha": "2026-10-19",
        "configuracion": CONFIGURACION,
        "huella_manifiesto": "a" * 64,
        "huella_modelo": "b" * 64,
        "resumen_datos": {"particion": {"entrenamiento": 3, "prueba": 1}},
        "entrenamiento": {"mejor_auc": 0.97, "epoca_mejor": 4},
        "temperatura": 1.3,
        "entorno": {"python": "3.11", "torch": "2.6"},
        "metricas_prueba": metricas(),
        "exportacion": {"diferencia_maxima": 1e-7, "latencia_ms_por_imagen": 42.0},
        "commit": "c" * 40,
        "id_ejecucion": "ejecucion-1",
    }
    valores.update(cambios)
    return DatosFicha(**valores)
