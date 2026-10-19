"""Pruebas de las fuentes de datos y de la etapa obtener (tarea T09).

La fuente de Hugging Face se prueba con un cargador simulado en memoria:
las pruebas nunca acceden a la red (constitución, sección 5).
"""

import io
import shutil

import pytest
from PIL import Image

from clasificador.configuracion import ConfiguracionDatos, ConfiguracionFuente
from clasificador.datos.fuentes import (
    ErrorFuente,
    FuenteCarpetaLocal,
    FuenteHuggingFace,
    crear_fuente,
)
from clasificador.datos.obtencion import ErrorObtencion, obtener, obtener_de_fuente
from clasificador.datos.validacion import validar


def _bytes_imagen(color, formato="PNG"):
    bufer = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(bufer, format=formato)
    return bufer.getvalue()


def _config_hf(**cambios):
    valores = {
        "nombre": "hf_simulado",
        "tipo": "hugging_face",
        "conjunto": "alguien/conjunto",
        "columna_imagen": "imagen",
        "columna_clase": "etiqueta",
        "valores_sinteticos": ["falsa"],
        "columna_generador": "modelo",
        "cantidad_reales": 2,
        "cantidad_sinteticas": 2,
        "licencia": "cc-by-nc",
    }
    valores.update(cambios)
    return ConfiguracionFuente(**valores)


class _ConjuntoSimulado(list):
    """Imita un conjunto en streaming: una lista con el método shuffle."""

    def shuffle(self, seed, buffer_size):  # pylint: disable=unused-argument
        """Mezcla de forma determinista según la semilla."""
        return _ConjuntoSimulado(sorted(self, key=lambda fila: hash((seed, fila["id"]))))


def _filas():
    filas = []
    for indice in range(6):
        sintetica = indice % 2 == 1
        filas.append(
            {
                "id": indice,
                "imagen": {"bytes": _bytes_imagen((indice * 40, 0, 0)), "path": None},
                "etiqueta": "falsa" if sintetica else "real",
                "modelo": "sdxl" if sintetica else "",
            }
        )
    return _ConjuntoSimulado(filas)


def test_hugging_face_convierte_las_filas_en_ejemplos():
    """Se detectan la clase, el generador y el formato real."""
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: _filas())
    ejemplos = list(fuente.iterar())
    assert len(ejemplos) == 6
    assert {(e.clase, e.generador) for e in ejemplos} == {(0, "real"), (1, "sdxl")}
    assert {e.extension for e in ejemplos} == {".png"}


def test_hugging_face_usa_el_nombre_de_la_fuente_si_no_hay_generador():
    """Sin columna de generador, la imagen sintética se atribuye a la fuente."""
    fuente = FuenteHuggingFace(
        _config_hf(columna_generador=None), semilla=0, cargador=lambda _: _filas()
    )
    generadores = {e.generador for e in fuente.iterar() if e.clase == 1}
    assert generadores == {"hf_simulado"}


@pytest.mark.parametrize(
    "valor",
    [
        _bytes_imagen((1, 2, 3), "JPEG"),
        Image.new("RGB", (8, 8)),
    ],
)
def test_hugging_face_acepta_bytes_o_imagenes_decodificadas(valor):
    """La columna de imagen puede venir en distintas formas."""
    fila = {"id": 0, "imagen": valor, "etiqueta": "real"}
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: [fila])
    assert next(fuente.iterar()).clase == 0


def test_hugging_face_informa_una_columna_faltante():
    """El error indica qué columnas sí existen, para corregir la receta."""
    fila = {"id": 0, "img": b"", "etiqueta": "real"}
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: [fila])
    with pytest.raises(ErrorFuente, match="columnas disponibles"):
        next(fuente.iterar())


@pytest.mark.parametrize("valor", [b"no es una imagen", 12345])
def test_hugging_face_rechaza_contenido_invalido(valor):
    """Bytes que no son imagen o tipos desconocidos se rechazan."""
    fila = {"id": 0, "imagen": valor, "etiqueta": "real"}
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: [fila])
    with pytest.raises(ErrorFuente):
        next(fuente.iterar())


@pytest.fixture
def carpeta_propia(tmp_path):
    """Conjunto propio con la estructura <clase>/<generador>/<variante>/."""
    raiz = tmp_path / "propio"
    for clase, generador, variante, color in [
        ("real", "celular", "original", (10, 10, 10)),
        ("real", "celular", "whatsapp", (20, 20, 20)),
        ("sintetica", "gemini", "original", (30, 30, 30)),
        ("sintetica", "chatgpt", "editada", (40, 40, 40)),
    ]:
        carpeta = raiz / clase / generador / variante
        carpeta.mkdir(parents=True)
        (carpeta / "foto.jpg").write_bytes(_bytes_imagen(color, "JPEG"))
    (raiz / "LEEME.txt").write_text("se ignora", encoding="utf-8")
    return raiz


