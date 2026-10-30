"""Pruebas de la exploración de candidatos (tarea T25).

El acceso a Hugging Face se reemplaza por un inspector simulado en memoria:
las pruebas nunca acceden a la red (constitución, sección 5).
"""

import io
import json

import pytest
import yaml
from PIL import Image

from clasificador.configuracion import ConfiguracionFuente, ErrorConfiguracion
from clasificador.datos.exploracion import (
    Candidato,
    ErrorInspeccion,
    InformacionConjunto,
    InspectorConjuntos,
    ListaCandidatos,
    cargar_candidatos,
    describir_imagen,
    estimar_calidad_jpeg,
    explorar,
    explorar_candidato,
    licencia_verificable,
    proponer_fuente,
    tabla_markdown,
)


def _bytes(formato, calidad=None, tamanio=(64, 48)):
    bufer = io.BytesIO()
    opciones = {"quality": calidad} if calidad else {}
    Image.new("RGB", tamanio, (120, 30, 200)).save(bufer, format=formato, **opciones)
    return bufer.getvalue()


class _InspectorSimulado(InspectorConjuntos):
    """Tres archivos: uno de reales (JPEG) y dos de sintéticas (PNG)."""

    def __init__(self, licencia="cc-by-nc-4.0", columnas=None, falla=False):
        self.licencia = licencia
        self.nombres_columnas = columnas or ["image", "label", "model"]
        self.falla = falla
        self.archivos = {
            "data/a.parquet": [{"label": "real", "model": "real"}] * 6,
            "data/b.parquet": [{"label": "fake", "model": "sdxl"}] * 4
            + [{"label": "fake", "model": "flux"}] * 2,
            "data/c.parquet": [{"label": "fake", "model": "sdxl"}] * 3,
        }

    def informacion(self, conjunto, revision):
        if self.falla:
            raise ErrorInspeccion("404 no existe")
        return InformacionConjunto("abc123def456", self.licencia, True,
                                   [*self.archivos, "README.md"])

    def columnas(self, conjunto, revision, archivo):
        return self.nombres_columnas

    def leer_filas(self, conjunto, revision, archivo, columnas):
        return [{c: fila[c] for c in columnas} for fila in self.archivos[archivo]]

    def leer_imagenes(self, conjunto, revision, archivo, columnas, cantidad):
        filas = []
        for fila in self.archivos[archivo][:cantidad]:
            real = fila["label"] == "real"
            contenido = _bytes("JPEG", 90) if real else _bytes("PNG")
            filas.append({"image": {"bytes": contenido}, "label": fila["label"]})
        return filas


def _candidato(**cambios):
    valores = {
        "nombre": "simulado", "conjunto": "alguien/conjunto", "columna_clase": "label",
        "valores_sinteticos": ["fake"], "columna_generador": "model", "uso": "entrenamiento",
    }
    valores.update(cambios)
    return Candidato(**valores)


def test_estima_la_calidad_jpeg():
    """La calidad estimada se acerca a la usada al guardar."""
    for calidad in (60, 75, 90):
        with Image.open(io.BytesIO(_bytes("JPEG", calidad, (128, 128)))) as imagen:
            assert abs(estimar_calidad_jpeg(imagen) - calidad) <= 2
    with Image.open(io.BytesIO(_bytes("PNG"))) as imagen:
        assert estimar_calidad_jpeg(imagen) is None


def test_describe_imagenes_validas_e_ilegibles():
    """Formato y tamaño de una imagen; las ilegibles no rompen la exploración."""
    assert describir_imagen(_bytes("PNG"))["formato"] == "png"
    assert describir_imagen(_bytes("PNG"))["ancho"] == 64
    assert describir_imagen(b"no es una imagen")["formato"] == "ilegible"


@pytest.mark.parametrize("licencia, esperado", [
    ("cc-by-nc-sa-4.0", True), ("mit", True), ("other", False), ("", False), ("cc", False),
])
def test_licencias_verificables(licencia, esperado):
    """«other», vacía o «cc» sin variante no permiten saber qué se puede hacer."""
    assert licencia_verificable(licencia) is esperado


def test_explora_un_candidato_disponible():
    """Cuenta clases y generadores y describe la muestra de cada clase."""
    informe = explorar_candidato(_InspectorSimulado(), _candidato(), 10, 4, semilla=0)
    assert informe.incluido and informe.disponible
    assert informe.revision_exacta == "abc123def456"
    assert informe.requiere_aceptar_condiciones
    assert informe.cantidad_archivos == 3
    assert informe.por_clase == {"real": 6, "sintetica": 9}
    assert informe.por_generador == {"sdxl": 7, "flux": 2}
    formatos = informe.resumen_formatos()
    assert formatos["real"]["formatos"] == {"jpeg": 4}
    assert formatos["real"]["calidad_jpeg_mediana"] == 90
    assert formatos["sintetica"]["formatos"] == {"png": 4}


