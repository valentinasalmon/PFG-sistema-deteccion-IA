"""Pruebas del análisis de imágenes a través de la API.

Criterios de aceptación de la funcionalidad 007: CA1 a CA14. En las pruebas
la cola es sincrónica: el análisis termina antes de que vuelva la solicitud.
Las imágenes se generan en memoria.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import io
from datetime import timedelta
from pathlib import Path

import pytest
from PIL import Image, PngImagePlugin

from app.analisis.metadatos import CapaMetadatos
from app.extensiones import db
from app.modelos.analisis import Analisis
from app.modelos.imagen import Imagen
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import crear_estudio, entradas_auditoria

CASO = {
    "espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
    "lugar": "Av. Corrientes 1234",
}


def _png(color=(10, 20, 30), parametros=None, tamanio=(64, 48)):
    info = PngImagePlugin.PngInfo()
    if parametros:
        info.add_text("parameters", parametros)
    salida = io.BytesIO()
    Image.new("RGB", tamanio, color).save(salida, "PNG", pnginfo=info)
    return salida.getvalue()


def _cargar(cliente, id_caso, contenido, nombre="foto.png"):
    respuesta = cliente.post(
        f"/api/casos/{id_caso}/imagenes", data={"archivo": (io.BytesIO(contenido), nombre)},
        content_type="multipart/form-data",
    )
    assert respuesta.status_code == 201, respuesta.get_json()
    return respuesta.get_json()["imagen"]["id"]


def _analizar(cliente, id_caso, ids):
    return cliente.post(f"/api/casos/{id_caso}/analisis", json={"imagenes": ids})


def _detalle(cliente, id_caso, id_analisis):
    return cliente.get(f"/api/casos/{id_caso}/analisis/{id_analisis}").get_json()["analisis"]


def _caso(cliente, id_caso):
    return cliente.get(f"/api/casos/{id_caso}").get_json()["caso"]


class ColaRetenida:
    """Cola que guarda los trabajos sin ejecutarlos, para ver el análisis en curso."""

    def __init__(self):
        self.trabajos = []

    def encolar(self, trabajo, *argumentos):
        """Guarda el trabajo."""
        self.trabajos.append((trabajo, argumentos))
        return "retenido"


@pytest.fixture
def ana(cuenta):
    """Responsable de los casos."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Otra persona, miembro del estudio de Ana."""
    return cuenta("beto@ejemplo.com", "Beto")


@pytest.fixture
def caso(ana):
    """Caso personal de Ana con dos imágenes: una sin metadatos y otra con parámetros de IA."""
    id_caso = ana.post("/api/casos", json=CASO).get_json()["caso"]["id"]
    sin_datos = _cargar(ana, id_caso, _png(), "sin_datos.png")
    generada = _cargar(
        ana, id_caso, _png((1, 2, 3), "a cat, Steps: 20, Sampler: Euler a, Seed: 1"),
        "generada.png",
    )
    return {"id": id_caso, "imagenes": [sin_datos, generada]}


@pytest.fixture
def cola_retenida(aplicacion):
    """Reemplaza la cola de la aplicación por una que no ejecuta los trabajos."""
    cola = ColaRetenida()
    aplicacion.extensions["cola_analisis"] = cola
    return cola


# --- Pedido y procesamiento (CA1, CA5, CA7) ---

def test_analizar_procesa_las_imagenes_y_deja_el_caso_analizado(aplicacion, ana, caso, correos):
    """CA1 y CA7: con la cola sincrónica, el análisis termina antes de responder."""
    respuesta = _analizar(ana, caso["id"], caso["imagenes"])

    assert respuesta.status_code == 202
    resumen = respuesta.get_json()["analisis"]
    assert resumen["cantidad_imagenes"] == 2
    analisis = _detalle(ana, caso["id"], resumen["id"])
    assert analisis["estado"] == "finalizado"
    assert analisis["solicitante"] == "Ana López"
    assert analisis["versiones"]["metadatos"].startswith("1.0 (ExifTool")
    assert analisis["versiones"]["c2pa"].startswith("1.0 (c2pa-python")
    sin_datos, generada = analisis["imagenes"]
    assert sin_datos["integridad"] == "verificada"
    resultado = sin_datos["resultados"][0]
    assert (resultado["capa"], resultado["estado"], resultado["nivel"]) == (
        "metadatos", "completado", 0,
    )
    assert resultado["detalle"]["sin_metadatos"] is True
    credenciales = sin_datos["resultados"][1]
    assert (credenciales["capa"], credenciales["estado"], credenciales["nivel"]) == (
        "c2pa", "completado", 0,
    )
    assert credenciales["detalle"]["sin_credenciales"] is True
    nivel_generada = generada["resultados"][0]
    assert nivel_generada["nivel"] == 90
    assert nivel_generada["anomalias"][0]["severidad"] == "directo"
    assert "perito especializado" in nivel_generada["conclusion"]
    assert _caso(ana, caso["id"])["estado"] == "analizado"
    aviso = correos[-1]
    assert (aviso.destinatario, aviso.asunto) == (
        "ana@ejemplo.com", f"Terminó el análisis del caso {_caso(ana, caso['id'])['numero']}",
    )
    assert entradas_auditoria(aplicacion, "analisis.solicitud")[-1]["resultado"] == "exitoso"
    assert entradas_auditoria(aplicacion, "analisis.finalizacion")[-1]["detalle"]["imagenes"] == 2


