"""Pruebas de la copia de datos personales y de la eliminación de la cuenta.

Criterios de aceptación de la funcionalidad 019: CA1 a CA11.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
# Las pruebas de varias personas reciben muchos accesorios.
# pylint: disable=too-many-arguments,too-many-positional-arguments
import json
from datetime import timedelta

import pytest

from app.extensiones import db
from app.modelos.caso import AccesoCaso, Caso
from app.modelos.organizacion import Invitacion, Membresia, Organizacion
from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    datos_registro,
    entradas_auditoria,
    extraer_token,
    obtener_usuario,
)

CASO = {
    "espacio": "personal", "tipo": "laboral", "fecha_hecho": "2026-09-01",
    "lugar": "Planta de Juan Pérez", "descripcion": "Reclamo de Juan Pérez.",
}


@pytest.fixture
def ana(cuenta):
    """Persona que pide la copia o elimina su cuenta."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Otra persona, cuyos datos nunca deben aparecer en la copia de Ana."""
    return cuenta("beto@ejemplo.com", "Beto")


def _organizacion(cliente, nombre):
    respuesta = cliente.post(
        "/api/organizaciones", json={"nombre": nombre, "tipo": "estudio_juridico"}
    )
    return respuesta.get_json()["organizacion"]["id"]


def _sumar(referente, miembro, id_org, correo):
    id_inv = referente.post(
        f"/api/organizaciones/{id_org}/invitaciones", json={"correo": correo}
    ).get_json()["invitacion"]["id"]
    assert miembro.post(f"/api/invitaciones/{id_inv}/aceptacion").status_code == 200


def _caso(cliente, **cambios):
    respuesta = cliente.post("/api/casos", json={**CASO, **cambios})
    assert respuesta.status_code == 201, respuesta.get_json()
    return respuesta.get_json()["caso"]


def _enlaces(cliente):
    respuesta = cliente.post("/api/perfil/copia")
    assert respuesta.status_code == 200
    return respuesta.get_json()["enlaces"]


def _eliminar(cliente, contrasenia=CONTRASENIA_VALIDA):
    return cliente.delete("/api/perfil", json={"contrasenia": contrasenia})


# --- Copia de datos (CA1 a CA4) ---

def test_pedir_la_copia_da_enlaces_y_avisa_sin_enlace(aplicacion, ana, correos):
    """CA1: enlaces JSON y PDF que vencen a los 15 minutos, y aviso por correo."""
    respuesta = ana.post("/api/perfil/copia")
    cuerpo = respuesta.get_json()
    assert set(cuerpo["enlaces"]) == {"json", "pdf"}
    assert cuerpo["enlaces"]["json"].startswith("/api/perfil/copia/json?token=")
    assert "15 minutos" in cuerpo["mensaje"]
    aviso = correos[-1]
    assert aviso.destinatario == "ana@ejemplo.com"
    assert aviso.asunto == "Se generó una copia de tus datos"
    assert "/api/perfil/copia" not in aviso.texto
    entrada = entradas_auditoria(aplicacion, "cuenta.copia_solicitud")[-1]
    assert (entrada["id_usuario"], entrada["resultado"]) == (ana.id_usuario, "exitoso")


def test_la_copia_json_tiene_los_datos_de_la_persona(aplicacion, ana, beto):
    """CA2 y CA3: datos propios completos, sin datos de terceros ni contenido de casos."""
    id_org = _organizacion(ana, "Estudio Pérez")
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    _caso(ana)
    id_otra = _organizacion(beto, "Estudio Paz")
    beto.post(f"/api/organizaciones/{id_otra}/invitaciones", json={"correo": "ana@ejemplo.com"})

    respuesta = ana.get(_enlaces(ana)["json"])

    assert respuesta.status_code == 200
    assert respuesta.mimetype == "application/json"
    assert "attachment" in respuesta.headers["Content-Disposition"]
    assert respuesta.headers["Cache-Control"] == "no-store"
    copia = json.loads(respuesta.data)
    assert copia["cuenta"]["correo"] == "ana@ejemplo.com"
    assert copia["cuenta"]["perfil"] == "Abogado"
    assert copia["consentimiento"]["version_terminos"]
    assert copia["organizaciones"] == [{
        "nombre": "Estudio Pérez", "tipo": "Estudio Jurídico", "rol": "Referente",
        "cargo": None, "incorporado_en": copia["organizaciones"][0]["incorporado_en"],
    }]
    assert [i["organizacion"] for i in copia["invitaciones_pendientes"]] == ["Estudio Paz"]
    assert [c["tipo"] for c in copia["casos_a_cargo"]] == ["Laboral"]
    acciones = {a["accion"] for a in copia["actividad"]}
    assert {"cuenta.registro", "sesion.inicio", "caso.creacion"} <= acciones
    texto = respuesta.data.decode("utf-8")
    for ajeno in ("beto@ejemplo.com", "Beto", "Juan Pérez"):
        assert ajeno not in texto
    entrada = entradas_auditoria(aplicacion, "cuenta.copia_descarga")[-1]
    assert entrada["detalle"] == {"formato": "json"}


