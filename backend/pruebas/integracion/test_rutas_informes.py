"""Pruebas de los informes PDF a través de la API.

Criterios de aceptación de la funcionalidad 008: CA1 y CA4 a CA9 (CA2 y CA3,
el contenido del informe, están en ``pruebas/unitarias/test_informe_analisis.py``).
La cola es sincrónica: el informe existe al volver del pedido de análisis.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import hashlib
import io
from pathlib import Path

import pytest
from PIL import Image

from app.extensiones import db
from app.informes import informe_analisis
from app.modelos.imagen import Imagen
from app.modelos.informe import Informe
from pruebas.conftest import crear_estudio, entradas_auditoria

CASO = {
    "espacio": "personal", "tipo": "laboral", "fecha_hecho": "2026-09-01",
    "lugar": "Planta industrial", "expediente": "EXP-12/2026",
}


def _png(color):
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), color).save(salida, "PNG")
    return salida.getvalue()


def _cargar(cliente, id_caso, contenido, nombre):
    return cliente.post(
        f"/api/casos/{id_caso}/imagenes", data={"archivo": (io.BytesIO(contenido), nombre)},
        content_type="multipart/form-data",
    ).get_json()["imagen"]["id"]


def _analizar(cliente, id_caso, ids):
    respuesta = cliente.post(f"/api/casos/{id_caso}/analisis", json={"imagenes": ids})
    return respuesta.get_json()["analisis"]["id"]


def _informes(cliente, id_caso):
    return cliente.get(f"/api/casos/{id_caso}/informes").get_json()["informes"]


def _descargar(cliente, aplicacion, id_caso, id_informe):
    url = cliente.get(f"/api/casos/{id_caso}/informes/{id_informe}/descarga").get_json()["url"]
    return aplicacion.test_client().get(url)


@pytest.fixture
def ana(cuenta):
    """Responsable del caso."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def caso(ana):
    """Caso personal de Ana con dos imágenes."""
    id_caso = ana.post("/api/casos", json=CASO).get_json()["caso"]["id"]
    imagenes = [_cargar(ana, id_caso, _png((i, i, i)), f"foto{i}.png") for i in (1, 2)]
    return {"id": id_caso, "imagenes": imagenes}


def _archivo(aplicacion, clave):
    return Path(aplicacion.config["DIRECTORIO_ALMACENAMIENTO"], clave)


# --- Generación (CA1, CA4, CA5) ---

def test_al_finalizar_el_analisis_se_genera_el_informe(aplicacion, ana, caso, correos):
    """CA1: el PDF se guarda con su huella y el correo avisa que está disponible."""
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"])

    informes = _informes(ana, caso["id"])
    assert len(informes) == 1
    informe = informes[0]
    assert informe["id_analisis"] == id_analisis
    assert informe["solicitante"] == "Ana López"
    assert informe["imagenes"] == ["foto1.png", "foto2.png"]
    archivo = _descargar(ana, aplicacion, caso["id"], informe["id"])
    assert archivo.status_code == 200
    assert archivo.data.startswith(b"%PDF")
    assert hashlib.sha256(archivo.data).hexdigest() == informe["huella"]
    assert "attachment" in archivo.headers["Content-Disposition"]
    detalle = ana.get(f"/api/casos/{caso['id']}/analisis/{id_analisis}").get_json()["analisis"]
    assert detalle["informe"]["id"] == informe["id"]
    assert ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]["estado"] == "analizado"
    assert "El informe PDF ya está disponible" in correos[-1].texto
    entrada = entradas_auditoria(aplicacion, "informe.generacion")[-1]
    assert entrada["detalle"]["sha256"] == informe["huella"]
    assert entradas_auditoria(aplicacion, "informe.descarga")[-1]["resultado"] == "exitoso"


def test_un_analisis_nuevo_genera_otro_informe_sin_tocar_el_anterior(aplicacion, ana, caso):
    """CA4 (RF44 CA4, RN25)."""
    _analizar(ana, caso["id"], caso["imagenes"][:1])
    primero = _informes(ana, caso["id"])[0]
    with aplicacion.app_context():
        clave = db.session.get(Informe, primero["id"]).clave
    contenido = _archivo(aplicacion, clave).read_bytes()

    _analizar(ana, caso["id"], caso["imagenes"])

    informes = _informes(ana, caso["id"])
    assert [i["id"] for i in informes][1] == primero["id"]
    assert informes[1]["huella"] == primero["huella"]
    assert _archivo(aplicacion, clave).read_bytes() == contenido
    assert len(informes[0]["imagenes"]) == 2


def test_las_imagenes_del_informe_no_se_eliminan_y_el_caso_reabre_en_analizado(ana, caso):
    """CA5 (RN24, RF29 CA1)."""
    _analizar(ana, caso["id"], caso["imagenes"][:1])
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert [i["en_informe"] for i in imagenes] == [True, False]

    respuesta = ana.delete(f"/api/casos/{caso['id']}/imagenes/{caso['imagenes'][0]}")
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "imagen_en_informe")
    assert ana.delete(f"/api/casos/{caso['id']}/imagenes/{caso['imagenes'][1]}").status_code == 200

    ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "cerrar"})
    ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "reabrir"})
    assert ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]["estado"] == "analizado"


def test_una_imagen_alterada_no_queda_marcada(aplicacion, ana, caso):
    """CA5: solo se marcan las imágenes que el informe realmente incluye."""
    with aplicacion.app_context():
        clave = db.session.get(Imagen, caso["imagenes"][0]).clave
    _archivo(aplicacion, clave).write_bytes(_png((200, 0, 0)))
    _analizar(ana, caso["id"], caso["imagenes"])
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert [i["en_informe"] for i in imagenes] == [False, True]


