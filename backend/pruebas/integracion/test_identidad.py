"""Pruebas de la verificación de identidad del Referente de una aseguradora (035).

Criterios de aceptación CA1 a CA7 y regla RN41. La verificación se activa
explícitamente con el proveedor simulado, porque en el entorno de pruebas
viene desactivada (igual que en producción mientras no esté Identik).
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import pytest

from app.extensiones import db
from app.integraciones.identidad import (
    ProveedorIdentidadSimulado,
    crear_proveedor_identidad,
)
from app.modelos.verificacion_identidad import VerificacionIdentidad
from pruebas.conftest import crear_estudio_pagado, entradas_auditoria
from pruebas.integracion import test_aseguradoras as base

_organizacion_de = base._organizacion_de  # pylint: disable=protected-access


@pytest.fixture
def nuevo_cliente(aplicacion):
    """Fábrica de clientes HTTP independientes (una persona por cliente)."""
    return aplicacion.test_client


@pytest.fixture
def administrador(aplicacion, nuevo_cliente, correos):
    """Cliente con la sesión de un Administrador (como en las pruebas de la 021)."""
    return base.administrador.__wrapped__(aplicacion, nuevo_cliente, correos)


@pytest.fixture
def rita(nuevo_cliente, correos):
    """Referente de Seguros Galicia, con la aseguradora todavía pendiente."""
    return base._registrar_aseguradora(  # pylint: disable=protected-access
        nuevo_cliente(), correos
    )


@pytest.fixture
def activa(aplicacion):
    """Activa la verificación de identidad con el proveedor simulado."""
    aplicacion.config["VERIFICACION_IDENTIDAD"] = "simulado"
    return aplicacion


def _token_de(respuesta):
    """El token del enlace que devolvió el inicio de la verificación."""
    return respuesta.get_json()["url"].rsplit("/identidad/", 1)[1]


def _iniciar(cliente):
    id_org = _organizacion_de(cliente)["id"]
    return id_org, cliente.post(f"/api/organizaciones/{id_org}/identidad")


# --- Proveedor ---

def test_el_proveedor_se_elige_por_configuracion():
    """Desactivado no crea proveedor; simulado crea el simulado; otro valor es un error."""
    assert crear_proveedor_identidad({"VERIFICACION_IDENTIDAD": "desactivado"}) is None
    proveedor = crear_proveedor_identidad(
        {"VERIFICACION_IDENTIDAD": "simulado", "URL_FRONTEND": "https://ejemplo.com/"}
    )
    assert isinstance(proveedor, ProveedorIdentidadSimulado)
    datos = proveedor.iniciar("abc", None)
    assert datos["url"] == "https://ejemplo.com/identidad/abc"
    assert datos["referencia"].startswith("SIM-")
    with pytest.raises(ValueError):
        crear_proveedor_identidad({"VERIFICACION_IDENTIDAD": "identik"})


# --- Inicio (CA1, CA2) ---

def test_el_referente_inicia_la_verificacion(aplicacion, activa, rita):
    """CA1: el Referente recibe el enlace y queda una verificación pendiente."""
    id_org, respuesta = _iniciar(rita)
    assert respuesta.status_code == 201, respuesta.get_json()
    assert "/identidad/" in respuesta.get_json()["url"]
    estado = rita.get(f"/api/organizaciones/{id_org}/identidad").get_json()["identidad"]
    assert (estado["activa"], estado["corresponde"], estado["estado"]) == (
        True, True, "pendiente",
    )
    with aplicacion.app_context():
        verificacion = db.session.query(VerificacionIdentidad).one()
        # Solo se guarda la huella del token, nunca el token.
        assert verificacion.huella_token != _token_de(respuesta)
        assert len(verificacion.huella_token) == 64


def test_sin_verificacion_activa_no_se_inicia(rita):
    """Con la verificación desactivada, el inicio se rechaza y el estado lo dice."""
    id_org, respuesta = _iniciar(rita)
    assert respuesta.status_code == 400
    estado = rita.get(f"/api/organizaciones/{id_org}/identidad").get_json()["identidad"]
    assert (estado["activa"], estado["estado"]) == (False, "sin_verificar")


def test_solo_corresponde_a_aseguradoras_pendientes(activa, cuenta):
    """CA2: un estudio jurídico no verifica identidad."""
    ana = cuenta("ana@estudio.com")
    id_org = crear_estudio_pagado(ana)
    estado = ana.get(f"/api/organizaciones/{id_org}/identidad").get_json()["identidad"]
    assert estado["corresponde"] is False
    assert ana.post(f"/api/organizaciones/{id_org}/identidad").status_code == 400


def test_quien_no_es_miembro_no_ve_ni_inicia(activa, rita, cuenta):
    """CA2: una persona ajena a la aseguradora recibe 404."""
    id_org = _organizacion_de(rita)["id"]
    ajeno = cuenta("ajeno@ejemplo.com")
    assert ajeno.get(f"/api/organizaciones/{id_org}/identidad").status_code == 404
    assert ajeno.post(f"/api/organizaciones/{id_org}/identidad").status_code == 404


# --- Página pública y resultado (CA3, CA6, CA7) ---

def test_la_pagina_publica_muestra_la_aseguradora(activa, rita, nuevo_cliente):
    """CA6: con el token, sin sesión, se ve la aseguradora y que es simulada."""
    _, respuesta = _iniciar(rita)
    publico = nuevo_cliente()
    datos = publico.get(f"/api/identidad/{_token_de(respuesta)}").get_json()["verificacion"]
    assert datos["aseguradora"] == "SEGUROS GALICIA S.A."
    assert (datos["simulada"], datos["estado"]) == (True, "pendiente")
    invalido = publico.get("/api/identidad/no-existe")
    assert invalido.status_code == 404
    assert invalido.get_json()["codigo"] == "verificacion_invalida"


def test_simular_aprobada_registra_el_resultado(aplicacion, activa, rita, nuevo_cliente):
    """CA3 y CA6: el resultado queda en la auditoría, sin datos biométricos."""
    id_org, respuesta = _iniciar(rita)
    token = _token_de(respuesta)
    ruta = f"/api/identidad/{token}/simulacion"
    resultado = nuevo_cliente().post(ruta, json={"resultado": "aprobada"})
    assert resultado.status_code == 200, resultado.get_json()
    assert resultado.get_json()["verificacion"]["estado"] == "aprobada"
    # Idempotente: un segundo aviso no cambia el resultado.
    otra = nuevo_cliente().post(ruta, json={"resultado": "rechazada"})
    assert otra.get_json()["verificacion"]["estado"] == "aprobada"
    entradas = entradas_auditoria(aplicacion, "organizacion.identidad")
    assert [e["detalle"]["operacion"] for e in entradas] == ["inicio", "resultado"]
    assert entradas[-1]["detalle"]["resultado"] == "aprobada"
    assert set(entradas[-1]["detalle"]) == {"operacion", "resultado", "proveedor", "referencia"}
    # Ya aprobada, no se vuelve a iniciar.
    assert rita.post(f"/api/organizaciones/{id_org}/identidad").status_code == 400


def test_despues_de_un_rechazo_se_puede_volver_a_intentar(activa, rita, nuevo_cliente):
    """CA7: tras un rechazo, el Referente inicia una verificación nueva."""
    id_org, respuesta = _iniciar(rita)
    nuevo_cliente().post(
        f"/api/identidad/{_token_de(respuesta)}/simulacion", json={"resultado": "rechazada"}
    )
    estado = rita.get(f"/api/organizaciones/{id_org}/identidad").get_json()["identidad"]
    assert (estado["estado"], estado["motivo"]) == ("rechazada", "Rechazada en la simulación.")
    _, segunda = _iniciar(rita)
    assert segunda.status_code == 201
    estado = rita.get(f"/api/organizaciones/{id_org}/identidad").get_json()["identidad"]
    assert estado["estado"] == "pendiente"


def test_simulacion_invalida_o_con_proveedor_real(aplicacion, activa, rita, nuevo_cliente):
    """Un resultado inválido se rechaza; sin proveedor simulado no se puede simular."""
    _, respuesta = _iniciar(rita)
    ruta = f"/api/identidad/{_token_de(respuesta)}/simulacion"
    assert nuevo_cliente().post(ruta, json={"resultado": "quizas"}).status_code == 400
    aplicacion.config["VERIFICACION_IDENTIDAD"] = "desactivado"
    assert nuevo_cliente().post(ruta, json={"resultado": "aprobada"}).status_code == 403


# --- Administrador (CA4, CA5, RN41) ---

def test_el_administrador_ve_la_identidad_y_no_aprueba_sin_ella(
    activa, administrador, rita, nuevo_cliente
):
    """CA4 y CA5: estado visible y aprobación bloqueada hasta que se verifique."""
    id_org = _organizacion_de(rita)["id"]
    pendientes = administrador.get("/api/administracion/aseguradoras-pendientes").get_json()
    assert pendientes["verificacion_identidad"] is True
    assert pendientes["aseguradoras"][0]["identidad"]["estado"] == "sin_verificar"
    ruta = f"/api/administracion/organizaciones/{id_org}/aprobacion"
    bloqueada = administrador.post(ruta)
    assert bloqueada.status_code == 400
    assert bloqueada.get_json()["codigo"] == "identidad_sin_verificar"

    _, respuesta = _iniciar(rita)
    nuevo_cliente().post(
        f"/api/identidad/{_token_de(respuesta)}/simulacion", json={"resultado": "aprobada"}
    )
    pendientes = administrador.get("/api/administracion/aseguradoras-pendientes").get_json()
    assert pendientes["aseguradoras"][0]["identidad"]["estado"] == "aprobada"
    assert administrador.post(ruta).status_code == 200
    assert _organizacion_de(rita)["estado"] == "activa"


def test_sin_verificacion_activa_se_aprueba_como_antes(administrador, rita):
    """Con la verificación desactivada, la aprobación no cambia (compatibilidad)."""
    pendientes = administrador.get("/api/administracion/aseguradoras-pendientes").get_json()
    assert pendientes["verificacion_identidad"] is False
    id_org = _organizacion_de(rita)["id"]
    ruta = f"/api/administracion/organizaciones/{id_org}/aprobacion"
    assert administrador.post(ruta).status_code == 200