def test_excluye_sin_licencia_verificable_salvo_verificacion_manual():
    """Sin licencia en la ficha se excluye (CA2); la verificación manual la reemplaza."""
    inspector = _InspectorSimulado(licencia="other")
    excluido = explorar_candidato(inspector, _candidato(), 10, 2, semilla=0)
    assert not excluido.incluido
    assert "licencia verificable" in excluido.motivos_exclusion[0]
    manual = explorar_candidato(
        inspector, _candidato(licencia_verificada_a_mano="CC BY 4.0, según el artículo"),
        10, 2, semilla=0,
    )
    assert manual.incluido and manual.licencia.startswith("CC BY 4.0")


def test_excluye_no_disponibles_y_columnas_faltantes():
    """Un conjunto inexistente o con otras columnas queda anotado con el motivo."""
    no_disponible = explorar_candidato(_InspectorSimulado(falla=True), _candidato(), 2, 2, 0)
    assert not no_disponible.disponible and "404" in no_disponible.motivos_exclusion[0]
    sin_columna = explorar_candidato(
        _InspectorSimulado(columnas=["img", "label"]), _candidato(), 2, 2, 0
    )
    assert sin_columna.columnas_faltantes == ["image", "model"]
    assert not sin_columna.incluido


def test_excluye_conjuntos_sin_parquet():
    """Si no hay Parquet, se informa qué archivos tiene para revisarlo a mano."""
    inspector = _InspectorSimulado()
    inspector.archivos = {}
    informe = explorar_candidato(inspector, _candidato(), 2, 2, 0)
    assert "no tiene archivos Parquet" in informe.motivos_exclusion[0]


def test_conjunto_de_una_sola_clase():
    """Con clase fija se cuentan las filas sin leer ninguna columna."""
    inspector = _InspectorSimulado()
    inspector.archivos = {"data/a.parquet": [{"label": "x"}] * 5}
    candidato = Candidato(nombre="autos", conjunto="a/b", clase_fija="real", uso="reales")
    informe = explorar_candidato(inspector, candidato, 2, 2, 0)
    assert informe.por_clase == {"real": 5}
    assert informe.incluido


def test_un_candidato_sin_clase_es_invalido():
    """Hay que indicar la columna de clase o una clase fija."""
    with pytest.raises(ValueError):
        Candidato(nombre="x", conjunto="a/b", uso="?")


def test_propone_una_fuente_valida_para_la_receta():
    """La propuesta fija la revisión, elige archivos y una cuota por generador."""
    candidato = _candidato()
    informe = explorar_candidato(_InspectorSimulado(), candidato, 10, 2, semilla=0)
    propuesta = proponer_fuente(
        informe, candidato, cantidad_reales=4, cantidad_sinteticas=6, cantidad_generadores=1,
        semilla=0,
    )
    assert propuesta["revision"] == "abc123def456"
    assert propuesta["generadores_incluidos"] == ["sdxl"]
    assert propuesta["cuota_por_generador"] == 6
    assert set(propuesta["archivos"]) <= set(informe.archivos_explorados)
    assert ConfiguracionFuente(**propuesta).archivos == propuesta["archivos"]


def test_explorar_escribe_json_y_tabla(tmp_path):
    """La tabla muestra la licencia y la decisión de cada candidato."""
    lista = ListaCandidatos(candidatos=[_candidato(), _candidato(nombre="otro", conjunto="b/c")])
    informes = explorar(lista, tmp_path, inspector=_InspectorSimulado())
    assert len(informes) == 2
    datos = json.loads((tmp_path / "exploracion.json").read_text(encoding="utf-8"))
    assert datos[0]["por_generador"] == {"sdxl": 7, "flux": 2}
    tabla = (tmp_path / "exploracion.md").read_text(encoding="utf-8")
    assert "cc-by-nc-4.0" in tabla and "incluido" in tabla
    assert "excluido: no disponible" in tabla_markdown(
        [explorar_candidato(_InspectorSimulado(falla=True), _candidato(), 1, 1, 0)]
    )


def test_cargar_candidatos(tmp_path):
    """El archivo de candidatos se valida al cargarlo."""
    ruta = tmp_path / "candidatos.yaml"
    ruta.write_text(yaml.safe_dump({"candidatos": [_candidato().model_dump()]}), "utf-8")
    assert cargar_candidatos(ruta).candidatos[0].nombre == "simulado"
    ruta.write_text("candidatos: []", "utf-8")
    with pytest.raises(ErrorConfiguracion):
        cargar_candidatos(ruta)
    with pytest.raises(ErrorConfiguracion):
        cargar_candidatos(tmp_path / "no_existe.yaml")


def test_los_candidatos_del_repositorio_son_validos():
    """El archivo versionado de candidatos v1 cumple el esquema."""
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    ruta = Path(__file__).parents[2] / "configuracion" / "candidatos_v1.yaml"
    assert len(cargar_candidatos(ruta).candidatos) >= 5
