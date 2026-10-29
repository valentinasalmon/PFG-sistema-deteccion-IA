"""Pruebas del panel principal a través de la API (funcionalidad 013, RF48).

Ana es Referente de un estudio con Beto como miembro; Carla es otra cuenta
sin relación con ellos. En las pruebas la cola es sincrónica.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import io
from datetime import timedelta

import pytest
from PIL import Image

from app.extensiones import db
from app.modelos.caso import Caso
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import crear_estudio

CASO = {
    "espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
    "lugar": "Av. Corrientes 1234",
}


def _png():
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), (10, 20, 30)).save(salida, "PNG")
    return salida.getvalue()


def _crear_caso(cliente, **cambios):
    return cliente.post("/api/casos", json={**CASO, **cambios}).get_json()["caso"]


def _panel(cliente):
    respuesta = cliente.get("/api/panel")
    assert respuesta.status_code == 200
    return respuesta.get_json()["panel"]


@pytest.fixture
def ana(cuenta):
    """Referente del estudio."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Miembro del estudio de Ana."""
    return cuenta("beto@ejemplo.com", "Beto")


@pytest.fixture
def carla(cuenta):
    """Otra cuenta, sin relación con el estudio."""
    return cuenta("carla@ejemplo.com", "Carla")


@pytest.fixture
def estudio(ana, beto):
    """Estudio de Ana con Beto como miembro."""
    return crear_estudio(ana, beto, "beto@ejemplo.com")


def test_el_panel_exige_sesion(cliente):
    """Sin sesión no hay panel."""
    assert cliente.get("/api/panel").status_code == 401


def test_panel_vacio(ana):
    """Una cuenta nueva ve todas las secciones vacías."""
    panel = _panel(ana)

    assert panel == {
        "por_estado": {}, "recientes": [], "analisis_en_curso": [], "compartidos": [],
        "invitaciones": [], "transferencias": [], "proximos_a_destruir": [], "actividad": [],
    }


def test_casos_por_estado_recientes_y_actividad(ana, carla):
    """CA1 y CA2: resumen, últimos casos y eventos redactados; nada de casos ajenos."""
    primero = _crear_caso(ana)
    segundo = _crear_caso(ana, lugar="Ruta 2")
    ana.post(
        f"/api/casos/{segundo['id']}/imagenes",
        data={"archivo": (io.BytesIO(_png()), "frente.png")}, content_type="multipart/form-data",
    )
    _crear_caso(carla)

    panel = _panel(ana)

    assert panel["por_estado"] == {"borrador": 2}
    assert [c["numero"] for c in panel["recientes"]] == [segundo["numero"], primero["numero"]]
    assert panel["recientes"][0]["estado_nombre"] == "Borrador"
    textos = [evento["texto"] for evento in panel["actividad"]]
    assert textos == [
        f"Cargaste la imagen «frente.png» en {segundo['numero']}",
        f"Creaste el caso {segundo['numero']}",
        f"Creaste el caso {primero['numero']}",
    ]
    assert panel["actividad"][0]["id_caso"] == segundo["id"]
    assert all("ip" not in evento for evento in panel["actividad"])


def test_cambios_de_estado_y_analisis_en_la_actividad(ana):
    """El análisis y el cierre se redactan como eventos propios (RF48 CA2)."""
    caso = _crear_caso(ana)
    id_imagen = ana.post(
        f"/api/casos/{caso['id']}/imagenes",
        data={"archivo": (io.BytesIO(_png()), "frente.png")}, content_type="multipart/form-data",
    ).get_json()["imagen"]["id"]
    ana.post(f"/api/casos/{caso['id']}/analisis", json={"imagenes": [id_imagen]})
    ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "cerrar"})

    textos = [evento["texto"] for evento in _panel(ana)["actividad"]]

    numero = caso["numero"]
    assert textos[:4] == [
        f"Cerraste el caso {numero}",
        f"Terminó el análisis de {numero}",
        f"Se generó el informe PDF de {numero}",
        f"Pediste el análisis de 1 imagen(es) de {numero}",
    ]


