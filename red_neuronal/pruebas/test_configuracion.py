"""Pruebas de la configuración validada (tarea T05)."""

from pathlib import Path

import pytest

from clasificador.configuracion import ErrorConfiguracion, cargar_configuracion

RUTA_PRUEBA_DE_CONCEPTO = Path(__file__).parents[1] / "configuracion" / "prueba_de_concepto.yaml"

_MINIMA = """
nombre: minima
datos:
  fuentes:
    - nombre: propio
      tipo: carpeta_local
      ruta: /tmp/propio
      cantidad_reales: 10
      cantidad_sinteticas: 10
      licencia: propia
"""


def _escribir(tmp_path: Path, contenido: str) -> Path:
    ruta = tmp_path / "configuracion.yaml"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def test_la_configuracion_de_la_prueba_de_concepto_es_valida():
    """El archivo versionado del repositorio cumple el esquema."""
    configuracion = cargar_configuracion(RUTA_PRUEBA_DE_CONCEPTO)
    assert configuracion.nombre == "prueba_de_concepto"
    assert configuracion.datos.fuentes[0].tipo == "hugging_face"


def test_una_configuracion_minima_usa_los_valores_por_defecto(tmp_path):
    """Los hiperparámetros omitidos toman los valores del plan técnico."""
    configuracion = cargar_configuracion(_escribir(tmp_path, _MINIMA))
    assert configuracion.semilla == 42
    assert configuracion.entrenamiento.arquitectura == "efficientnet_b0"
    assert configuracion.compuerta.auc_minimo == pytest.approx(0.90)
    assert configuracion.datos.proporciones.entrenamiento == pytest.approx(0.8)


def test_un_archivo_inexistente_lanza_error_claro(tmp_path):
    """Se informa la ruta que no existe."""
    with pytest.raises(ErrorConfiguracion, match="no existe"):
        cargar_configuracion(tmp_path / "no_existe.yaml")


def test_un_yaml_invalido_lanza_error_claro(tmp_path):
    """Un YAML mal formado no produce un error genérico."""
    with pytest.raises(ErrorConfiguracion, match="no es YAML"):
        cargar_configuracion(_escribir(tmp_path, "nombre: [sin cerrar"))


def test_un_yaml_que_no_es_mapa_lanza_error(tmp_path):
    """El archivo debe ser un mapa de claves, no una lista."""
    with pytest.raises(ErrorConfiguracion, match="mapa"):
        cargar_configuracion(_escribir(tmp_path, "- uno\n- dos\n"))


def test_un_campo_obligatorio_faltante_se_informa(tmp_path):
    """Sin la sección de datos la configuración no es válida."""
    with pytest.raises(ErrorConfiguracion, match="datos"):
        cargar_configuracion(_escribir(tmp_path, "nombre: sin_datos\n"))


def test_un_campo_desconocido_se_rechaza(tmp_path):
    """Un error de tipeo no se ignora en silencio."""
    contenido = _MINIMA + "entrenamiento:\n  epoca: 3\n"
    with pytest.raises(ErrorConfiguracion, match="epoca"):
        cargar_configuracion(_escribir(tmp_path, contenido))


@pytest.mark.parametrize(
    ("agregado", "mensaje"),
    [
        ("entrenamiento:\n  epocas: 0\n", "epocas"),
        ("compuerta:\n  auc_minimo: 1.5\n", "auc_minimo"),
    ],
)
def test_un_valor_fuera_de_rango_se_rechaza(tmp_path, agregado, mensaje):
    """Los valores imposibles se detectan antes de entrenar."""
    with pytest.raises(ErrorConfiguracion, match=mensaje):
        cargar_configuracion(_escribir(tmp_path, _MINIMA + agregado))


def test_las_proporciones_deben_sumar_uno(tmp_path):
    """Una partición que no suma 1 se rechaza."""
    contenido = _MINIMA.replace(
        "datos:\n", "datos:\n  proporciones: {entrenamiento: 0.5, validacion: 0.2, prueba: 0.1}\n"
    )
    with pytest.raises(ErrorConfiguracion, match="sumar 1"):
        cargar_configuracion(_escribir(tmp_path, contenido))


