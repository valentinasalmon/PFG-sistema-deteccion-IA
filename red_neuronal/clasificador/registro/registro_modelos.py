"""Registro de modelos publicados (patrón Strategy, ADR-0012).

Una versión publicada es un **paquete** (una carpeta) con, como mínimo, el
modelo ONNX y su ficha, más las métricas, la configuración y el manifiesto.
Al publicar se agrega ``huellas.json`` con el SHA-256 de cada archivo; al
obtener una versión se verifica la huella del modelo antes de devolverlo.

Las versiones son **inmutables**: no se puede volver a publicar una versión
existente, porque un informe ya emitido debe poder reproducirse con el
modelo exacto que lo generó (RN29).

- ``RegistroHuggingFace``: repositorio privado de Hugging Face Hub; cada
  versión es una etiqueta ``vMAJOR.MINOR.PATCH``.
- ``RegistroLocal``: una carpeta; para la prueba de concepto y las pruebas.

Realiza: RN29, RNF24 CA4; CA16 de la funcionalidad 010.
"""

import json
import os
import re
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from clasificador.datos.manifiesto import huella_archivo

ARCHIVO_MODELO = "modelo.onnx"
ARCHIVO_FICHA = "ficha.md"
ARCHIVO_HUELLAS = "huellas.json"
ARCHIVOS_OBLIGATORIOS = (ARCHIVO_MODELO, ARCHIVO_FICHA)
_FORMATO_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


class ErrorRegistro(Exception):
    """La versión no es válida, ya existe, no existe o está alterada."""


def validar_version(version: str) -> None:
    """Exige el formato MAJOR.MINOR.PATCH."""
    if not _FORMATO_VERSION.match(version):
        raise ErrorRegistro(f"versión inválida '{version}': se espera MAJOR.MINOR.PATCH")


def sellar_paquete(directorio: Path) -> dict[str, str]:
    """Verifica los archivos obligatorios y escribe ``huellas.json``."""
    directorio = Path(directorio)
    faltantes = [nombre for nombre in ARCHIVOS_OBLIGATORIOS if not (directorio / nombre).is_file()]
    if faltantes:
        raise ErrorRegistro(f"al paquete le faltan archivos obligatorios: {faltantes}")
    huellas = {
        ruta.relative_to(directorio).as_posix(): huella_archivo(ruta)
        for ruta in sorted(directorio.rglob("*"))
        if ruta.is_file() and ruta.name != ARCHIVO_HUELLAS
    }
    (directorio / ARCHIVO_HUELLAS).write_text(
        json.dumps(huellas, indent=2, sort_keys=True), encoding="utf-8"
    )
    return huellas


def verificar_modelo(ruta_modelo: Path, ruta_huellas: Path) -> Path:
    """Comprueba que el modelo descargado no fue alterado."""
    huellas = json.loads(Path(ruta_huellas).read_text(encoding="utf-8"))
    if huella_archivo(ruta_modelo) != huellas.get(ARCHIVO_MODELO):
        raise ErrorRegistro(f"la huella de {ruta_modelo} no coincide con la registrada")
    return Path(ruta_modelo)


class RegistroModelos(ABC):
    """Interfaz común de los registros de modelos."""

    @abstractmethod
    def versiones(self) -> list[str]:
        """Versiones publicadas, ordenadas de menor a mayor."""

    @abstractmethod
    def _subir(self, version: str, directorio: Path) -> str:
        """Sube el paquete ya sellado y devuelve una referencia."""

    @abstractmethod
    def _descargar(self, version: str, nombre: str, destino: Path) -> Path:
        """Descarga un archivo de una versión."""

    def publicar(self, version: str, directorio: Path) -> str:
        """Publica un paquete como versión nueva e inmutable."""
        validar_version(version)
        if version in self.versiones():
            raise ErrorRegistro(f"la versión {version} ya existe y las versiones son inmutables")
        sellar_paquete(directorio)
        return self._subir(version, Path(directorio))

    def obtener(self, version: str, destino: Path) -> Path:
        """Descarga el modelo de una versión y verifica su huella."""
        validar_version(version)
        if version not in self.versiones():
            raise ErrorRegistro(f"la versión {version} no existe en el registro")
        destino = Path(destino)
        destino.mkdir(parents=True, exist_ok=True)
        modelo = self._descargar(version, ARCHIVO_MODELO, destino)
        huellas = self._descargar(version, ARCHIVO_HUELLAS, destino)
        return verificar_modelo(modelo, huellas)


def _clave_version(version: str) -> tuple[int, ...]:
    return tuple(int(parte) for parte in version.split("."))


class RegistroLocal(RegistroModelos):
    """Registro en una carpeta: ``<raiz>/v1.0.0/``."""

    def __init__(self, raiz: Path) -> None:
        self.raiz = Path(raiz)
        self.raiz.mkdir(parents=True, exist_ok=True)

    def versiones(self) -> list[str]:
        """Versiones presentes en la carpeta."""
        encontradas = [
            ruta.name[1:] for ruta in self.raiz.iterdir()
            if ruta.is_dir() and _FORMATO_VERSION.match(ruta.name[1:])
        ]
        return sorted(encontradas, key=_clave_version)

    def _subir(self, version: str, directorio: Path) -> str:
        destino = self.raiz / f"v{version}"
        shutil.copytree(directorio, destino)
        return str(destino)

    def _descargar(self, version: str, nombre: str, destino: Path) -> Path:
        return Path(shutil.copy2(self.raiz / f"v{version}" / nombre, destino / nombre))


class RegistroHuggingFace(RegistroModelos):
    """Registro en un repositorio privado de modelos de Hugging Face Hub.

    El *token* se toma de ``HF_TOKEN`` (secreto de Kaggle o del servidor);
    nunca de un archivo del repositorio.
    """

    def __init__(self, repositorio: str, cliente: Any = None) -> None:
        if cliente is None:
            # pylint: disable-next=import-outside-toplevel
            from huggingface_hub import HfApi

            cliente = HfApi(token=os.environ.get("HF_TOKEN"))
        self.repositorio = repositorio
        self.cliente = cliente

    def versiones(self) -> list[str]:
        """Versiones según las etiquetas ``vX.Y.Z`` del repositorio."""
        referencias = self.cliente.list_repo_refs(self.repositorio, repo_type="model")
        nombres = [etiqueta.name[1:] for etiqueta in referencias.tags]
        return sorted((v for v in nombres if _FORMATO_VERSION.match(v)), key=_clave_version)

    def _subir(self, version: str, directorio: Path) -> str:
        confirmacion = self.cliente.upload_folder(
            repo_id=self.repositorio,
            folder_path=str(directorio),
            repo_type="model",
            commit_message=f"Publicar la versión {version} del clasificador",
        )
        self.cliente.create_tag(
            self.repositorio, tag=f"v{version}", revision=confirmacion.oid, repo_type="model"
        )
        return f"{self.repositorio}@v{version}"

    def _descargar(self, version: str, nombre: str, destino: Path) -> Path:
        return Path(
            self.cliente.hf_hub_download(
                repo_id=self.repositorio,
                filename=nombre,
                revision=f"v{version}",
                repo_type="model",
                local_dir=str(destino / f"v{version}"),
            )
        )