def test_la_copia_pdf_es_un_pdf(ana):
    """CA1: la copia legible en PDF."""
    respuesta = ana.get(_enlaces(ana)["pdf"])
    assert respuesta.status_code == 200
    assert respuesta.mimetype == "application/pdf"
    assert respuesta.data.startswith(b"%PDF")


def test_un_enlace_alterado_o_de_otra_persona_no_descarga(aplicacion, ana, beto):
    """CA4."""
    enlace_de_ana = _enlaces(ana)["json"]
    respuesta = beto.get(enlace_de_ana)
    assert respuesta.status_code == 400
    assert entradas_auditoria(aplicacion, "cuenta.copia_descarga")[-1]["detalle"] == {
        "motivo": "otra_cuenta", "formato": "json",
    }
    assert ana.get(enlace_de_ana + "x").status_code == 400
    assert ana.get("/api/perfil/copia/json").status_code == 400


def test_un_enlace_vencido_no_descarga(aplicacion, ana):
    """CA4: el enlace vence."""
    enlace = _enlaces(ana)["pdf"]
    aplicacion.config["VIGENCIA_COPIA_DATOS"] = timedelta(seconds=-1)
    respuesta = ana.get(enlace)
    assert respuesta.status_code == 400
    assert "venció" in respuesta.get_json()["mensaje"]


def test_el_enlace_exige_la_sesion(aplicacion, ana):
    """CA4: el enlace solo no alcanza."""
    enlace = _enlaces(ana)["json"]
    assert aplicacion.test_client().get(enlace).status_code == 401
    assert aplicacion.test_client().post("/api/perfil/copia").status_code == 401


# --- Eliminación de la cuenta (CA5 a CA11) ---

def test_la_baja_lista_los_casos_y_las_organizaciones_a_resolver(aplicacion, ana, beto):
    """CA5, CA6 y CA7: casos a cargo, Referente con otros miembros y organizaciones solas."""
    id_org = _organizacion(ana, "Estudio Pérez")
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    caso = _caso(ana)
    id_sola = _organizacion(ana, "Estudio Sola")
    _caso(ana, espacio=str(id_sola))

    situacion = ana.get("/api/perfil/baja").get_json()

    assert [c["numero"] for c in situacion["casos"]] == [caso["numero"]]
    assert situacion["casos"][0]["espacio"] == "Personal"
    assert situacion["referente_de"] == [{"id": id_org, "nombre": "Estudio Pérez"}]
    assert situacion["a_eliminar"] == [
        {"id": id_sola, "nombre": "Estudio Sola", "cantidad_casos": 1}
    ]
    assert situacion["puede_eliminar"] is False

    respuesta = _eliminar(ana)

    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "baja_pendiente")
    assert obtener_usuario(aplicacion) is not None
    entrada = entradas_auditoria(aplicacion, "cuenta.eliminacion")[-1]
    assert entrada["resultado"] == "rechazado"
    assert entrada["detalle"]["casos"] == 1


def test_con_todo_resuelto_puede_eliminar(ana):
    """CA5: sin casos ni organizaciones con otros miembros."""
    situacion = ana.get("/api/perfil/baja").get_json()
    assert situacion == {"casos": [], "referente_de": [], "a_eliminar": [], "puede_eliminar": True}


def test_contrasenia_incorrecta_no_elimina(aplicacion, ana):
    """CA8."""
    respuesta = _eliminar(ana, "Otra12345678")
    assert respuesta.status_code == 400
    assert "contrasenia" in respuesta.get_json()["errores"]
    assert obtener_usuario(aplicacion) is not None
    entrada = entradas_auditoria(aplicacion, "cuenta.eliminacion")[-1]
    assert (entrada["resultado"], entrada["detalle"]) == (
        "fallido", {"motivo": "contrasenia_incorrecta"},
    )