def test_las_imagenes_analizadas_quedan_marcadas(ana, caso):
    """CU27 paso 1: la pantalla elige por defecto las que todavía no se analizaron."""
    _analizar(ana, caso["id"], caso["imagenes"][:1])
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert [i["analizada"] for i in imagenes] == [True, False]


def test_historial_del_mas_reciente_al_mas_antiguo(ana, caso):
    """RN25: cada análisis se conserva."""
    primero = _analizar(ana, caso["id"], caso["imagenes"][:1]).get_json()["analisis"]["id"]
    segundo = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]
    historial = ana.get(f"/api/casos/{caso['id']}/analisis").get_json()["analisis"]
    assert [a["id"] for a in historial] == [segundo, primero]
    assert [a["cantidad_imagenes"] for a in historial] == [2, 1]


# --- Validaciones del pedido (CA2, CA3) ---

def test_pedido_sin_imagenes_o_con_imagenes_ajenas(aplicacion, ana, caso):
    """CA2."""
    respuesta = _analizar(ana, caso["id"], [])
    assert respuesta.status_code == 400
    assert "imagenes" in respuesta.get_json()["errores"]
    otro = ana.post("/api/casos", json=CASO).get_json()["caso"]["id"]
    ajena = _cargar(ana, otro, _png((9, 9, 9)))
    assert _analizar(ana, caso["id"], [ajena]).status_code == 400
    assert entradas_auditoria(aplicacion, "analisis.solicitud")[-1]["detalle"]["motivo"] == (
        "imagen_ajena"
    )
    assert _caso(ana, caso["id"])["estado"] == "borrador"


def test_lector_sin_permiso_y_caso_cerrado(ana, beto, caso):
    """CA2 (RN19, RN20): solo el Responsable o un Colaborador, en Borrador o Analizado."""
    assert _analizar(beto, caso["id"], caso["imagenes"]).status_code == 404
    ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "cerrar"})
    respuesta = _analizar(ana, caso["id"], caso["imagenes"])
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "caso_sin_analisis")


def test_el_lector_de_un_caso_de_organizacion_no_analiza(ana, beto):
    """CA2: el Lector consulta pero no pide análisis."""
    id_org = crear_estudio(ana, beto, "beto@ejemplo.com")
    id_caso = ana.post("/api/casos", json={**CASO, "espacio": str(id_org)}).get_json()["caso"]["id"]
    imagen = _cargar(ana, id_caso, _png())
    ana.post(
        f"/api/casos/{id_caso}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )
    assert _analizar(beto, id_caso, [imagen]).status_code == 403
    assert beto.get(f"/api/casos/{id_caso}/analisis").status_code == 200


def test_no_se_pide_otro_analisis_mientras_hay_uno_en_curso(ana, caso, cola_retenida):
    """CA3 y CA5: el análisis queda en cola, el caso En análisis y no admite cambios."""
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]

    assert _caso(ana, caso["id"])["estado"] == "en_analisis"
    analisis = _detalle(ana, caso["id"], id_analisis)
    assert (analisis["estado"], analisis["en_curso"]) == ("en_cola", True)
    respuesta = _analizar(ana, caso["id"], caso["imagenes"])
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "analisis_en_curso")
    borrado = ana.delete(f"/api/casos/{caso['id']}/imagenes/{caso['imagenes'][0]}")
    assert borrado.status_code == 409
    assert cola_retenida.trabajos == [("app.tareas.analisis.ejecutar_analisis", (id_analisis,))]


# --- Integridad (CA4) ---

def test_imagen_alterada_se_excluye(aplicacion, ana, caso):
    """CA4 (RF38 CA4, RNF07): si la huella no coincide, la imagen no se analiza."""
    with aplicacion.app_context():
        clave = db.session.get(Imagen, caso["imagenes"][0]).clave
    Path(aplicacion.config["DIRECTORIO_ALMACENAMIENTO"], clave).write_bytes(_png((255, 0, 0)))

    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]

    alterada, intacta = _detalle(ana, caso["id"], id_analisis)["imagenes"]
    assert (alterada["integridad"], alterada["resultados"]) == ("alterada", [])
    assert intacta["integridad"] == "verificada"
    entrada = entradas_auditoria(aplicacion, "analisis.integridad")[-1]
    assert entrada["resultado"] == "fallido"
    assert entrada["detalle"]["nombre"] == "sin_datos.png"


