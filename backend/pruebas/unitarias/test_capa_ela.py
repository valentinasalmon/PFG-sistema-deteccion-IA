"""Pruebas de la capa de análisis de niveles de error (funcionalidad 011).

Las imágenes se generan en memoria: una "foto" sintética con gradientes y
ruido, guardada en JPEG, y la misma foto con una región pegada desde otra
imagen. Nunca se usan imágenes de casos reales.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import io
from datetime import datetime

import numpy as np
import pytest
from PIL import Image, ImageFilter

from app.analisis.base import (
    RECOMENDACION,
    TERMINOS_DE_VEREDICTO,
    CapaNoDisponible,
    ContextoImagen,
)
from app.analisis.ela import (
    MAXIMO_REGIONES_INFORMADAS,
    CapaELA,
    Region,
    buscar_regiones,
    describir_ubicacion,
    estimar_calidad_jpeg,
)

CARGA = datetime(2026, 10, 20, 12, 0)


def _foto(ancho=1024, alto=768, semilla=1):
    """Imagen sintética con gradientes suaves y ruido, parecida a una foto."""
    azar = np.random.default_rng(semilla)
    fila, columna = np.mgrid[0:alto, 0:ancho]
    canales = [128 + 80 * np.sin(columna / 90 + c) * np.cos(fila / 70) for c in (0, 1, 2)]
    pixeles = np.stack(canales, axis=2) + azar.normal(0, 6, (alto, ancho, 3))
    imagen = Image.fromarray(np.clip(pixeles, 0, 255).astype(np.uint8))
    return imagen.filter(ImageFilter.GaussianBlur(1))


def _jpeg(imagen, calidad):
    salida = io.BytesIO()
    imagen.save(salida, "JPEG", quality=calidad)
    return salida.getvalue()


def _contexto(formato="jpeg", tamanio=(1024, 768)):
    return ContextoImagen(formato, tamanio[0], tamanio[1], CARGA)


@pytest.fixture(scope="module")
def original():
    """Foto sintética sin editar, en JPEG al 80 %."""
    return _jpeg(_foto(), 80)


@pytest.fixture(scope="module")
def empalme(original):
    """La misma foto con una región de otra imagen pegada y guardada al 90 %."""
    imagen = Image.open(io.BytesIO(original)).convert("RGB")
    imagen.paste(_foto(semilla=7).crop((0, 0, 200, 160)), (500, 300))
    return _jpeg(imagen, 90)


# --- Resultado (RF41) ---

def test_imagen_sin_editar_no_senala_regiones(original):
    """CA2: comportamiento homogéneo, nivel 0 y la aclaración de que no descarta ediciones."""
    resultado = CapaELA().analizar(original, _contexto())

    assert resultado.nivel == 0
    assert not resultado.anomalias
    assert resultado.detalle["regiones"] == 0
    assert "no descarta ediciones" in resultado.conclusion
    assert resultado.conclusion.endswith(RECOMENDACION)


def test_region_pegada_se_senala_con_su_ubicacion(original, empalme):
    """CA1: la región pegada aparece cerca de donde se pegó y sube el nivel."""
    capa = CapaELA()
    resultado = capa.analizar(empalme, _contexto())

    assert resultado.nivel > capa.analizar(original, _contexto()).nivel
    assert 1 <= len(resultado.anomalias) <= MAXIMO_REGIONES_INFORMADAS
    assert {a.severidad for a in resultado.anomalias} <= {"moderado", "debil"}
    assert any(a.severidad == "moderado" for a in resultado.anomalias)
    descripcion = resultado.anomalias[0].descripcion
    # La región se pegó entre el 49 % y el 68 % del ancho, y entre el 39 % y el 60 % del alto.
    izquierda = int(descripcion.split("% del borde izquierdo")[0].rsplit(" ", 2)[-2])
    arriba = int(descripcion.split("% del borde superior")[0].rsplit(" ", 2)[-2])
    assert 45 <= izquierda <= 70 and 35 <= arriba <= 62
    assert "también a un borde" in descripcion


def test_el_resultado_incluye_el_mapa_y_la_tabla(empalme):
    """CA4: mapa PNG reducido y datos de la técnica."""
    resultado = CapaELA().analizar(empalme, _contexto())

    mapa = Image.open(io.BytesIO(resultado.imagen))
    assert mapa.format == "PNG" and max(mapa.size) <= 900
    # El recuadro rojo de la región está dibujado sobre el mapa.
    assert (np.asarray(mapa)[:, :, 0] > 200).any()
    tabla = {fila["campo"]: fila["valor"] for fila in resultado.detalle["tabla"]}
    assert tabla["Calidad JPEG estimada"] == "90 %"
    assert tabla["Recompresión de referencia"] == "JPEG al 90 %"
    assert tabla["Bloques analizados"] == "3072 de 16 × 16 píxeles"


def test_png_tiene_validez_limitada_y_solo_indicios_debiles(empalme):
    """CA3: en PNG se aclara la limitación y no hay indicios moderados."""
    salida = io.BytesIO()
    Image.open(io.BytesIO(empalme)).save(salida, "PNG")

    resultado = CapaELA().analizar(salida.getvalue(), _contexto("png"))

    assert "validez limitada" in resultado.conclusion
    assert all(a.severidad == "debil" for a in resultado.anomalias)
    assert resultado.nivel <= 20
    tabla = {fila["campo"]: fila["valor"] for fila in resultado.detalle["tabla"]}
    assert tabla["Calidad JPEG estimada"] == "no corresponde"


def test_imagen_muy_chica_no_se_analiza():
    """Menos de 8 bloques por lado: se informa el motivo sin nivel de indicio."""
    resultado = CapaELA().analizar(_jpeg(_foto(100, 300), 90), _contexto(tamanio=(100, 300)))

    assert resultado.nivel == 0
    assert resultado.imagen is None
    assert [a.severidad for a in resultado.anomalias] == ["neutro"]
    assert "demasiado chica" in resultado.conclusion


def test_imagen_ilegible_deja_la_capa_no_disponible():
    """CA7 (RN26): el servicio la informa como "No disponible"."""
    with pytest.raises(CapaNoDisponible, match="No se pudo leer"):
        CapaELA().analizar(b"no es una imagen", _contexto())


def test_las_conclusiones_no_emiten_veredictos(original, empalme):
    """CA6 (RN27)."""
    for contenido in (original, empalme):
        resultado = CapaELA().analizar(contenido, _contexto())
        for texto in (resultado.conclusion, *(a.descripcion for a in resultado.anomalias)):
            assert not any(t in texto.lower().split() for t in TERMINOS_DE_VEREDICTO), texto


def test_version_registra_bibliotecas_y_calidad():
    """CA6 (RN29)."""
    version = CapaELA().version()

    assert version.startswith("1.0 (Pillow ")
    assert "NumPy" in version and "recompresión JPEG al 90 %" in version


# --- Funciones auxiliares ---

@pytest.mark.parametrize("calidad", [50, 75, 90, 95])
def test_estimar_calidad_jpeg(calidad):
    """La calidad estimada coincide con la usada al guardar, con un margen chico."""
    imagen = Image.open(io.BytesIO(_jpeg(_foto(256, 256), calidad)))

    assert abs(estimar_calidad_jpeg(imagen) - calidad) <= 2


def test_sin_tablas_de_cuantizacion_no_hay_calidad():
    """Un PNG no tiene tablas de cuantización."""
    assert estimar_calidad_jpeg(Image.new("RGB", (8, 8))) is None


def test_buscar_regiones_descarta_las_chicas_y_ordena():
    """Las regiones de menos de 6 bloques se consideran ruido."""
    desvios = np.zeros((20, 20))
    desvios[2:4, 2:4] = 20  # 4 bloques: ruido
    desvios[10:13, 10:14] = 8  # 12 bloques
    desvios[15:17, 0:4] = 30  # 8 bloques, más llamativa

    regiones = buscar_regiones(desvios)

    assert [(r.bloques, round(r.desvio)) for r in regiones] == [(8, 30), (12, 8)]
    assert (regiones[1].fila, regiones[1].columna, regiones[1].alto, regiones[1].ancho) == (
        10, 10, 3, 4,
    )


def test_describir_ubicacion():
    """La ubicación se expresa en porcentajes de la imagen."""
    region = Region(fila=10, columna=25, alto=5, ancho=10, bloques=50, desvio=12.0)

    assert describir_ubicacion(region, 50, 100) == (
        "una zona de aproximadamente 10 % × 10 % de la imagen, a 25 % del borde izquierdo "
        "y 20 % del borde superior"
    )