@pytest.mark.parametrize(
    ("campo", "valor", "mensaje"),
    [
        ("calidad_jpeg", "[95, 75]", "calidad_jpeg"),
        ("lado_menor", "[100, 512]", "lado_menor"),
    ],
)
def test_los_rangos_invalidos_se_rechazan(tmp_path, campo, valor, mensaje):
    """Un rango con mínimo mayor que el máximo o fuera de límites falla."""
    contenido = _MINIMA.replace("datos:\n", f"datos:\n  {campo}: {valor}\n")
    with pytest.raises(ErrorConfiguracion, match=mensaje):
        cargar_configuracion(_escribir(tmp_path, contenido))


def test_una_fuente_de_hugging_face_requiere_sus_columnas(tmp_path):
    """Sin la columna de clase no se puede etiquetar."""
    contenido = """
nombre: incompleta
datos:
  fuentes:
    - nombre: hf
      tipo: hugging_face
      conjunto: alguien/conjunto
      cantidad_reales: 1
      licencia: cc-by
"""
    with pytest.raises(ErrorConfiguracion, match="columna_clase"):
        cargar_configuracion(_escribir(tmp_path, contenido))


def test_una_fuente_de_hugging_face_requiere_valores_sinteticos(tmp_path):
    """Hay que indicar qué valores de la columna de clase son sintéticos."""
    contenido = """
nombre: incompleta
datos:
  fuentes:
    - nombre: hf
      tipo: hugging_face
      conjunto: alguien/conjunto
      columna_clase: label
      cantidad_reales: 1
      licencia: cc-by
"""
    with pytest.raises(ErrorConfiguracion, match="valores_sinteticos"):
        cargar_configuracion(_escribir(tmp_path, contenido))


def test_una_carpeta_local_requiere_ruta(tmp_path):
    """Una fuente local sin ruta se rechaza."""
    contenido = _MINIMA.replace("      ruta: /tmp/propio\n", "")
    with pytest.raises(ErrorConfiguracion, match="ruta"):
        cargar_configuracion(_escribir(tmp_path, contenido))


def test_una_fuente_sin_cantidades_se_rechaza(tmp_path):
    """Una fuente que no pide imágenes es un error de configuración."""
    contenido = _MINIMA.replace("cantidad_reales: 10", "cantidad_reales: 0").replace(
        "cantidad_sinteticas: 10", "cantidad_sinteticas: 0"
    )
    with pytest.raises(ErrorConfiguracion, match="ninguna imagen"):
        cargar_configuracion(_escribir(tmp_path, contenido))


def test_las_fuentes_con_nombre_repetido_se_rechazan(tmp_path):
    """Cada fuente debe tener un nombre único para el manifiesto."""
    fuente = _MINIMA.split("  fuentes:\n")[1]
    contenido = _MINIMA.rstrip("\n") + "\n" + fuente
    with pytest.raises(ErrorConfiguracion, match="mismo nombre"):
        cargar_configuracion(_escribir(tmp_path, contenido))


def test_la_receta_v1_es_valida():
    """La receta v1 versionada cumple el esquema."""
    configuracion = cargar_configuracion(RUTA_PRUEBA_DE_CONCEPTO.parent / "v1.yaml")
    assert configuracion.nombre == "v1"
    assert configuracion.datos.generadores_reservados


def test_el_muestreo_por_archivos_es_solo_para_hugging_face(tmp_path):
    """Una carpeta local no admite archivos, generadores ni cuotas."""
    # pylint: disable-next=import-outside-toplevel
    from clasificador.configuracion import ConfiguracionFuente

    with pytest.raises(ValueError, match="solo se usan en fuentes de Hugging Face"):
        ConfiguracionFuente(nombre="p", tipo="carpeta_local", ruta=tmp_path,
                            cantidad_reales=1, licencia="propia", cuota_por_generador=3)
    with pytest.raises(ValueError, match="clase_fija"):
        ConfiguracionFuente(nombre="h", tipo="hugging_face", conjunto="a/b",
                            cantidad_reales=1, licencia="x")