# --- Fallas (CA6, CA13) ---

def test_capa_no_disponible_no_detiene_el_analisis(aplicacion, ana, caso):
    """CA13 (RN26): sin ExifTool, la capa queda "No disponible" con el motivo."""
    aplicacion.config["RUTA_EXIFTOOL"] = "/no/existe/exiftool"
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]
    analisis = _detalle(ana, caso["id"], id_analisis)
    assert analisis["estado"] == "finalizado"
    resultado = analisis["imagenes"][0]["resultados"][0]
    assert (resultado["estado"], resultado["nivel"]) == ("no_disponible", None)
    assert "no está instalado" in resultado["motivo"]


def test_falla_inesperada_de_una_capa(ana, caso, monkeypatch):
    """CA13: una excepción de la capa también se informa como "No disponible"."""
    def fallar(*_):
        raise RuntimeError("error interno")

    monkeypatch.setattr(CapaMetadatos, "analizar", fallar)
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]
    resultado = _detalle(ana, caso["id"], id_analisis)["imagenes"][0]["resultados"][0]
    assert resultado["estado"] == "no_disponible"
    assert "falló de forma inesperada" in resultado["motivo"]


def test_falla_general_deja_el_analisis_fallido(aplicacion, ana, caso, correos, monkeypatch):
    """CA6 (RF46 CA2): el caso vuelve a su estado anterior y se avisa."""
    _analizar(ana, caso["id"], caso["imagenes"][:1])  # el caso queda Analizado

    def fallar(_clave):
        raise OSError("almacenamiento caído")

    monkeypatch.setattr(aplicacion.extensions["almacenamiento"], "leer", fallar)
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]

    analisis = _detalle(ana, caso["id"], id_analisis)
    assert analisis["estado"] == "fallido"
    assert "error inesperado" in analisis["motivo_falla"]
    assert _caso(ana, caso["id"])["estado"] == "analizado"
    assert correos[-1].asunto.startswith("No se pudo completar el análisis")
    assert entradas_auditoria(aplicacion, "analisis.falla")[-1]["resultado"] == "fallido"


def test_analisis_interrumpido_queda_fallido(aplicacion, ana, caso, correos, cola_retenida):
    """CA6 (RF46 CA2): sin avance durante el tiempo máximo, la consulta lo da por fallido."""
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]
    with aplicacion.app_context():
        analisis = db.session.get(Analisis, id_analisis)
        analisis.actualizado_en = ahora_utc() - timedelta(minutes=16)
        db.session.commit()

    analisis = _detalle(ana, caso["id"], id_analisis)

    assert analisis["estado"] == "fallido"
    assert "se interrumpió" in analisis["motivo_falla"]
    assert _caso(ana, caso["id"])["estado"] == "borrador"
    assert correos[-1].asunto.startswith("No se pudo completar el análisis")
    # Si el trabajo retenido se ejecuta tarde, no hace nada.
    with aplicacion.app_context():
        from app.tareas.analisis import ejecutar_analisis  # pylint: disable=import-outside-toplevel
        ejecutar_analisis(id_analisis)
    assert _detalle(ana, caso["id"], id_analisis)["estado"] == "fallido"


def test_si_no_se_puede_encolar_queda_fallido(aplicacion, ana, caso):
    """CA6: con la cola caída, el pedido no deja el caso bloqueado En análisis."""
    class ColaCaida:  # pylint: disable=too-few-public-methods
        """Cola que no acepta trabajos."""

        def encolar(self, *_):
            """Falla siempre."""
            raise ConnectionError("Redis no responde")

    aplicacion.extensions["cola_analisis"] = ColaCaida()
    respuesta = _analizar(ana, caso["id"], caso["imagenes"])
    assert respuesta.status_code == 202
    assert respuesta.get_json()["analisis"]["estado"] == "fallido"
    assert _caso(ana, caso["id"])["estado"] == "borrador"


def test_analisis_de_otro_caso_no_se_encuentra(ana, caso):
    """RNF05: el id del análisis tiene que ser del caso indicado."""
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"]).get_json()["analisis"]["id"]
    otro = ana.post("/api/casos", json=CASO).get_json()["caso"]["id"]
    assert ana.get(f"/api/casos/{otro}/analisis/{id_analisis}").status_code == 404