def test_eliminar_la_cuenta_suprime_todo_lo_que_depende_de_ella(aplicacion, ana, beto, correos):
    """CA7, CA9 y CA10."""
    # Ana es el único miembro de un estudio con un caso: se elimina con ella.
    id_sola = _organizacion(ana, "Estudio Sola")
    _caso(ana, espacio=str(id_sola))
    # Ana es miembro del estudio de Beto, con acceso a un caso.
    id_beto = _organizacion(beto, "Estudio Paz")
    _sumar(beto, ana, id_beto, "ana@ejemplo.com")
    caso_compartido = _caso(beto, espacio=str(id_beto))
    beto.post(
        f"/api/casos/{caso_compartido['id']}/accesos",
        json={"nivel": "colaboracion", "id_usuario": ana.id_usuario},
    )
    # Beto le pidió a Ana que acepte un caso personal.
    caso_personal = _caso(beto)
    beto.post(
        f"/api/casos/{caso_personal['id']}/transferencia", json={"destino": "ana@ejemplo.com"}
    )
    id_ana = ana.id_usuario

    respuesta = _eliminar(ana)

    assert respuesta.status_code == 200, respuesta.get_json()
    assert "eliminada" in respuesta.get_json()["mensaje"]
    with aplicacion.app_context():
        assert db.session.get(Organizacion, id_sola) is None
        assert Caso.query.filter_by(id_organizacion=id_sola).count() == 0
        assert Membresia.query.filter_by(id_usuario=id_ana).count() == 0
        assert AccesoCaso.query.filter_by(id_usuario=id_ana).count() == 0
        assert Invitacion.query.filter_by(correo="ana@ejemplo.com").count() == 0
        assert db.session.get(Caso, caso_personal["id"]).transferencia_a is None
        assert db.session.get(Caso, caso_compartido["id"]) is not None
    assert obtener_usuario(aplicacion) is None
    # La auditoría conserva las entradas sin el usuario (RN34).
    propias = [
        e for e in entradas_auditoria(aplicacion)
        if e["tipo_recurso"] == "usuario" and e["id_recurso"] == str(id_ana)
    ]
    assert propias and all(e["id_usuario"] is None for e in propias)
    eliminacion = entradas_auditoria(aplicacion, "cuenta.eliminacion")[-1]
    assert eliminacion["resultado"] == "exitoso"
    assert eliminacion["detalle"] == {"organizaciones_eliminadas": 1}
    assert entradas_auditoria(aplicacion, "organizacion.eliminacion")[-1]["detalle"]["motivo"] == (
        "baja_de_cuenta"
    )
    confirmacion = correos[-1]
    assert (confirmacion.destinatario, confirmacion.asunto) == (
        "ana@ejemplo.com", "Tu cuenta fue eliminada",
    )
    assert "Estudio Sola" in confirmacion.texto
    # La sesión quedó cerrada.
    assert ana.get("/api/perfil").status_code == 401


def test_las_otras_sesiones_dejan_de_valer(aplicacion, ana):
    """CA9: se cierran todas las sesiones."""
    otra = aplicacion.test_client()
    otra.post("/api/sesion", json={"correo": "ana@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA})
    assert otra.get("/api/perfil").status_code == 200
    assert _eliminar(ana).status_code == 200
    assert otra.get("/api/perfil").status_code == 401


def test_el_correo_puede_volver_a_registrarse(aplicacion, ana, correos):
    """CA11: la cuenta nueva no tiene datos de la anterior."""
    _caso(ana)
    situacion = ana.get("/api/perfil/baja").get_json()
    ana.delete(f"/api/casos/{situacion['casos'][0]['id']}", json={
        "confirmacion": situacion["casos"][0]["numero"],
    })
    assert _eliminar(ana).status_code == 200

    nuevo = aplicacion.test_client()
    respuesta = nuevo.post("/api/cuentas/registro", json=datos_registro(nombre="Ana María"))
    assert respuesta.status_code == 201
    nuevo.post("/api/cuentas/verificacion", json={"token": extraer_token(correos[-1])})
    nuevo.post(
        "/api/sesion", json={"correo": "ana@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA}
    )
    assert nuevo.get("/api/casos").get_json()["total"] == 0
    assert obtener_usuario(aplicacion).nombre == "Ana María"
