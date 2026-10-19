"""Etapa ``evaluar``: ejecuta el modelo ONNX sobre un manifiesto.

Usa el mismo ``PredictorOnnx`` que el backend, de modo que las métricas
reportadas son las del modelo que realmente se publica (CA14). Produce:

- ``metricas.json``: total, por partición, por generador y por variante.
- ``predicciones.csv``: la probabilidad de cada imagen, para analizar errores.
- ``curva_roc.png`` y ``matriz_confusion.png``: gráficos para la ficha.

Realiza: RNF24 CA3; CA10 a CA13 de la funcionalidad 010.
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from clasificador.datos.manifiesto import RegistroImagen
from clasificador.evaluacion.metricas import (
    UMBRAL_REPORTE,
    calcular_metricas,
    metricas_por_generador,
    metricas_por_grupo,
)
from clasificador.inferencia.predictor import PredictorOnnx


@dataclass(frozen=True)
class InformeMetricas:
    """Resultado de una evaluación, listo para guardar y para la ficha."""

    version_modelo: str
    total: dict
    por_particion: dict[str, dict]
    por_generador: dict[str, dict]
    por_variante: dict[str, dict]

    def a_diccionario(self) -> dict:
        """Representación serializable a JSON."""
        return {
            "version_modelo": self.version_modelo,
            "umbral_reporte": UMBRAL_REPORTE,
            "total": self.total,
            "por_particion": self.por_particion,
            "por_generador": self.por_generador,
            "por_variante": self.por_variante,
        }


def predecir_registros(
    predictor: PredictorOnnx, registros: list[RegistroImagen], raiz: Path
) -> np.ndarray:
    """Probabilidad de cada imagen del manifiesto, en el mismo orden."""
    probabilidades = []
    for registro in registros:
        with Image.open(Path(raiz) / registro.ruta_relativa) as imagen:
            probabilidades.append(predictor.predecir(imagen).probabilidad_sintetica)
    return np.asarray(probabilidades, dtype=float)


def _guardar_graficos(etiquetas: np.ndarray, probabilidades: np.ndarray, directorio: Path) -> None:
    """Curva ROC y matriz de confusión en PNG."""
    # pylint: disable=import-outside-toplevel
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay

    if len(np.unique(etiquetas)) == 2:
        figura, eje = plt.subplots(figsize=(5, 5))
        RocCurveDisplay.from_predictions(etiquetas, probabilidades, ax=eje, name="Clasificador")
        eje.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Azar")
        eje.set_xlabel("Tasa de falsos positivos")
        eje.set_ylabel("Tasa de verdaderos positivos")
        eje.set_title("Curva ROC")
        eje.legend(loc="lower right")
        figura.savefig(directorio / "curva_roc.png", dpi=120, bbox_inches="tight")
        plt.close(figura)

    figura, eje = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(
        etiquetas,
        (probabilidades >= UMBRAL_REPORTE).astype(int),
        labels=[0, 1],
        display_labels=["Real", "Sintética"],
        ax=eje,
        colorbar=False,
    )
    eje.set_xlabel("Predicción (umbral 0,5, solo para reportar)")
    eje.set_ylabel("Clase verdadera")
    eje.set_title("Matriz de confusión")
    figura.savefig(directorio / "matriz_confusion.png", dpi=120, bbox_inches="tight")
    plt.close(figura)


def _guardar_predicciones(
    registros: list[RegistroImagen], probabilidades: np.ndarray, ruta: Path
) -> None:
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(
            ["ruta_relativa", "clase", "generador", "variante", "particion", "probabilidad"]
        )
        for registro, probabilidad in zip(registros, probabilidades):
            escritor.writerow(
                [
                    registro.ruta_relativa, registro.clase, registro.generador,
                    registro.variante, registro.particion, f"{probabilidad:.6f}",
                ]
            )


def evaluar(
    predictor: PredictorOnnx, registros: list[RegistroImagen], raiz: Path, directorio_salida: Path
) -> InformeMetricas:
    """Etapa ``evaluar``: predice, calcula las métricas y guarda los resultados."""
    directorio_salida = Path(directorio_salida)
    directorio_salida.mkdir(parents=True, exist_ok=True)
    probabilidades = predecir_registros(predictor, registros, raiz)
    etiquetas = np.asarray([registro.clase for registro in registros])
    informe = InformeMetricas(
        version_modelo=predictor.version,
        total=calcular_metricas(etiquetas, probabilidades),
        por_particion=metricas_por_grupo(
            etiquetas, probabilidades, [r.particion for r in registros]
        ),
        por_generador=metricas_por_generador(
            etiquetas, probabilidades, [r.generador for r in registros]
        ),
        por_variante=metricas_por_grupo(etiquetas, probabilidades, [r.variante for r in registros]),
    )
    (directorio_salida / "metricas.json").write_text(
        json.dumps(informe.a_diccionario(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _guardar_predicciones(registros, probabilidades, directorio_salida / "predicciones.csv")
    _guardar_graficos(etiquetas, probabilidades, directorio_salida)
    return informe
