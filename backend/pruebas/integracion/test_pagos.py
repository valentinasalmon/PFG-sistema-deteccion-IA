"""Pruebas del pago del plan en el registro y en la organización (funcionalidad 032).

Criterios de aceptación de la especificación 032 que se comprueban en el
backend: CA1, CA3 a CA9.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import pytest

from app.extensiones import db
from app.modelos.cobro import Cobro
from app.modelos.organizacion import Organizacion
from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    ID_SEGUROS_GALICIA,
    datos_registro,
    entradas_auditoria,
    extraer_token,
    pagar,
)

CASO = {"tipo": "automovilistico", "fecha_hecho": "2026-09-01", "lugar": "Av. Corrientes 1234"}


def _registrar(cliente, **cambios):
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(**cambios))
    assert respuesta.status_code == 201, respuesta.get_json()
    return respuesta


def _entrar(cliente, correos, correo):
    token = extraer_token(next(c for c in reversed(correos) if c.destinatario == correo))
    cliente.post("/api/cuentas/verificacion", json={"token": token})
    respuesta = cliente.post(
        "/api/sesion", json={"correo": correo, "contrasenia": CONTRASENIA_VALIDA}
    )
    assert respuesta.status_code == 200
    return cliente


def _organizacion(cliente):
    return cliente.get("/api/organizaciones").get_json()["organizaciones"][0]


def test_el_independiente_no_paga(cliente):
    """CA1: sin estudio no hay plan ni pago."""
    assert _registrar(cliente).get_json()["pago"] is None


def test_estudio_en_el_registro_con_plan_y_pago(aplicacion, cliente, correos):
    """CA3 y CA4: el estudio espera el pago y queda activo al acreditarse."""
    respuesta = _registrar(cliente, nombre_estudio="Estudio Salmón", plan="profesional")
    token = respuesta.get_json()["pago"]["token"]

    cobro = cliente.get(f"/api/pagos/{token}").get_json()["cobro"]
    assert cobro["estado"] == "pendiente" and cobro["referencia"].startswith("EVD-")
    assert cobro["organizacion"]["nombre"] == "Estudio Salmón"
    assert cobro["plan"] == {
        "codigo": "profesional", "nombre": "Organización Profesional", "precio": None,
    }
    assert len(cobro["cvu"]) == 22 and cobro["alias"].startswith("EVIDENTIA.")
    assert cobro["permite_simular"] is True

    _entrar(cliente, correos, "ana@ejemplo.com")
    organizacion = _organizacion(cliente)
    assert organizacion["estado"] == "pago_pendiente"
    ruta_invitar = f"/api/organizaciones/{organizacion['id']}/invitaciones"
    invitar = cliente.post(ruta_invitar, json={"correo": "beto@ejemplo.com"})
    assert invitar.status_code == 409 and invitar.get_json()["codigo"] == "pago_pendiente"
    caso = cliente.post("/api/casos", json={**CASO, "espacio": str(organizacion["id"])})
    assert caso.status_code == 400

    acreditado = pagar(cliente, respuesta)
    assert acreditado["estado"] == "acreditado" and acreditado["acreditado_en"]
    assert _organizacion(cliente)["estado"] == "activa"
    plan = cliente.get(f"/api/organizaciones/{organizacion['id']}/plan").get_json()["plan"]
    assert plan["codigo"] == "profesional"
    operaciones = [e["detalle"]["operacion"] for e in entradas_auditoria(
        aplicacion, "organizacion.cobro"
    )]
    assert operaciones == ["crear", "acreditar"]
    # Acreditar de nuevo no cambia nada.
    assert pagar(cliente, respuesta)["estado"] == "acreditado"


def test_correo_existente_responde_igual(aplicacion, cliente, correos):
    """CA5: con un correo ya registrado la respuesta y el pago son iguales (RF01 CA3)."""
    _registrar(cliente)
    repetido = _registrar(cliente, nombre_estudio="Estudio Copia")
    token = repetido.get_json()["pago"]["token"]
    assert set(repetido.get_json()) == {"mensaje", "pago"}
    cobro = cliente.get(f"/api/pagos/{token}").get_json()["cobro"]
    assert cobro["organizacion"]["nombre"] == "Estudio Copia"
    assert pagar(cliente, repetido)["estado"] == "acreditado"
    with aplicacion.app_context():
        assert Organizacion.query.count() == 0
        assert Cobro.query.one().id_organizacion is None


def test_plan_invalido_y_enlace_inventado(cliente):
    """Un plan que no existe se rechaza y un enlace inventado no sirve."""
    respuesta = cliente.post(
        "/api/cuentas/registro", json=datos_registro(nombre_estudio="X", plan="oro")
    )
    assert respuesta.status_code == 400
    assert cliente.get("/api/pagos/inventado").status_code == 404
    assert cliente.post("/api/pagos/inventado/simulacion").status_code == 404


def test_aseguradora_paga_antes_de_la_aprobacion_y_se_devuelve_al_rechazar(aplicacion, correos):
    """CA4 y CA6: la aseguradora pagada espera la aprobación; rechazada, se devuelve."""
    rita = aplicacion.test_client()
    respuesta = _registrar(
        rita, correo="rita@galicia.com", nombre="Rita", perfil="aseguradora", colegio=None,
        id_aseguradora=ID_SEGUROS_GALICIA, plan="basico",
    )
    _entrar(rita, correos, "rita@galicia.com")
    assert _organizacion(rita)["estado"] == "pago_pendiente"

    admin = aplicacion.test_client()
    _registrar(admin, correo="admin@plataforma.com")
    _entrar(admin, correos, "admin@plataforma.com")
    aplicacion.test_cli_runner().invoke(args=["administracion", "promover", "admin@plataforma.com"])
    admin.post(
        "/api/sesion", json={"correo": "admin@plataforma.com", "contrasenia": CONTRASENIA_VALIDA}
    )
    pendientes = admin.get("/api/administracion/aseguradoras-pendientes").get_json()
    assert pendientes["aseguradoras"] == []  # sin pago no llega al Administrador

    pagar(rita, respuesta)
    assert _organizacion(rita)["estado"] == "pendiente"
    id_org = admin.get("/api/administracion/aseguradoras-pendientes").get_json()[
        "aseguradoras"][0]["id"]
    rechazo = admin.post(
        f"/api/administracion/organizaciones/{id_org}/rechazo", json={"motivo": "No corresponde."}
    )
    assert rechazo.status_code == 200
    with aplicacion.app_context():
        cobro = Cobro.query.one()
        assert cobro.estado == "devuelto" and cobro.id_organizacion is None
    assert entradas_auditoria(aplicacion, "organizacion.cobro")[-1]["detalle"]["operacion"] == (
        "devolver"
    )


@pytest.fixture
def ana(cuenta):
    """Abogada independiente con la sesión iniciada."""
    return cuenta("ana@ejemplo.com")


def test_crear_el_estudio_desde_el_perfil_y_retomar_el_pago(ana):
    """CA7 y CA9: el estudio nuevo espera el pago; el Referente puede retomarlo."""
    respuesta = ana.post(
        "/api/organizaciones",
        json={"nombre": "Estudio Pérez", "tipo": "estudio_juridico", "plan": "profesional"},
    )
    assert respuesta.status_code == 201
    id_org = respuesta.get_json()["organizacion"]["id"]
    assert respuesta.get_json()["organizacion"]["estado"] == "pago_pendiente"
    viejo = respuesta.get_json()["pago"]["token"]

    retomado = ana.post(f"/api/organizaciones/{id_org}/cobro")
    assert retomado.status_code == 201
    assert ana.get(f"/api/pagos/{viejo}").status_code == 404  # solo vale el último enlace
    pagar(ana, retomado)
    plan = ana.get(f"/api/organizaciones/{id_org}/plan").get_json()["plan"]
    assert plan["codigo"] == "profesional" and plan["estado_organizacion"] == "activa"
    otra_vez = ana.post(f"/api/organizaciones/{id_org}/cobro")
    assert otra_vez.status_code == 409 and otra_vez.get_json()["codigo"] == "sin_pago"


def test_no_se_cambia_el_plan_con_el_pago_pendiente(ana):
    """CA8: con el pago del alta pendiente no se puede pedir otro plan."""
    respuesta = ana.post(
        "/api/organizaciones", json={"nombre": "Estudio", "tipo": "estudio_juridico"}
    )
    id_org = respuesta.get_json()["organizacion"]["id"]
    cambio = ana.post(f"/api/organizaciones/{id_org}/plan", json={"plan": "profesional"})
    assert cambio.status_code == 409 and cambio.get_json()["codigo"] == "pago_pendiente"


def test_los_planes_son_publicos(cliente):
    """Los planes, sus límites y el precio a confirmar, sin sesión."""
    datos = cliente.get("/api/catalogos/planes").get_json()
    assert [p["codigo"] for p in datos["planes"]] == ["basico", "profesional"]
    assert datos["planes"][0]["miembros"] == 5 and datos["planes"][1]["miembros"] == 25
    assert all(p["precio"] is None for p in datos["planes"])
    assert datos["personal"]["analisis_mes"] == 10


def test_cuenta_de_prueba_queda_con_el_estudio_activo(aplicacion):
    """La cuenta de prueba no pasa por la pantalla de pago."""
    assert aplicacion.test_cli_runner().invoke(
        args=["administracion", "cuenta-de-prueba"]
    ).exit_code == 0
    with aplicacion.app_context():
        assert db.session.query(Organizacion).one().estado == "activa"
