"""Compuerta de promoción: decide si un modelo puede usarse en producción.

Un modelo solo se publica si cumple **todos** los criterios (CA15):

1. AUC sobre el conjunto de prueba de generadores conocidos ≥ umbral (CA10).
2. La salida ONNX coincide con la de PyTorch dentro de la tolerancia (CA14).
3. La ficha está completa, con todas sus secciones y la leyenda (CA17).
4. La huella del manifiesto declarada coincide con la de los datos usados.
5. El código estaba confirmado en Git: un modelo entrenado con cambios sin
   confirmar no se puede reproducir (CA7).

La decisión es automática y se informan **todos** los motivos de rechazo
juntos, para corregirlos de una vez.

Realiza: CA7, CA10, CA14, CA15 y CA17 de la funcionalidad 010.
"""

from dataclasses import dataclass, field

from clasificador.registro.ficha import secciones_faltantes


class ErrorCompuerta(Exception):
    """El modelo no cumple los criterios para publicarse."""


@dataclass(frozen=True)
class CandidatoPublicacion:
    """Evidencia reunida para decidir si un modelo se publica."""

    auc_prueba: float | None
    diferencia_onnx: float
    texto_ficha: str
    huella_manifiesto_declarada: str
    huella_manifiesto_real: str
    commit: str


@dataclass(frozen=True)
class ResultadoCompuerta:
    """Decisión de la compuerta con sus motivos."""

    motivos_rechazo: list[str] = field(default_factory=list)

    @property
    def aprobado(self) -> bool:
        """Verdadero si no hay ningún motivo de rechazo."""
        return not self.motivos_rechazo


def evaluar_compuerta(
    candidato: CandidatoPublicacion, auc_minimo: float, tolerancia_onnx: float
) -> ResultadoCompuerta:
    """Aplica los cinco criterios y devuelve todos los incumplidos."""
    motivos = []
    if candidato.auc_prueba is None:
        motivos.append("el AUC de prueba no es calculable")
    elif candidato.auc_prueba < auc_minimo:
        motivos.append(f"AUC de prueba {candidato.auc_prueba:.4f} menor al mínimo {auc_minimo}")
    if candidato.diferencia_onnx > tolerancia_onnx:
        motivos.append(
            f"la salida ONNX difiere en {candidato.diferencia_onnx:.2e} "
            f"(tolerancia {tolerancia_onnx:.0e})"
        )
    faltantes = secciones_faltantes(candidato.texto_ficha)
    if faltantes:
        motivos.append(f"a la ficha le faltan: {', '.join(faltantes)}")
    if candidato.huella_manifiesto_declarada != candidato.huella_manifiesto_real:
        motivos.append("la huella del manifiesto no coincide con la de los datos usados")
    if candidato.commit == "desconocido" or candidato.commit.endswith("-modificado"):
        motivos.append(f"el código no estaba confirmado en Git (commit: {candidato.commit})")
    return ResultadoCompuerta(motivos_rechazo=motivos)


def exigir_aprobacion(resultado: ResultadoCompuerta) -> None:
    """Detiene la publicación si la compuerta rechazó el modelo."""
    if not resultado.aprobado:
        detalle = "\n  - ".join(resultado.motivos_rechazo)
        raise ErrorCompuerta(f"la compuerta rechazó el modelo:\n  - {detalle}")