def _config_local(ruta):
    return ConfiguracionFuente(
        nombre="propio", tipo="carpeta_local", ruta=ruta,
        cantidad_reales=2, cantidad_sinteticas=2, licencia="propia",
    )


def test_carpeta_local_lee_clase_generador_y_variante(carpeta_propia):
    """La estructura de carpetas define las etiquetas."""
    ejemplos = list(FuenteCarpetaLocal(_config_local(carpeta_propia)).iterar())
    assert {(e.clase, e.generador, e.variante) for e in ejemplos} == {
        (0, "celular", "original"),
        (0, "celular", "whatsapp"),
        (1, "gemini", "original"),
        (1, "chatgpt", "editada"),
    }


def test_carpeta_local_rechaza_una_estructura_incorrecta(carpeta_propia):
    """Una imagen fuera de la estructura se informa en lugar de etiquetarse mal."""
    shutil.copy(next(carpeta_propia.rglob("*.jpg")), carpeta_propia / "suelta.jpg")
    with pytest.raises(ErrorFuente, match="estructura"):
        list(FuenteCarpetaLocal(_config_local(carpeta_propia)).iterar())


def test_carpeta_local_inexistente_falla(tmp_path):
    """Se informa la carpeta que falta."""
    with pytest.raises(ErrorFuente, match="no existe"):
        list(FuenteCarpetaLocal(_config_local(tmp_path / "nada")).iterar())


def test_la_fabrica_crea_la_fuente_segun_el_tipo(tmp_path):
    """crear_fuente elige la implementación por la configuración."""
    assert isinstance(crear_fuente(_config_hf(), 0), FuenteHuggingFace)
    assert isinstance(crear_fuente(_config_local(tmp_path), 0), FuenteCarpetaLocal)


def test_obtener_toma_la_cantidad_pedida_por_clase(tmp_path):
    """Se guardan exactamente 2 reales y 2 sintéticas, en formato original."""
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: _filas())
    registros = obtener_de_fuente(fuente, tmp_path, {0: 2, 1: 2})
    assert sorted(r.clase for r in registros) == [0, 0, 1, 1]
    assert all(r.ruta_relativa.endswith(".png") for r in registros)
    assert validar(registros, tmp_path).es_valido


def test_obtener_saltea_duplicados(tmp_path):
    """Dos filas con la misma imagen cuentan una sola vez."""
    repetida = {"bytes": _bytes_imagen((5, 5, 5))}
    filas = [{"id": i, "imagen": repetida, "etiqueta": "real"} for i in range(3)]
    filas.append({"id": 9, "imagen": {"bytes": _bytes_imagen((9, 9, 9))}, "etiqueta": "real"})
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: filas)
    registros = obtener_de_fuente(fuente, tmp_path, {0: 2, 1: 0})
    assert len({r.huella_sha256 for r in registros}) == 2


def test_obtener_falla_si_la_fuente_se_agota(tmp_path):
    """Pedir más imágenes de las que hay es un error explícito."""
    fuente = FuenteHuggingFace(_config_hf(), semilla=0, cargador=lambda _: _filas())
    with pytest.raises(ErrorObtencion, match="faltan 7 sintéticas"):
        obtener_de_fuente(fuente, tmp_path, {0: 1, 1: 10})


def test_la_etapa_obtener_recorre_todas_las_fuentes(carpeta_propia, tmp_path):
    """La etapa completa usa la configuración de datos."""
    configuracion = ConfiguracionDatos(fuentes=[_config_local(carpeta_propia)])
    registros = obtener(configuracion, tmp_path / "salida", semilla=0)
    assert len(registros) == 4
    assert {r.fuente for r in registros} == {"propio"}


def test_obtener_todas_las_imagenes_sin_cantidades(carpeta_propia, tmp_path):
    """Con cantidades=None se toma la fuente completa, sin error de agotamiento."""
    fuente = FuenteCarpetaLocal(_config_local(carpeta_propia))
    assert len(obtener_de_fuente(fuente, tmp_path / "todas", cantidades=None)) == 4


def test_hugging_face_excluye_filas_por_columna():
    """Las filas marcadas (por ejemplo, contenido explícito) se descartan."""
    filas = _filas()
    for fila in filas:
        fila["nsfw_flag"] = fila["id"] in (1, 2)
    fuente = FuenteHuggingFace(
        _config_hf(excluir={"nsfw_flag": ["True"]}), semilla=0, cargador=lambda _: filas
    )
    assert len(list(fuente.iterar())) == 4
