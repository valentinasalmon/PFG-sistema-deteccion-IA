"""Pruebas del conjunto de PyTorch y de las aumentaciones (tarea T10)."""

import torch
from PIL import Image

from clasificador.datos.aumentacion import AumentacionEntrenamiento, TransformacionEvaluacion
from clasificador.datos.conjunto import ConjuntoImagenes, filtrar_particion
from clasificador.datos.manifiesto import RegistroImagen
from clasificador.inferencia.preprocesamiento import preprocesar


def _registros(directorio_imagenes, raiz):
    return [
        RegistroImagen(
            "0" * 64, str(imagen.ruta.relative_to(raiz)), imagen.clase, "prueba",
            imagen.generador, "entrenamiento" if indice % 4 else "validacion",
        )
        for indice, imagen in enumerate(directorio_imagenes)
    ]


def test_el_conjunto_devuelve_tensores_y_clases(directorio_imagenes, tmp_path):
    """Cada elemento es ([3, 224, 224], [1]) con la clase del manifiesto."""
    registros = _registros(directorio_imagenes, tmp_path)
    conjunto = ConjuntoImagenes(registros, tmp_path, TransformacionEvaluacion())
    assert len(conjunto) == 40
    for indice in (0, 1):
        tensor, clase = conjunto[indice]
        assert tensor.shape == (3, 224, 224)
        assert clase.item() == registros[indice].clase


def test_filtrar_particion(directorio_imagenes, tmp_path):
    """Se separan las particiones del manifiesto."""
    registros = _registros(directorio_imagenes, tmp_path)
    assert len(filtrar_particion(registros, "validacion")) == 10
    assert len(filtrar_particion(registros, "entrenamiento")) == 30


def test_las_aumentaciones_son_reproducibles_con_semilla():
    """Con la misma semilla de PyTorch se obtiene el mismo tensor."""
    imagen = Image.effect_noise((400, 300), 40).convert("RGB")
    aumentacion = AumentacionEntrenamiento(probabilidad_jpeg=1.0, probabilidad_escala=1.0)
    torch.manual_seed(5)
    primero = aumentacion(imagen)
    torch.manual_seed(5)
    segundo = aumentacion(imagen)
    torch.manual_seed(6)
    tercero = aumentacion(imagen)
    assert torch.equal(primero, segundo)
    assert not torch.equal(primero, tercero)


def test_las_aumentaciones_toleran_imagenes_chicas_y_con_transparencia():
    """La salida siempre tiene el tamaño de entrada del modelo."""
    aumentacion = AumentacionEntrenamiento(probabilidad_jpeg=1.0, probabilidad_escala=1.0)
    for imagen in (Image.new("RGBA", (100, 50)), Image.new("L", (1500, 300))):
        assert aumentacion(imagen).shape == (3, 224, 224)


def test_la_evaluacion_usa_el_recorte_central_de_la_inferencia():
    """El tensor de validación es el quinto recorte del contrato de inferencia."""
    imagen = Image.effect_noise((500, 400), 30).convert("RGB")
    esperado = torch.from_numpy(preprocesar(imagen)[4])
    assert torch.equal(TransformacionEvaluacion()(imagen), esperado)
