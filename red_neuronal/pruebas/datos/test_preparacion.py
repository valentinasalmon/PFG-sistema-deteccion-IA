"""Pruebas de la preparación y partición de datos (tarea T08)."""

from collections import Counter

import pytest
from PIL import Image

from clasificador.configuracion import ConfiguracionDatos, ConfiguracionFuente
from clasificador.datos.manifiesto import RegistroImagen, huella_archivo, huella_manifiesto
from clasificador.datos.preparacion import normalizar_imagen, particionar, preparar
from clasificador.datos.validacion import validar


def _configuracion(**cambios):
    fuente = ConfiguracionFuente(
        nombre="prueba", tipo="carpeta_local", ruta="/tmp", cantidad_reales=1, licencia="propia"
    )
    valores = {"fuentes": [fuente], "lado_menor": (224, 300), "calidad_jpeg": (80, 90)}
    valores.update(cambios)
    return ConfiguracionDatos(**valores)


@pytest.fixture
def registros_crudos(directorio_imagenes, tmp_path):
    """Registros del manifiesto crudo de las imágenes de prueba."""
    return [
        RegistroImagen(
            huella_archivo(imagen.ruta),
            str(imagen.ruta.relative_to(tmp_path)),
            imagen.clase,
            "prueba",
            imagen.generador,
        )
        for imagen in directorio_imagenes
    ], tmp_path


def test_la_misma_semilla_produce_el_mismo_manifiesto(registros_crudos, tmp_path):
    """Preparar dos veces con la misma semilla da exactamente el mismo conjunto (CA7)."""
    registros, raiz = registros_crudos
    primero = preparar(registros, raiz, tmp_path / "uno", _configuracion(), semilla=7)
    segundo = preparar(list(reversed(registros)), raiz, tmp_path / "dos", _configuracion(), 7)
    assert huella_manifiesto(primero) == huella_manifiesto(segundo)


def test_otra_semilla_produce_otra_particion(registros_crudos, tmp_path):
    """La semilla efectivamente controla el resultado."""
    registros, raiz = registros_crudos
    primero = preparar(registros, raiz, tmp_path / "uno", _configuracion(), semilla=1)
    segundo = preparar(registros, raiz, tmp_path / "dos", _configuracion(), semilla=2)
    assert huella_manifiesto(primero) != huella_manifiesto(segundo)


def test_ambas_clases_quedan_con_el_mismo_formato_y_tamanios(registros_crudos, tmp_path):
    """Después de normalizar no hay diferencias de formato entre clases (CA5)."""
    registros, raiz = registros_crudos
    destino = tmp_path / "preparado"
    preparados = preparar(registros, raiz, destino, _configuracion(), semilla=3)
    formatos, lados = Counter(), {0: [], 1: []}
    for registro in preparados:
        with Image.open(destino / registro.ruta_relativa) as imagen:
            formatos[(registro.clase, imagen.format, imagen.mode)] += 1
            lados[registro.clase].append(min(imagen.size))
    assert set(formatos) == {(0, "JPEG", "RGB"), (1, "JPEG", "RGB")}
    for clase in (0, 1):
        assert 224 <= min(lados[clase]) and max(lados[clase]) <= 300


def test_el_conjunto_preparado_pasa_la_validacion(registros_crudos, tmp_path):
    """La salida de preparar es un conjunto válido y balanceado."""
    registros, raiz = registros_crudos
    destino = tmp_path / "preparado"
    preparados = preparar(registros, raiz, destino, _configuracion(), semilla=3)
    resultado = validar(preparados, destino, desbalance_tolerado=0.2)
    assert resultado.es_valido, resultado.errores


def test_los_generadores_reservados_van_a_no_visto(registros_crudos, tmp_path):
    """Un generador reservado nunca aparece en entrenamiento ni validación (CA6)."""
    registros, raiz = registros_crudos
    configuracion = _configuracion(generadores_reservados=["generador_b"])
    preparados = preparar(registros, raiz, tmp_path / "p", configuracion, semilla=3)
    particiones = {r.particion for r in preparados if r.generador == "generador_b"}
    assert particiones == {"no_visto"}
    assert any(r.particion == "entrenamiento" for r in preparados if r.generador == "generador_a")


def test_la_particion_respeta_las_proporciones_por_grupo():
    """Cada grupo (clase, generador) se reparte 80/10/10."""
    registros = [
        RegistroImagen(f"{i:064x}", f"{i}.jpg", i % 2, "f", f"g{i % 2}") for i in range(200)
    ]
    configuracion = _configuracion()
    particionados = particionar(registros, configuracion.proporciones, [], semilla=0)
    conteo = Counter((r.clase, r.particion) for r in particionados)
    for clase in (0, 1):
        assert conteo[(clase, "entrenamiento")] == 80
        assert conteo[(clase, "validacion")] == 10
        assert conteo[(clase, "prueba")] == 10


def test_normalizar_compone_la_transparencia_sobre_blanco(tmp_path):
    """Un píxel totalmente transparente queda blanco, no negro."""
    origen = tmp_path / "transparente.png"
    Image.new("RGBA", (300, 300), (0, 0, 0, 0)).save(origen)
    destino = tmp_path / "salida.jpg"
    normalizar_imagen(origen, destino, lado_menor=224, calidad_jpeg=95)
    with Image.open(destino) as imagen:
        assert imagen.mode == "RGB"
        assert min(imagen.getpixel((112, 112))) > 240
