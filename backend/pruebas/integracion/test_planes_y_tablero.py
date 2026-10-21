"""Pruebas de planes, pago simulado, límite de análisis, tablero y listados (014).

Ana es Referente de un estudio con Beto como miembro; el Administrador se
promueve desde la terminal. En las pruebas la cola es sincrónica.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import io

import pytest
from PIL import Image

from pruebas.conftest import crear_estudio, entradas_auditoria

CASO = {"espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
        "lugar": "Av. Corrientes 1234"}


def _png():
    salida = io.BytesIO()
    Image.new("RGB", (64, 48), (10, 20, 30)).save(salida, "PNG")
    return salida.getvalue()


def _caso_con_imagen(cliente, **cambios):
    caso = cliente.post("/api/casos", json={**CASO, **cambios}).get_json()["caso"]
    imagen = cliente.post(
        f"/api/casos/{caso['id']}/imagenes",
        data={"archivo": (io.BytesIO(_png()), "frente.png")}, content_type="multipart/form-data",
    ).get_json()["imagen"]
    return caso, imagen


@pytest.fixture
def ana(cuenta):
    """Referente del estudio."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Miembro del estudio."""
    return cuenta("beto@ejemplo.com", "Beto")


@pytest.fixture
def estudio(ana, beto):
    """Estudio de Ana con Beto como miembro."""
    return crear_estudio(ana, beto, "beto@ejemplo.com")


@pytest.fixture
def administrador(aplicacion, cuenta):
    """Cuenta promovida a Administrador desde la terminal."""
    aplicacion.test_cli_runner().invoke(args=["administracion", "cuenta-de-prueba"])
    cliente = aplicacion.test_client()
    respuesta = cliente.post(
        "/api/sesion", json={"correo": "prueba@evidentia.local", "contrasenia": "Prueba12345"}
    )
    assert respuesta.status_code == 200
    return cliente


# --- Plan y consumo (RF20) ---

def test_plan_y_consumo_de_la_organizacion(ana, estudio):
    """CA1: nombre, límites y consumo del período."""
    plan = ana.get(f"/api/organizaciones/{estudio}/plan").get_json()["plan"]

    assert plan["nombre"] == "Organización Básico"
    assert plan["consumo"] == {"miembros": 2, "analisis_mes": 0}
    assert plan["limites"]["analisis_mes"] == 100
    assert plan["puede_cambiar"] is True
    assert [p["codigo"] for p in plan["disponibles"]] == ["basico", "profesional"]


def test_cambio_de_plan_con_pago_simulado(aplicacion, ana, estudio):
    """CA2: se aplica de inmediato y queda auditado como pago simulado."""
    respuesta = ana.post(f"/api/organizaciones/{estudio}/plan", json={"plan": "profesional"})

    assert respuesta.status_code == 200
    assert "simulado" in respuesta.get_json()["mensaje"]
    assert respuesta.get_json()["plan"]["limites"]["miembros"] == 25
    entrada = entradas_auditoria(aplicacion, "organizacion.cambio_plan")[-1]
    assert entrada["detalle"] == {"anterior": "basico", "nuevo": "profesional", "pago": "simulado"}


def test_solo_el_referente_cambia_el_plan(beto, estudio):
    """Un miembro ve el plan pero no puede cambiarlo."""
    ruta = f"/api/organizaciones/{estudio}/plan"
    assert beto.get(ruta).get_json()["plan"]["puede_cambiar"] is False
    assert beto.post(ruta, json={"plan": "profesional"}).status_code == 403


def test_plan_inexistente(ana, estudio):
    """Un plan que no existe se rechaza."""
    assert ana.post(f"/api/organizaciones/{estudio}/plan", json={"plan": "oro"}).status_code == 400


def test_plan_personal(ana):
    """El abogado ve el plan de su espacio personal."""
    plan = ana.get("/api/perfil/plan").get_json()["plan"]
    assert plan["nombre"] == "Personal" and plan["limites"]["analisis_mes"] == 10


# --- Límite mensual de análisis (RF19 CA2) ---

def test_limite_mensual_de_analisis(aplicacion, ana):
    """Al alcanzar el límite se rechaza con la fecha de renovación."""
    aplicacion.config["PLAN_PERSONAL"] = {**aplicacion.config["PLAN_PERSONAL"], "analisis_mes": 1}
    caso, imagen = _caso_con_imagen(ana)
    pedido = ana.post(f"/api/casos/{caso['id']}/analisis", json={"imagenes": [imagen["id"]]})
    assert pedido.status_code == 202

    otro, otra = _caso_con_imagen(ana, lugar="Ruta 2")
    respuesta = ana.post(f"/api/casos/{otro['id']}/analisis", json={"imagenes": [otra["id"]]})

    assert respuesta.status_code == 409
    assert respuesta.get_json()["codigo"] == "limite_de_analisis"
    assert "se renueva el" in respuesta.get_json()["mensaje"]


# --- Tablero y listados (RF21, RF22) ---

def test_tablero_del_administrador(administrador, ana, estudio):
    """CA1 y CA2: indicadores agregados, sin casos identificables."""
    _caso_con_imagen(ana)

    tablero = administrador.get("/api/administracion/tablero").get_json()["tablero"]

    assert tablero["usuarios_por_perfil"]["abogado"] == 3
    assert tablero["organizaciones_por_tipo"]["estudio_juridico"] == 2
    assert tablero["casos_por_estado"] == {"borrador": 1}
    assert sum(tablero["altas_por_mes"].values()) == 3
    assert "CASO" not in str(tablero)


def test_tablero_filtra_por_fechas(administrador):
    """Un rango sin datos devuelve series vacías; fechas inválidas, error."""
    tablero = administrador.get(
        "/api/administracion/tablero?desde=2001-01-01&hasta=2001-12-31"
    ).get_json()["tablero"]
    assert tablero["altas_por_mes"] == {} and tablero["analisis_por_mes"] == {}
    assert administrador.get("/api/administracion/tablero?desde=ayer").status_code == 400


def test_listados_del_administrador(administrador, ana, beto, estudio):
    """RF22: búsqueda y paginado, de solo lectura."""
    usuarios = administrador.get("/api/administracion/usuarios?busqueda=beto").get_json()
    assert [u["correo"] for u in usuarios["usuarios"]] == ["beto@ejemplo.com"]
    assert usuarios["usuarios"][0]["estado"] == "Activa"

    ruta = "/api/administracion/organizaciones?busqueda=pérez"
    organizaciones = administrador.get(ruta).get_json()
    assert organizaciones["organizaciones"][0]["miembros"] == 2
    assert organizaciones["organizaciones"][0]["plan"] == "Organización Básico"


def test_solo_el_administrador(ana):
    """CA3: cualquier otra cuenta recibe acceso denegado."""
    for ruta in ("tablero", "usuarios", "organizaciones"):
        assert ana.get(f"/api/administracion/{ruta}").status_code == 403