def test_caso_compartido_recientemente(ana, beto, estudio):
    """CA1: Beto ve el caso que Ana le compartió y su actividad; Ana no lo ve como compartido."""
    caso = _crear_caso(ana, espacio=str(estudio))
    ana.post(
        f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )

    panel = _panel(beto)

    assert [c["caso"]["numero"] for c in panel["compartidos"]] == [caso["numero"]]
    assert panel["compartidos"][0]["nivel_nombre"] == "Lectura"
    assert panel["compartidos"][0]["responsable"] == "Ana López"
    assert panel["actividad"][0]["texto"] == f"Ana López compartió el caso {caso['numero']}"
    assert _panel(ana)["compartidos"] == []


def test_un_acceso_viejo_no_es_reciente(aplicacion, ana, beto, estudio):
    """Solo cuentan los accesos de los últimos 30 días."""
    caso = _crear_caso(ana, espacio=str(estudio))
    ana.post(
        f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )
    with aplicacion.app_context():
        acceso = db.session.get(Caso, caso["id"]).accesos[0]
        acceso.otorgado_en = ahora_utc() - timedelta(days=31)
        db.session.commit()

    assert _panel(beto)["compartidos"] == []


def test_invitaciones_y_transferencias_pendientes(ana, beto):
    """CA1 y CA3: la invitación y la transferencia que esperan respuesta."""
    id_org = ana.post(
        "/api/organizaciones", json={"nombre": "Estudio Pérez", "tipo": "estudio_juridico"}
    ).get_json()["organizacion"]["id"]
    ana.post(f"/api/organizaciones/{id_org}/invitaciones", json={"correo": "beto@ejemplo.com"})
    caso = _crear_caso(ana)
    ana.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": "beto@ejemplo.com"})

    panel = _panel(beto)

    assert [i["organizacion"]["nombre"] for i in panel["invitaciones"]] == ["Estudio Pérez"]
    assert [t["numero"] for t in panel["transferencias"]] == [caso["numero"]]
    assert panel["actividad"] == []  # el caso todavía no es suyo


def test_casos_proximos_a_destruirse(aplicacion, ana):
    """CA1 (RN31): los casos del Responsable que vencen dentro de 30 días."""
    proximo = _crear_caso(ana)
    lejano = _crear_caso(ana)
    for caso in (proximo, lejano):
        ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "cerrar"})
    with aplicacion.app_context():
        # Cerrado hace 5 años menos 10 días: vence dentro de 10 días.
        db.session.get(Caso, proximo["id"]).retencion_desde = (
            ahora_utc() - timedelta(days=5 * 365 - 8)
        )
        db.session.commit()

    panel = _panel(ana)

    assert [p["caso"]["numero"] for p in panel["proximos_a_destruir"]] == [proximo["numero"]]
    assert panel["proximos_a_destruir"][0]["vence_en"]


def test_analisis_en_curso(aplicacion, ana):
    """CA1: un análisis en cola aparece con su caso."""

    class ColaRetenida:  # pylint: disable=too-few-public-methods
        """Guarda los trabajos sin ejecutarlos."""

        def encolar(self, *argumentos):
            """No ejecuta nada."""
            return "retenido"

    aplicacion.extensions["cola_analisis"] = ColaRetenida()
    caso = _crear_caso(ana)
    id_imagen = ana.post(
        f"/api/casos/{caso['id']}/imagenes",
        data={"archivo": (io.BytesIO(_png()), "frente.png")}, content_type="multipart/form-data",
    ).get_json()["imagen"]["id"]
    ana.post(f"/api/casos/{caso['id']}/analisis", json={"imagenes": [id_imagen]})

    en_curso = _panel(ana)["analisis_en_curso"]

    assert [(a["caso"]["numero"], a["estado"], a["cantidad_imagenes"]) for a in en_curso] == [
        (caso["numero"], "en_cola", 1),
    ]
