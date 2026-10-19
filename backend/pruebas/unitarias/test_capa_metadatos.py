"""Pruebas de la capa de metadatos (funcionalidad 007).

Retoman los casos de ``tests/test_metadatos_exif.py`` del repositorio anterior
(TIF) y suman los de las reglas nuevas. Las imágenes se generan en memoria y
ExifTool les escribe los metadatos: nunca se usan imágenes de casos reales.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import io
import shutil
import subprocess
from datetime import date, datetime

import pytest
from PIL import Image, PngImagePlugin

from app.analisis.base import (
    TERMINOS_DE_VEREDICTO,
    Anomalia,
    CapaNoDisponible,
    ContextoImagen,
)
from app.analisis.dispositivos import fecha_de_lanzamiento
from app.analisis.metadatos import CapaMetadatos, _declaraciones_c2pa

EXIFTOOL = shutil.which("exiftool")
requiere_exiftool = pytest.mark.skipif(EXIFTOOL is None, reason="ExifTool no está instalado")
CARGA = datetime(2026, 10, 19, 12, 0)


def _jpeg(tmp_path, *etiquetas, tamanio=(64, 48)):
    """JPEG generado con los metadatos indicados (``-Campo=valor``) escritos por ExifTool."""
    ruta = tmp_path / "foto.jpg"
    Image.new("RGB", tamanio, (120, 80, 40)).save(ruta, "JPEG")
    if etiquetas:
        subprocess.run(
            [EXIFTOOL, "-overwrite_original", *etiquetas, str(ruta)], check=True,
            capture_output=True,
        )
    return ruta.read_bytes()


def _contexto(formato="jpeg", tamanio=(64, 48)):
    return ContextoImagen(formato, tamanio[0], tamanio[1], CARGA)


def _analizar(contenido, contexto=None):
    return CapaMetadatos(EXIFTOOL).analizar(contenido, contexto or _contexto())


def _campos(resultado):
    return {a.campo: a.severidad for a in resultado.anomalias}


# --- Extracción (regresión del TIF) ---

@requiere_exiftool
def test_extraer_devuelve_nombres_solos_y_con_grupo(tmp_path):
    """El TIF corrigió que los validadores buscaran "Make" con claves con grupo."""
    datos = CapaMetadatos(EXIFTOOL).extraer(_jpeg(tmp_path, "-Make=Apple", "-Software=12"))
    assert datos["Make"] == "Apple"
    assert any(clave.endswith(":Make") for clave in datos)
    # ExifTool devuelve números JSON: las reglas no deben romperse con ellos.
    assert not CapaMetadatos.regla_software(datos)
    # Los datos de la entrada estándar (archivo temporal) se descartan.
    assert not any(clave.startswith("File:System") for clave in datos)


# --- Reglas del TIF, conservadas ---

@requiere_exiftool
@pytest.mark.parametrize("software, texto", [
    ("Adobe Photoshop 25.0", "un editor"),
    ("Snapseed 2.0", "un editor"),
    ("Midjourney v6", "un generador de imágenes"),
])
def test_software_declarado(tmp_path, software, texto):
    """CA8 (RF39 CA1): editor o generador declarado, severidad directa."""
    resultado = _analizar(_jpeg(tmp_path, f"-Software={software}"))
    anomalia = next(a for a in resultado.anomalias if a.campo == "Software")
    assert anomalia.severidad == "directo"
    assert texto in anomalia.descripcion
    assert resultado.nivel == 90


@requiere_exiftool
def test_historial_xmp(tmp_path):
    """El TIF pedía ``-XMP:History`` sin ``-struct`` y la regla nunca se activaba."""
    resultado = _analizar(_jpeg(tmp_path, "-XMP-xmpMM:HistoryAction=saved"))
    assert _campos(resultado)["xmpMM:History"] == "directo"


@requiere_exiftool
def test_makernotes_y_bloque_de_captura_ausentes(tmp_path):
    """Marca conocida sin MakerNotes (fuerte) y sin parámetros de captura (moderado)."""
    resultado = _analizar(_jpeg(tmp_path, "-Make=Apple", "-Model=iPhone 13"))
    campos = _campos(resultado)
    assert campos["MakerNotes"] == "fuerte"
    assert campos["Parámetros de captura"] == "moderado"
    assert resultado.nivel == 80


@requiere_exiftool
def test_dispositivo_con_parametros_de_captura(tmp_path):
    """Con exposición, apertura e ISO no se informa el bloque de captura vacío."""
    resultado = _analizar(_jpeg(
        tmp_path, "-Make=Canon", "-ExposureTime=1/125", "-FNumber=4", "-ISO=200",
    ))
    assert "Parámetros de captura" not in _campos(resultado)


@requiere_exiftool
def test_modificacion_muy_posterior_a_la_captura(tmp_path):
    """Moderado: ModifyDate más de 24 h después de DateTimeOriginal."""
    resultado = _analizar(_jpeg(
        tmp_path, "-DateTimeOriginal=2026:01:01 10:00:00", "-ModifyDate=2026:01:05 10:00:00",
    ))
    assert _campos(resultado)["ModifyDate / DateTimeOriginal"] == "moderado"
    assert resultado.nivel == 45


def test_dimensiones_tipicas_de_ia():
    """Débil: resolución habitual de los generadores."""
    anomalias = CapaMetadatos.regla_dimensiones(_contexto(tamanio=(1024, 1024)))
    assert [a.severidad for a in anomalias] == ["debil"]
    assert not CapaMetadatos.regla_dimensiones(_contexto(tamanio=(4032, 3024)))


# --- Reglas nuevas ---

@requiere_exiftool
def test_fecha_de_captura_posterior_a_la_carga(tmp_path):
    """CA9 (RF39 CA2): la fecha de carga reemplaza a la "fecha del sistema" del TIF."""
    resultado = _analizar(_jpeg(tmp_path, "-DateTimeOriginal=2026:12:31 10:00:00"))
    anomalia = next(a for a in resultado.anomalias if a.campo == "DateTimeOriginal")
    assert anomalia.severidad == "fuerte"
    assert "posterior a la fecha en que la imagen se cargó" in anomalia.descripcion


@requiere_exiftool
def test_captura_dentro_de_la_tolerancia_de_zona_horaria(tmp_path):
    """Las fechas EXIF no tienen zona: unas horas después de la carga no es imposible."""
    resultado = _analizar(_jpeg(tmp_path, "-DateTimeOriginal=2026:10:19 20:00:00"))
    assert "DateTimeOriginal" not in _campos(resultado)


@requiere_exiftool
def test_fecha_anterior_al_lanzamiento_del_dispositivo(tmp_path):
    """CA9 (RF39 CA2): un iPhone 15 no podía sacar fotos en 2020."""
    resultado = _analizar(_jpeg(
        tmp_path, "-Model=iPhone 15 Pro", "-DateTimeOriginal=2020:05:01 10:00:00",
    ))
    anomalia = next(a for a in resultado.anomalias if a.campo == "DateTimeOriginal / Model")
    assert anomalia.severidad == "fuerte"
    assert "2023-09-22" in anomalia.valor


@requiere_exiftool
def test_origen_sintetico_iptc(tmp_path):
    """Origen declarado como generado por IA en XMP (vocabulario IPTC)."""
    resultado = _analizar(_jpeg(
        tmp_path,
        "-XMP-iptcExt:DigitalSourceType="
        "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    ))
    assert _campos(resultado)["DigitalSourceType"] == "directo"


def test_parametros_de_generacion_en_png():
    """Parámetros de AUTOMATIC1111 en los textos del PNG (directo)."""
    info = PngImagePlugin.PngInfo()
    info.add_text("parameters", "a cat, Steps: 20, Sampler: Euler a, CFG scale: 7, Seed: 1")
    salida = io.BytesIO()
    Image.new("RGB", (64, 64)).save(salida, "PNG", pnginfo=info)
    textos = CapaMetadatos.textos_png(salida.getvalue())
    anomalias = CapaMetadatos.regla_parametros_png(textos)
    assert [a.severidad for a in anomalias] == ["directo"]
    assert "steps" in anomalias[0].valor and "sampler" in anomalias[0].valor


@requiere_exiftool
def test_imagen_sin_metadatos(tmp_path):
    """CA10 (RF39 CA3): se informa como dato, sin elevar el nivel."""
    resultado = _analizar(_jpeg(tmp_path))
    assert resultado.nivel == 0
    assert _campos(resultado) == {"Metadatos": "neutro"}
    assert "mensajería" in resultado.conclusion
    assert resultado.detalle["sin_metadatos"] is True


@requiere_exiftool
def test_tabla_de_metadatos_relevantes(tmp_path):
    """CA11 (RF39 CA4)."""
    resultado = _analizar(_jpeg(
        tmp_path, "-Make=Google", "-Model=Pixel 8", "-GPSLatitude=34.6", "-GPSLatitudeRef=S",
        "-GPSLongitude=58.4", "-GPSLongitudeRef=W",
    ))
    tabla = {fila["campo"]: fila["valor"] for fila in resultado.detalle["tabla"]}
    assert tabla["Fabricante"] == "Google"
    assert tabla["Modelo"] == "Pixel 8"
    assert "S" in tabla["Ubicación GPS"]
    assert tabla["Dimensiones"] == "64 × 48 píxeles"


def test_declaraciones_de_credenciales_de_contenido():
    """Las acciones C2PA (estructura de ExifTool) se leen como software y origen declarados."""
    datos = {
        "JUMBF:CBOR:Actions": [{
            "action": "c2pa.created",
            "softwareAgent": {"name": "ChatGPT"},
            "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/"
                                 "trainedAlgorithmicMedia",
        }],
        "JUMBF:CBOR:Claim_generator_info": {"name": "OpenAI Media Service API"},
    }
    datos.update(_declaraciones_c2pa(datos))
    assert datos["C2PASoftware"] == "ChatGPT; OpenAI Media Service API"
    software = CapaMetadatos.regla_software(datos)
    origen = CapaMetadatos.regla_origen_iptc(datos)
    assert [a.severidad for a in software + origen] == ["directo", "directo"]
    assert "sin verificar su firma" in software[0].descripcion
    conclusion = CapaMetadatos.redactar_conclusion(90, software + origen, False)
    assert "capa de credenciales de contenido" in conclusion


# --- Nivel y conclusión (RF43) ---

@pytest.mark.parametrize("severidades, nivel", [
    ([], 0),
    (["neutro"], 0),
    (["debil"], 20),
    (["moderado", "moderado"], 55),
    (["fuerte", "moderado"], 80),
    (["fuerte", "debil"], 70),
    (["directo", "directo", "fuerte"], 90),
])
def test_calculo_del_nivel(severidades, nivel):
    """Método documentado en el plan: base de la más grave + 10 por cada otra relevante."""
    anomalias = [Anomalia("c", "v", "d", s) for s in severidades]
    assert CapaMetadatos.calcular_nivel(anomalias) == nivel


@pytest.mark.parametrize("nivel, sin_metadatos, texto", [
    (0, True, "no conserva metadatos"),
    (0, False, "No se encontraron indicios"),
    (20, False, "indicios débiles"),
    (55, False, "indicios moderados"),
    (90, False, "indicios fuertes"),
])
def test_conclusiones_sin_veredicto(nivel, sin_metadatos, texto):
    """CA12 (RN27): indicios, recomendación y ningún término de veredicto."""
    anomalias = [Anomalia("c", "v", "Descripción del hallazgo.", "debil")] if nivel else []
    conclusion = CapaMetadatos.redactar_conclusion(nivel, anomalias, sin_metadatos)
    assert texto in conclusion
    assert "perito especializado" in conclusion
    palabras = conclusion.lower().replace(".", " ").replace(",", " ").split()
    assert not set(palabras) & set(TERMINOS_DE_VEREDICTO)


# --- Fallas y versión (RN26, RN29) ---

def test_sin_exiftool_la_capa_no_esta_disponible():
    """CA13: el servicio informa la capa como "No disponible" con este motivo."""
    capa = CapaMetadatos("/no/existe/exiftool")
    with pytest.raises(CapaNoDisponible, match="no está instalado"):
        capa.analizar(b"\xff\xd8\xff", _contexto())
    assert capa.version() == "1.0 (ExifTool no disponible)"


@requiere_exiftool
def test_version_incluye_la_de_exiftool():
    """CA14 (RN29)."""
    assert CapaMetadatos(EXIFTOOL).version().startswith("1.0 (ExifTool 1")


@pytest.mark.parametrize("modelo, fecha", [
    ("iPhone 15 Pro Max", date(2023, 9, 22)),
    ("iPhone 15", date(2023, 9, 22)),
    ("iPhone 13 mini", date(2021, 9, 24)),
    ("SM-S918B", date(2023, 2, 17)),
    ("Modelo desconocido", None),
    (None, None),
])
def test_fecha_de_lanzamiento(modelo, fecha):
    """Se usa la coincidencia más larga; un modelo desconocido no genera anomalías."""
    assert fecha_de_lanzamiento(modelo) == fecha
