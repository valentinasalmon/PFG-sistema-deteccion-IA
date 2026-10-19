"""Registro de experimentos de entrenamiento (patrón Strategy).

Cada ejecución queda registrada con la versión del código, la
configuración, la huella del manifiesto, el entorno y las métricas, para
poder compararlas y reproducirlas (CA9).

- ``RegistradorMlflow``: MLflow con una base SQLite local (ADR-0012).
- ``RegistradorNulo``: guarda todo en memoria; se usa en las pruebas.

Realiza: RNF24 CA2; CA9 de la funcionalidad 010.
"""

import platform
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


def aplanar(diccionario: dict[str, Any], prefijo: str = "") -> dict[str, str]:
    """Convierte un diccionario anidado en claves con puntos.

    MLflow solo admite parámetros planos: ``{"entrenamiento": {"epocas": 3}}``
    pasa a ``{"entrenamiento.epocas": "3"}``.
    """
    plano: dict[str, str] = {}
    for clave, valor in diccionario.items():
        nombre = f"{prefijo}{clave}"
        if isinstance(valor, dict):
            plano.update(aplanar(valor, f"{nombre}."))
        else:
            plano[nombre] = str(valor)
    return plano


def commit_actual(directorio: Path | None = None) -> str:
    """Devuelve el commit de Git del código en uso, o 'desconocido'.

    Si hay cambios sin confirmar se agrega el sufijo '-modificado': un
    resultado obtenido con código sin confirmar no es reproducible.
    """
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=directorio, capture_output=True,
            text=True, check=True,
        ).stdout.strip()
        cambios = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=directorio,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"
    return f"{commit}-modificado" if cambios else commit


def describir_entorno() -> dict[str, str]:
    """Versiones de Python y bibliotecas, y el dispositivo de cálculo."""
    entorno = {"python": sys.version.split()[0], "plataforma": platform.platform()}
    try:
        # pylint: disable-next=import-outside-toplevel
        import torch

        entorno["torch"] = torch.__version__
        entorno["dispositivo"] = (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
        )
    except ImportError:  # pragma: no cover - torch siempre está en el entrenamiento
        entorno["torch"] = "no instalado"
    return entorno


class RegistradorExperimentos(ABC):
    """Interfaz común para registrar una ejecución de entrenamiento."""

    @abstractmethod
    def iniciar(self, nombre: str, parametros: dict[str, Any]) -> str:
        """Abre una ejecución, registra sus parámetros y devuelve su identificador."""

    @abstractmethod
    def registrar_metricas(self, metricas: dict[str, float], paso: int | None = None) -> None:
        """Registra métricas numéricas, opcionalmente asociadas a un paso (época)."""

    @abstractmethod
    def registrar_artefacto(self, ruta: Path) -> None:
        """Adjunta un archivo a la ejecución (gráfico, ficha, configuración)."""

    @abstractmethod
    def finalizar(self, exitosa: bool = True) -> None:
        """Cierra la ejecución indicando si terminó bien."""


class RegistradorNulo(RegistradorExperimentos):
    """Registrador en memoria, para pruebas y ejecuciones descartables."""

    def __init__(self) -> None:
        self.parametros: dict[str, str] = {}
        self.metricas: list[tuple[int | None, dict[str, float]]] = []
        self.artefactos: list[Path] = []
        self.estado = "sin_iniciar"

    def iniciar(self, nombre: str, parametros: dict[str, Any]) -> str:
        """Guarda los parámetros y devuelve un identificador fijo."""
        self.parametros = aplanar(parametros)
        self.estado = "en_curso"
        return f"nulo-{nombre}"

    def registrar_metricas(self, metricas: dict[str, float], paso: int | None = None) -> None:
        """Agrega las métricas a la lista en memoria."""
        self.metricas.append((paso, dict(metricas)))

    def registrar_artefacto(self, ruta: Path) -> None:
        """Agrega la ruta a la lista en memoria."""
        self.artefactos.append(Path(ruta))

    def finalizar(self, exitosa: bool = True) -> None:
        """Marca el estado final."""
        self.estado = "finalizada" if exitosa else "fallida"


class RegistradorMlflow(RegistradorExperimentos):
    """Registrador sobre MLflow con una base SQLite local, sin servidor.

    Todo queda en un único directorio (``mlflow.db`` más la carpeta
    ``artefactos/``), que en Kaggle forma parte de la salida del cuaderno y
    se empaqueta con cada versión publicada. Para comparar ejecuciones:
    ``mlflow ui --backend-store-uri sqlite:///<directorio>/mlflow.db``.
    Se usa SQLite porque MLflow dejó el almacén de archivos planos en modo
    de mantenimiento (ADR-0012).
    """

    def __init__(self, directorio: Path, experimento: str = "clasificador_sintetico") -> None:
        # pylint: disable-next=import-outside-toplevel
        import mlflow

        self._mlflow = mlflow
        self.directorio = Path(directorio).resolve()
        self.directorio.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"sqlite:///{self.directorio / 'mlflow.db'}")
        if mlflow.get_experiment_by_name(experimento) is None:
            mlflow.create_experiment(
                experimento, artifact_location=(self.directorio / "artefactos").as_uri()
            )
        mlflow.set_experiment(experimento)

    def iniciar(self, nombre: str, parametros: dict[str, Any]) -> str:
        """Abre la ejecución en MLflow y registra los parámetros aplanados."""
        ejecucion = self._mlflow.start_run(run_name=nombre)
        self._mlflow.log_params(aplanar(parametros))
        return ejecucion.info.run_id

    def registrar_metricas(self, metricas: dict[str, float], paso: int | None = None) -> None:
        """Registra las métricas en la ejecución activa."""
        self._mlflow.log_metrics({clave: float(valor) for clave, valor in metricas.items()}, paso)

    def registrar_artefacto(self, ruta: Path) -> None:
        """Copia el archivo a los artefactos de la ejecución."""
        self._mlflow.log_artifact(str(ruta))

    def finalizar(self, exitosa: bool = True) -> None:
        """Cierra la ejecución con estado FINISHED o FAILED."""
        self._mlflow.end_run(status="FINISHED" if exitosa else "FAILED")
