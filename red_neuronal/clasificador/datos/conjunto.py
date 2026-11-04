"""Conjunto de datos de PyTorch construido a partir del manifiesto.

Realiza: CA2 de la funcionalidad 010.
"""

from collections.abc import Callable
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset

from clasificador.datos.manifiesto import RegistroImagen


def filtrar_particion(registros: list[RegistroImagen], particion: str) -> list[RegistroImagen]:
    """Devuelve solo los registros de una partición."""
    return [registro for registro in registros if registro.particion == particion]


class ConjuntoImagenes(Dataset):
    """Entrega pares (imagen transformada, clase) para entrenar o validar.

    La clase se devuelve como tensor ``float32`` de forma ``[1]``, que es lo
    que espera la función de pérdida binaria con *logits*.
    """

    def __init__(
        self,
        registros: list[RegistroImagen],
        raiz: Path,
        transformacion: Callable[[Image.Image], torch.Tensor],
    ) -> None:
        self.registros = list(registros)
        self.raiz = Path(raiz)
        self.transformacion = transformacion

    def __len__(self) -> int:
        return len(self.registros)

    def __getitem__(self, indice: int) -> tuple[torch.Tensor, torch.Tensor]:
        registro = self.registros[indice]
        with Image.open(self.raiz / registro.ruta_relativa) as imagen:
            imagen.load()
            tensor = self.transformacion(imagen)
        return tensor, torch.tensor([float(registro.clase)], dtype=torch.float32)
