"""Bucle de entrenamiento con parada temprana y puntos de control.

Decisiones:

- **Pérdida**: entropía cruzada binaria sobre *logits*
  (``BCEWithLogitsLoss``), numéricamente estable.
- **Optimizador**: AdamW con tasa de aprendizaje en coseno, la combinación
  habitual para ajustar redes preentrenadas.
- **Selección del modelo**: el mejor AUC sobre la partición de validación.
  Si no mejora durante ``paciencia`` épocas, se detiene (parada temprana).
- **Puntos de control**: al final de cada época se guarda ``ultimo.pt``
  con todo el estado. Si Kaggle corta la sesión, el entrenamiento se
  reanuda desde ahí en lugar de empezar de cero.
- **Precisión mixta**: solo con GPU; acelera el entrenamiento en la T4.

Realiza: RNF24 CA1; CA7 y CA9 de la funcionalidad 010.
"""

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch import nn
from torch.utils.data import DataLoader

from clasificador.configuracion import ConfiguracionEntrenamiento
from clasificador.seguimiento.experimentos import RegistradorExperimentos

NOMBRE_ULTIMO = "ultimo.pt"
NOMBRE_MEJOR = "mejor.pt"


def fijar_semillas(semilla: int) -> None:
    """Fija las semillas de Python, numpy y PyTorch (CA7)."""
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)
    torch.cuda.manual_seed_all(semilla)
    torch.backends.cudnn.benchmark = False


def elegir_dispositivo() -> torch.device:
    """Usa la GPU si está disponible (Kaggle) y la CPU en otro caso."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def auc_seguro(etiquetas: np.ndarray, puntajes: np.ndarray) -> float:
    """AUC ROC, o NaN si hay una sola clase (el AUC no está definido)."""
    if len(np.unique(etiquetas)) < 2:
        return math.nan
    return float(roc_auc_score(etiquetas, puntajes))


@torch.no_grad()
def predecir_logits(
    modelo: nn.Module, cargador: DataLoader, dispositivo: torch.device
) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve los *logits* del modelo y las etiquetas de todo el cargador."""
    modelo.eval()
    logits, etiquetas = [], []
    for entradas, clases in cargador:
        logits.append(modelo(entradas.to(dispositivo)).float().cpu())
        etiquetas.append(clases)
    return torch.cat(logits).numpy().ravel(), torch.cat(etiquetas).numpy().ravel()


@dataclass
class ResultadoEntrenamiento:
    """Resumen del entrenamiento para el registro y la ficha del modelo."""

    ruta_mejor: Path
    mejor_auc: float
    epoca_mejor: int
    historial: list[dict[str, float]] = field(default_factory=list)


@dataclass
class EstadoEntrenamiento:
    """Lo que hay que guardar para poder reanudar un entrenamiento cortado."""

    epoca_inicial: int = 0
    mejor_auc: float = -math.inf
    epoca_mejor: int = -1
    historial: list[dict[str, float]] = field(default_factory=list)


@dataclass
class OpcionesEjecucion:
    """Opciones que no son hiperparámetros: dónde corre y cuánto (para pruebas)."""

    dispositivo: torch.device | None = None
    maximos_pasos_por_epoca: int | None = None


@dataclass
class Optimizacion:
    """Optimizador, planificador de la tasa de aprendizaje y escalador de precisión mixta."""

    optimizador: torch.optim.Optimizer
    planificador: torch.optim.lr_scheduler.LRScheduler
    escalador: torch.amp.GradScaler
    precision_mixta: bool

    @classmethod
    def crear(
        cls, modelo: nn.Module, configuracion: ConfiguracionEntrenamiento, dispositivo: torch.device
    ) -> "Optimizacion":
        """AdamW con coseno; precisión mixta solo si hay GPU."""
        optimizador = torch.optim.AdamW(
            modelo.parameters(),
            lr=configuracion.tasa_aprendizaje,
            weight_decay=configuracion.decaimiento_pesos,
        )
        precision_mixta = configuracion.precision_mixta and dispositivo.type == "cuda"
        return cls(
            optimizador=optimizador,
            planificador=torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizador, T_max=configuracion.epocas
            ),
            escalador=torch.amp.GradScaler("cuda", enabled=precision_mixta),
            precision_mixta=precision_mixta,
        )