# --- Falla del informe (CA6) ---

def test_si_falla_el_informe_el_analisis_finaliza_y_se_puede_regenerar(
    aplicacion, ana, caso, correos, monkeypatch
):
    """CA6."""
    def fallar(*_):
        raise RuntimeError("sin fuentes")

    monkeypatch.setattr(informe_analisis, "generar_pdf", fallar)
    id_analisis = _analizar(ana, caso["id"], caso["imagenes"])

    detalle = ana.get(f"/api/casos/{caso['id']}/analisis/{id_analisis}").get_json()["analisis"]
    assert (detalle["estado"], detalle["informe"]) == ("finalizado", None)
    assert detalle["imagenes"][0]["resultados"]
    assert _informes(ana, caso["id"]) == []
    assert "No se pudo generar el informe PDF" in correos[-1].texto
    imagenes = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]
    assert not any(i["en_informe"] for i in imagenes)

    monkeypatch.undo()
    regenerar = f"/api/casos/{caso['id']}/analisis/{id_analisis}/informe"
    respuesta = ana.post(regenerar)
    assert respuesta.status_code == 201
    assert len(_informes(ana, caso["id"])) == 1
    otra = ana.post(regenerar)
    assert (otra.status_code, otra.get_json()["codigo"]) == (409, "informe_no_regenerable")
    assert ana.post(f"/api/casos/{caso['id']}/analisis/999/informe").status_code == 404


# --- Permisos (CA7, CA8) ---

def test_el_lector_consulta_y_descarga_pero_no_regenera(aplicacion, ana, cuenta):
    """CA7 y CA8: Responsable, Colaboradores y Lectores descargan; sin permiso, 404."""
    beto = cuenta("beto@ejemplo.com", "Beto")
    carla = cuenta("carla@ejemplo.com", "Carla")
    id_org = crear_estudio(ana, beto, "beto@ejemplo.com")
    id_caso = ana.post("/api/casos", json={**CASO, "espacio": str(id_org)}).get_json()["caso"]["id"]
    id_analisis = _analizar(ana, id_caso, [_cargar(ana, id_caso, _png((5, 5, 5)), "a.png")])
    ana.post(
        f"/api/casos/{id_caso}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )

    informe = _informes(beto, id_caso)[0]
    assert _descargar(beto, aplicacion, id_caso, informe["id"]).status_code == 200
    assert beto.post(f"/api/casos/{id_caso}/analisis/{id_analisis}/informe").status_code == 403
    assert carla.get(f"/api/casos/{id_caso}/informes").status_code == 404
    otro = ana.post("/api/casos", json=CASO).get_json()["caso"]["id"]
    assert ana.get(f"/api/casos/{otro}/informes/{informe['id']}/descarga").status_code == 404


# --- Eliminación (CA9) ---

def test_eliminar_el_caso_borra_los_pdf(aplicacion, ana, caso):
    """CA9 (RN21): la auditoría guarda la huella del PDF junto con las de las imágenes."""
    _analizar(ana, caso["id"], caso["imagenes"])
    informe = _informes(ana, caso["id"])[0]
    with aplicacion.app_context():
        clave = db.session.get(Informe, informe["id"]).clave
    assert _archivo(aplicacion, clave).is_file()
    numero = ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]["numero"]

    ana.delete(f"/api/casos/{caso['id']}", json={"confirmacion": numero})

    assert not _archivo(aplicacion, clave).exists()
    entrada = entradas_auditoria(aplicacion, "caso.eliminacion")[-1]
    assert informe["huella"] in entrada["detalle"]["sha256_eliminados"]
    assert len(entrada["detalle"]["sha256_eliminados"]) == 3


# --- Informe verificable (funcionalidad 026) ---

def test_el_informe_tiene_codigo_y_su_huella_queda_sellada(aplicacion, ana, caso):
    """RF55 CA1 y CA2: código de verificación, QR en el PDF y sello de la huella del PDF."""
    _analizar(ana, caso["id"], caso["imagenes"])
    informe = _informes(ana, caso["id"])[0]

    assert len(informe["codigo_verificacion"]) == 12
    assert informe["sello"]["estado"] == "sellado" and informe["sello"]["simulado"] is True
    entrada = entradas_auditoria(aplicacion, "imagen.sello")[-1]
    assert entrada["detalle"]["tipo"] == "informe"
    assert entrada["detalle"]["sha256"] == informe["huella"]


def test_verificacion_publica_por_codigo_y_por_huella(aplicacion, ana, caso):
    """RF55 CA3: sin sesión, por código (con o sin guiones) o por huella; nunca datos del caso."""
    _analizar(ana, caso["id"], caso["imagenes"])
    informe = _informes(ana, caso["id"])[0]
    codigo = informe["codigo_verificacion"]
    visitante = aplicacion.test_client()

    legible = "-".join(codigo[i:i + 4] for i in range(0, 12, 4)).lower()
    for consulta in (f"codigo={legible}", f"huella={informe['huella']}"):
        respuesta = visitante.get(f"/api/verificacion?{consulta}")
        assert respuesta.status_code == 200, consulta
        datos = respuesta.get_json()["informe"]
        assert datos["huella"] == informe["huella"] and datos["sello"]["estado"] == "sellado"
        assert "caso" not in datos and "EXP-12/2026" not in respuesta.get_data(as_text=True)

    assert visitante.get("/api/verificacion?codigo=NOEXISTE1234").status_code == 404
    assert visitante.get("/api/verificacion?huella=" + "0" * 64).status_code == 404
    assert visitante.get("/api/verificacion").status_code == 404