class Entrenador:
    """Entrena un modelo con la configuración dada y guarda sus puntos de control."""

    def __init__(
        self,
        modelo: nn.Module,
        configuracion: ConfiguracionEntrenamiento,
        directorio_salida: Path,
        registrador: RegistradorExperimentos,
        opciones: OpcionesEjecucion | None = None,
    ) -> None:
        self.opciones = opciones or OpcionesEjecucion()
        if self.opciones.dispositivo is None:
            self.opciones.dispositivo = elegir_dispositivo()
        self.modelo = modelo.to(self.opciones.dispositivo)
        self.configuracion = configuracion
        self.directorio = Path(directorio_salida)
        self.directorio.mkdir(parents=True, exist_ok=True)
        self.registrador = registrador
        self.optimizacion = Optimizacion.crear(modelo, configuracion, self.opciones.dispositivo)
        self.estado = EstadoEntrenamiento()

    def _entrenar_epoca(self, cargador: DataLoader) -> float:
        """Una pasada por el conjunto de entrenamiento; devuelve la pérdida media."""
        self.modelo.train()
        dispositivo, opt = self.opciones.dispositivo, self.optimizacion
        total, cantidad = 0.0, 0
        for paso, (entradas, clases) in enumerate(cargador):
            if (
                self.opciones.maximos_pasos_por_epoca is not None
                and paso >= self.opciones.maximos_pasos_por_epoca
            ):
                break
            entradas, clases = entradas.to(dispositivo), clases.to(dispositivo)
            opt.optimizador.zero_grad(set_to_none=True)
            with torch.autocast(dispositivo.type, enabled=opt.precision_mixta):
                perdida = nn.functional.binary_cross_entropy_with_logits(
                    self.modelo(entradas), clases
                )
            opt.escalador.scale(perdida).backward()
            opt.escalador.step(opt.optimizador)
            opt.escalador.update()
            total += perdida.item() * len(entradas)
            cantidad += len(entradas)
        return total / max(cantidad, 1)

    def _guardar_punto_de_control(self, epoca: int) -> None:
        opt = self.optimizacion
        torch.save(
            {
                "epoca": epoca,
                "modelo": self.modelo.state_dict(),
                "optimizador": opt.optimizador.state_dict(),
                "planificador": opt.planificador.state_dict(),
                "escalador": opt.escalador.state_dict(),
                "mejor_auc": self.estado.mejor_auc,
                "epoca_mejor": self.estado.epoca_mejor,
                "historial": self.estado.historial,
            },
            self.directorio / NOMBRE_ULTIMO,
        )

    def reanudar(self) -> bool:
        """Carga ``ultimo.pt`` si existe. Devuelve si se reanudó."""
        ruta = self.directorio / NOMBRE_ULTIMO
        if not ruta.is_file():
            return False
        guardado = torch.load(ruta, map_location=self.opciones.dispositivo, weights_only=False)
        self.modelo.load_state_dict(guardado["modelo"])
        self.optimizacion.optimizador.load_state_dict(guardado["optimizador"])
        self.optimizacion.planificador.load_state_dict(guardado["planificador"])
        self.optimizacion.escalador.load_state_dict(guardado["escalador"])
        self.estado = EstadoEntrenamiento(
            epoca_inicial=guardado["epoca"] + 1,
            mejor_auc=guardado["mejor_auc"],
            epoca_mejor=guardado["epoca_mejor"],
            historial=guardado["historial"],
        )
        return True

    def entrenar(
        self, cargador_entrenamiento: DataLoader, cargador_validacion: DataLoader
    ) -> ResultadoEntrenamiento:
        """Entrena hasta completar las épocas o hasta la parada temprana."""
        estado = self.estado
        for epoca in range(estado.epoca_inicial, self.configuracion.epocas):
            perdida = self._entrenar_epoca(cargador_entrenamiento)
            logits, etiquetas = predecir_logits(
                self.modelo, cargador_validacion, self.opciones.dispositivo
            )
            auc = auc_seguro(etiquetas, logits)
            self.optimizacion.planificador.step()
            metricas = {"perdida_entrenamiento": perdida, "auc_validacion": auc}
            estado.historial.append({"epoca": epoca, **metricas})
            self.registrador.registrar_metricas(metricas, paso=epoca)

            if not math.isnan(auc) and auc > estado.mejor_auc:
                estado.mejor_auc, estado.epoca_mejor = auc, epoca
                torch.save(self.modelo.state_dict(), self.directorio / NOMBRE_MEJOR)
            self._guardar_punto_de_control(epoca)
            if epoca - estado.epoca_mejor >= self.configuracion.paciencia:
                break

        ruta_mejor = self.directorio / NOMBRE_MEJOR
        if not ruta_mejor.is_file():
            # Sin un AUC válido (validación de una sola clase), se conserva el último.
            torch.save(self.modelo.state_dict(), ruta_mejor)
        return ResultadoEntrenamiento(
            ruta_mejor, estado.mejor_auc, estado.epoca_mejor, estado.historial
        )
