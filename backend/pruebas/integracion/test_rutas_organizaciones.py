"""Pruebas de organizaciones, invitaciones y membresías a través de la API.

Criterios de aceptación de la funcionalidad 004: CA1 a CA22.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
from datetime import timedelta

import pytest

from app.extensiones import db
from app.modelos.organizacion import Invitacion, Membresia
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import entradas_auditoria, extraer_token, pagar

ORGANIZACION = {"nombre": "Estudio Pérez", "tipo": "estudio_juridico", "telefono": "11 5555-0000"}


@pytest.fixture
def ana(cuenta):
    """Usuaria que crea las organizaciones."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Segundo usuario, para invitar."""
    return cuenta("beto@ejemplo.com", nombre="Beto")


def _crear_organizacion(cliente, **cambios):
    respuesta = cliente.post("/api/organizaciones", json={**ORGANIZACION, **cambios})
    assert respuesta.status_code == 201, respuesta.get_json()
    pagar(cliente, respuesta)
    return respuesta.get_json()["organizacion"]["id"]


def _invitar(cliente, id_org, correo, cargo=None):
    return cliente.post(
        f"/api/organizaciones/{id_org}/invitaciones", json={"correo": correo, "cargo": cargo}
    )


def _sumar(cliente_referente, cliente_invitado, id_org, correo, cargo=None):
    """Invita y acepta: el invitado queda como miembro."""
    id_inv = _invitar(cliente_referente, id_org, correo, cargo).get_json()["invitacion"]["id"]
    assert cliente_invitado.post(f"/api/invitaciones/{id_inv}/aceptacion").status_code == 200
    return id_inv


def _miembros(cliente, id_org):
    return cliente.get(f"/api/organizaciones/{id_org}/miembros").get_json()["miembros"]


def _ultima(aplicacion, accion):
    return entradas_auditoria(aplicacion, accion)[-1]


# --- Organizaciones (CA1 a CA4) ---

def test_crear_organizacion_con_plan_inicial_y_referente(aplicacion, ana):
    """CA1."""
    respuesta = ana.post("/api/organizaciones", json=ORGANIZACION)
    organizacion = respuesta.get_json()["organizacion"]
    assert respuesta.status_code == 201
    assert organizacion["mi_rol"] == "referente"
    assert organizacion["tipo_nombre"] == "Estudio Jurídico"
    assert organizacion["plan"] == {
        "codigo": "basico", "nombre": "Organización Básico", "limite_miembros": 5,
    }
    assert organizacion["correo_contacto"] is None
    entrada = _ultima(aplicacion, "organizacion.creacion")
    assert entrada["tipo_recurso"] == "organizacion"
    assert entrada["id_recurso"] == str(organizacion["id"])


def test_la_sesion_indica_si_el_usuario_es_miembro(ana):
    """028: el menú muestra «Organizaciones» solo a quien es miembro de alguna."""
    assert ana.get("/api/sesion").get_json()["usuario"]["en_organizacion"] is False
    _crear_organizacion(ana)
    assert ana.get("/api/sesion").get_json()["usuario"]["en_organizacion"] is True


def test_crear_organizacion_valida_los_datos(ana):
    """CU08 3a: datos inválidos señalados por campo."""
    respuesta = ana.post(
        "/api/organizaciones", json={"nombre": "", "tipo": "otro", "correo_contacto": "x"}
    )
    errores = respuesta.get_json()["errores"]
    assert respuesta.status_code == 400
    assert set(errores) == {"nombre", "tipo", "correo_contacto"}
    assert errores["correo_contacto"] == "El correo electrónico no es válido."


def test_varias_organizaciones_conservan_las_membresias(ana):
    """CA2: crear otra organización no quita las anteriores (RN06)."""
    _crear_organizacion(ana)
    _crear_organizacion(ana, nombre="Estudio Abril")
    nombres = [o["nombre"] for o in ana.get("/api/organizaciones").get_json()["organizaciones"]]
    assert nombres == ["Estudio Abril", "Estudio Pérez"]


def test_el_referente_edita_y_queda_en_la_auditoria(aplicacion, ana):
    """CA3: valor anterior y nuevo de cada campo modificado."""
    id_org = _crear_organizacion(ana)
    respuesta = ana.patch(
        f"/api/organizaciones/{id_org}",
        json={"nombre": "Estudio Pérez y Asociados", "telefono": "", "correo_contacto": "a@b.com"},
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["organizacion"]["telefono"] is None
    assert _ultima(aplicacion, "organizacion.edicion")["detalle"]["cambios"] == {
        "nombre": {"anterior": "Estudio Pérez", "nuevo": "Estudio Pérez y Asociados"},
        "telefono": {"anterior": "11 5555-0000", "nuevo": None},
        "correo_contacto": {"anterior": None, "nuevo": "a@b.com"},
    }


def test_un_miembro_no_puede_editar(aplicacion, ana, beto):
    """CA3 y CA22."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    respuesta = beto.patch(f"/api/organizaciones/{id_org}", json={"nombre": "Otro"})
    assert respuesta.status_code == 403
    assert respuesta.get_json()["codigo"] == "acceso_denegado"
    entrada = _ultima(aplicacion, "organizacion.edicion")
    assert (entrada["resultado"], entrada["detalle"]["motivo"]) == ("rechazado", "no_es_referente")


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", ""), ("patch", ""), ("delete", ""), ("get", "/miembros"),
        ("get", "/invitaciones"), ("post", "/invitaciones"), ("post", "/abandono"),
    ],
)
def test_quien_no_es_miembro_no_ve_la_organizacion(ana, beto, metodo, ruta):
    """CA4: misma respuesta que si no existiera."""
    id_org = _crear_organizacion(ana)
    # Cuerpos válidos: así la respuesta depende solo del acceso, no de la validación.
    if (metodo, ruta) == ("delete", ""):
        cuerpo = {"confirmacion": "Estudio Pérez"}
    elif ruta == "/invitaciones":
        cuerpo = {"correo": "x@ejemplo.com"}
    else:
        cuerpo = {}
    respuesta = getattr(beto, metodo)(f"/api/organizaciones/{id_org}{ruta}", json=cuerpo)
    inexistente = getattr(beto, metodo)(f"/api/organizaciones/9999{ruta}", json=cuerpo)
    assert respuesta.status_code == inexistente.status_code == 404
    assert respuesta.get_json() == inexistente.get_json()


def test_sin_sesion_se_pide_iniciar_sesion(cliente):
    """Todas las rutas de organizaciones requieren sesión."""
    assert cliente.get("/api/organizaciones").status_code == 401
    assert cliente.get("/api/invitaciones").status_code == 401


# --- Invitaciones (CA5 a CA13) ---

def test_invitar_a_un_correo_registrado_y_a_uno_no_registrado(aplicacion, correos, ana, beto):
    """CA5: invitación pendiente con vencimiento a 7 días y correo con enlace."""
    id_org = _crear_organizacion(ana)
    correos.clear()
    registrado = _invitar(ana, id_org, "Beto@Ejemplo.com", cargo="Asociado")
    nuevo = _invitar(ana, id_org, "carla@ejemplo.com")
    assert registrado.status_code == nuevo.status_code == 201
    invitacion = registrado.get_json()["invitacion"]
    assert (invitacion["correo"], invitacion["cargo"], invitacion["estado"]) == (
        "beto@ejemplo.com", "Asociado", "pendiente",
    )
    vence = invitacion["vence_en"][:10]
    assert vence == (ahora_utc() + timedelta(days=7)).date().isoformat()
    assert [c.destinatario for c in correos] == ["beto@ejemplo.com", "carla@ejemplo.com"]
    assert "iniciar sesión con este correo" in correos[0].texto
    assert "Todavía no tenés una cuenta" in correos[1].texto
    assert "/invitaciones/responder?token=" in correos[1].texto
    assert _ultima(aplicacion, "invitacion.envio")["detalle"]["correo"] == "carla@ejemplo.com"


def test_limite_del_plan_cuenta_miembros_e_invitaciones(aplicacion, ana):
    """CA6: con 5 lugares, el Referente y 4 invitaciones completan el plan."""
    id_org = _crear_organizacion(ana)
    for numero in range(4):
        assert _invitar(ana, id_org, f"p{numero}@ejemplo.com").status_code == 201
    respuesta = _invitar(ana, id_org, "otra@ejemplo.com")
    assert respuesta.status_code == 409
    assert respuesta.get_json()["codigo"] == "limite_del_plan"
    assert "límite de 5 miembros" in respuesta.get_json()["mensaje"]
    assert _ultima(aplicacion, "invitacion.envio")["detalle"]["motivo"] == "limite_del_plan"


def test_una_invitacion_vencida_no_ocupa_lugar(aplicacion, ana):
    """CA6: las invitaciones vencidas no cuentan para el límite."""
    id_org = _crear_organizacion(ana)
    for numero in range(4):
        _invitar(ana, id_org, f"p{numero}@ejemplo.com")
    with aplicacion.app_context():
        Invitacion.query.filter_by(correo="p0@ejemplo.com").first().vence_en = ahora_utc()
        db.session.commit()
    assert _invitar(ana, id_org, "otra@ejemplo.com").status_code == 201
    # Volver a invitar a un correo con la invitación vencida la renueva.
    assert _invitar(ana, id_org, "p0@ejemplo.com").status_code == 409  # sin lugar
    ana.delete(f"/api/organizaciones/{id_org}/invitaciones/"
               f"{_invitaciones(ana, id_org)[-1]['id']}")
    renovada = _invitar(ana, id_org, "p0@ejemplo.com")
    assert renovada.status_code == 201
    with aplicacion.app_context():
        assert Invitacion.query.filter_by(correo="p0@ejemplo.com").count() == 1


def _invitaciones(cliente, id_org):
    return cliente.get(f"/api/organizaciones/{id_org}/invitaciones").get_json()["invitaciones"]


def test_no_se_invita_a_un_miembro_ni_dos_veces(ana, beto):
    """CA7."""
    id_org = _crear_organizacion(ana)
    _invitar(ana, id_org, "carla@ejemplo.com")
    repetida = _invitar(ana, id_org, "carla@ejemplo.com")
    assert (repetida.status_code, repetida.get_json()["codigo"]) == (409, "ya_invitado")
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    miembro = _invitar(ana, id_org, "beto@ejemplo.com")
    assert (miembro.status_code, miembro.get_json()["codigo"]) == (409, "ya_es_miembro")
    assert _invitar(ana, id_org, "ana@ejemplo.com").get_json()["codigo"] == "ya_es_miembro"


def test_reenviar_y_cancelar(aplicacion, correos, ana):
    """CA8: el reenvío renueva el vencimiento y manda otro correo; cancelar la saca de la lista."""
    id_org = _crear_organizacion(ana)
    id_inv = _invitar(ana, id_org, "carla@ejemplo.com").get_json()["invitacion"]["id"]
    with aplicacion.app_context():
        db.session.get(Invitacion, id_inv).vence_en = ahora_utc() + timedelta(days=1)
        db.session.commit()
    correos.clear()
    respuesta = ana.post(f"/api/organizaciones/{id_org}/invitaciones/{id_inv}/reenvio")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["invitacion"]["vence_en"][:10] == (
        (ahora_utc() + timedelta(days=7)).date().isoformat()
    )
    assert len(correos) == 1
    assert ana.delete(f"/api/organizaciones/{id_org}/invitaciones/{id_inv}").status_code == 200
    assert _invitaciones(ana, id_org) == []
    otra_vez = ana.delete(f"/api/organizaciones/{id_org}/invitaciones/{id_inv}")
    assert otra_vez.status_code == 404
    acciones = [e["accion"] for e in entradas_auditoria(aplicacion) if "invitacion" in e["accion"]]
    assert acciones == ["invitacion.envio", "invitacion.reenvio", "invitacion.cancelacion"]


def test_un_miembro_no_ve_ni_gestiona_invitaciones(ana, beto):
    """CA22."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    assert beto.get(f"/api/organizaciones/{id_org}/invitaciones").status_code == 403
    assert _invitar(beto, id_org, "x@ejemplo.com").status_code == 403


def test_consultar_la_invitacion_sin_sesion(aplicacion, correos, ana):
    """CA9: el enlace muestra la organización y el correo invitado."""
    id_org = _crear_organizacion(ana)
    _invitar(ana, id_org, "carla@ejemplo.com")
    token = extraer_token(correos[-1])
    respuesta = aplicacion.test_client().post("/api/invitaciones/consulta", json={"token": token})
    invitacion = respuesta.get_json()["invitacion"]
    assert respuesta.status_code == 200
    assert invitacion["organizacion"]["nombre"] == "Estudio Pérez"
    assert invitacion["correo"] == "carla@ejemplo.com"
    assert invitacion["invitante"] == "Ana López"
    assert invitacion["vigente"] is True
    assert invitacion["sesion_con_el_correo"] is False


def test_consultar_con_un_enlace_alterado(cliente):
    """CA12."""
    respuesta = cliente.post("/api/invitaciones/consulta", json={"token": "alterado"})
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (400, "enlace_invalido")


def test_aceptar_suma_como_miembro_y_avisa_al_referente(aplicacion, correos, ana, beto):
    """CA10."""
    id_org = _crear_organizacion(ana)
    invitada = _invitar(ana, id_org, "beto@ejemplo.com", cargo="Perito")
    id_inv = invitada.get_json()["invitacion"]["id"]
    token = extraer_token(correos[-1])
    consulta = beto.post("/api/invitaciones/consulta", json={"token": token}).get_json()
    assert consulta["invitacion"]["sesion_con_el_correo"] is True

    correos.clear()
    respuesta = beto.post(f"/api/invitaciones/{id_inv}/aceptacion")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["id_organizacion"] == id_org
    beto_miembro = next(m for m in _miembros(ana, id_org) if m["correo"] == "beto@ejemplo.com")
    assert (beto_miembro["rol"], beto_miembro["cargo"]) == ("miembro", "Perito")
    assert [c.destinatario for c in correos] == ["ana@ejemplo.com"]
    assert "aceptó la invitación" in correos[0].texto
    assert _ultima(aplicacion, "invitacion.aceptacion")["id_usuario"] == beto.id_usuario


def test_rechazar_avisa_al_referente(aplicacion, correos, ana, beto):
    """CA10 (CU11 4a)."""
    id_org = _crear_organizacion(ana)
    id_inv = _invitar(ana, id_org, "beto@ejemplo.com").get_json()["invitacion"]["id"]
    correos.clear()
    assert beto.post(f"/api/invitaciones/{id_inv}/rechazo").status_code == 200
    assert "rechazó la invitación" in correos[0].texto
    assert len(_miembros(ana, id_org)) == 1
    with aplicacion.app_context():
        assert db.session.get(Invitacion, id_inv).estado == "rechazada"


def test_otro_correo_no_puede_responder(aplicacion, ana, beto, cuenta):
    """CA11."""
    id_org = _crear_organizacion(ana)
    id_inv = _invitar(ana, id_org, "beto@ejemplo.com").get_json()["invitacion"]["id"]
    carla = cuenta("carla@ejemplo.com", nombre="Carla")
    respuesta = carla.post(f"/api/invitaciones/{id_inv}/aceptacion")
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (403, "correo_distinto")
    assert "beto@ejemplo.com" not in respuesta.get_json()["mensaje"]
    assert len(_miembros(ana, id_org)) == 1
    assert _ultima(aplicacion, "invitacion.aceptacion")["detalle"]["motivo"] == "correo_distinto"


@pytest.mark.parametrize("caso", ["vencida", "cancelada", "respondida"])
def test_invitacion_no_vigente(aplicacion, correos, ana, beto, caso):
    """CA12: vencida, cancelada o ya respondida."""
    id_org = _crear_organizacion(ana)
    id_inv = _invitar(ana, id_org, "beto@ejemplo.com").get_json()["invitacion"]["id"]
    token = extraer_token(correos[-1])
    if caso == "vencida":
        with aplicacion.app_context():
            db.session.get(Invitacion, id_inv).vence_en = ahora_utc() - timedelta(seconds=1)
            db.session.commit()
    elif caso == "cancelada":
        ana.delete(f"/api/organizaciones/{id_org}/invitaciones/{id_inv}")
    else:
        beto.post(f"/api/invitaciones/{id_inv}/rechazo")
    consulta = beto.post("/api/invitaciones/consulta", json={"token": token}).get_json()
    assert consulta["invitacion"]["vigente"] is False
    respuesta = beto.post(f"/api/invitaciones/{id_inv}/aceptacion")
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "invitacion_no_vigente")


def test_mis_invitaciones_pendientes(aplicacion, ana, cuenta):
    """CA13: tras registrarse con el correo invitado, ve la invitación y la acepta."""
    id_org = _crear_organizacion(ana)
    _invitar(ana, id_org, "carla@ejemplo.com")
    _invitar(ana, _crear_organizacion(ana, nombre="Otra"), "carla@ejemplo.com")
    carla = cuenta("carla@ejemplo.com", nombre="Carla")
    pendientes = carla.get("/api/invitaciones").get_json()["invitaciones"]
    assert [i["organizacion"]["nombre"] for i in pendientes] == ["Estudio Pérez", "Otra"]
    carla.post(f"/api/invitaciones/{pendientes[0]['id']}/aceptacion")
    assert len(carla.get("/api/invitaciones").get_json()["invitaciones"]) == 1
    assert carla.get(f"/api/organizaciones/{id_org}").get_json()["organizacion"]["mi_rol"] == (
        "miembro"
    )


def test_responder_una_invitacion_inexistente(beto):
    """Una invitación que no existe responde 404."""
    assert beto.post("/api/invitaciones/999/aceptacion").status_code == 404


# --- Miembros (CA14 a CA19) ---

def test_listado_de_miembros(ana, beto):
    """CA14: nombre, perfil, cargo, rol y fecha de incorporación; primero el Referente."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com", cargo="Asociado")
    miembros = _miembros(beto, id_org)
    assert [(m["nombre"], m["rol"], m["cargo"]) for m in miembros] == [
        ("Ana", "referente", None), ("Beto", "miembro", "Asociado"),
    ]
    assert miembros[1]["perfil"] == "abogado"
    assert miembros[1]["incorporado_en"]


def test_editar_cargo_sin_tocar_datos_personales(aplicacion, ana, beto):
    """CA15 (RN11)."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    respuesta = ana.patch(
        f"/api/organizaciones/{id_org}/miembros/{beto.id_usuario}",
        json={"cargo": "Socio", "nombre": "Otro"},
    )
    assert respuesta.status_code == 400  # los datos personales no se editan acá
    respuesta = ana.patch(
        f"/api/organizaciones/{id_org}/miembros/{beto.id_usuario}", json={"cargo": "Socio"}
    )
    assert respuesta.get_json()["miembro"]["cargo"] == "Socio"
    assert respuesta.get_json()["miembro"]["nombre"] == "Beto"
    assert _ultima(aplicacion, "membresia.edicion")["detalle"]["cargo"] == {
        "anterior": None, "nuevo": "Socio",
    }
    assert ana.patch(f"/api/organizaciones/{id_org}/miembros/999", json={}).status_code == 404


def test_designar_referente(aplicacion, correos, ana, beto):
    """CA16: intercambio de roles, un solo Referente y aviso a ambos."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    correos.clear()
    respuesta = ana.post(
        f"/api/organizaciones/{id_org}/referente", json={"id_usuario": beto.id_usuario}
    )
    assert respuesta.status_code == 200
    roles = {m["nombre"]: m["rol"] for m in _miembros(ana, id_org)}
    assert roles == {"Ana": "miembro", "Beto": "referente"}
    with aplicacion.app_context():
        assert Membresia.query.filter_by(id_organizacion=id_org, rol="referente").count() == 1
    assert sorted(c.destinatario for c in correos) == ["ana@ejemplo.com", "beto@ejemplo.com"]
    assert ana.patch(f"/api/organizaciones/{id_org}", json={"nombre": "X"}).status_code == 403


def test_designarse_a_si_mismo_se_rechaza(ana):
    """CA16: ya es el Referente."""
    id_org = _crear_organizacion(ana)
    respuesta = ana.post(
        f"/api/organizaciones/{id_org}/referente", json={"id_usuario": ana.id_usuario}
    )
    assert respuesta.status_code == 400


def test_desvincular_un_miembro(aplicacion, correos, ana, beto):
    """CA17: deja de pertenecer de inmediato y recibe un aviso."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    correos.clear()
    respuesta = ana.delete(f"/api/organizaciones/{id_org}/miembros/{beto.id_usuario}")
    assert respuesta.status_code == 200
    assert beto.get(f"/api/organizaciones/{id_org}").status_code == 404
    assert correos[0].destinatario == "beto@ejemplo.com"
    assert "te desvinculó" in correos[0].texto
    entrada = _ultima(aplicacion, "membresia.desvinculacion")
    assert entrada["detalle"]["correo"] == "beto@ejemplo.com"


def test_el_referente_no_puede_desvincularse(ana):
    """CA17."""
    id_org = _crear_organizacion(ana)
    respuesta = ana.delete(f"/api/organizaciones/{id_org}/miembros/{ana.id_usuario}")
    assert respuesta.get_json()["codigo"] == "referente_no_puede_desvincularse"


def test_un_miembro_abandona(aplicacion, correos, ana, beto):
    """CA18: deja de pertenecer y se avisa al Referente."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    correos.clear()
    respuesta = beto.post(f"/api/organizaciones/{id_org}/abandono", json={})
    assert respuesta.get_json()["organizacion_eliminada"] is False
    assert beto.get(f"/api/organizaciones/{id_org}").status_code == 404
    assert correos[0].destinatario == "ana@ejemplo.com"
    assert "abandonó" in correos[0].texto


def test_el_referente_debe_designar_antes_de_abandonar(ana, beto):
    """CA19."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    respuesta = ana.post(f"/api/organizaciones/{id_org}/abandono", json={})
    assert respuesta.status_code == 409
    assert respuesta.get_json()["codigo"] == "debe_designar_referente"


def test_el_unico_miembro_abandona_y_la_organizacion_se_elimina(aplicacion, ana):
    """CA19 (RN08): primero se advierte; con la confirmación, se elimina."""
    id_org = _crear_organizacion(ana)
    advertencia = ana.post(f"/api/organizaciones/{id_org}/abandono", json={})
    assert (advertencia.status_code, advertencia.get_json()["codigo"]) == (
        409, "organizacion_se_eliminara",
    )
    respuesta = ana.post(
        f"/api/organizaciones/{id_org}/abandono", json={"confirmar_eliminacion": True}
    )
    assert respuesta.get_json()["organizacion_eliminada"] is True
    assert ana.get("/api/organizaciones").get_json()["organizaciones"] == []
    assert _ultima(aplicacion, "organizacion.eliminacion")["resultado"] == "exitoso"


# --- Eliminación (CA20) ---

def test_eliminar_con_el_nombre_exacto(aplicacion, correos, ana, beto):
    """CA20: se eliminan membresías e invitaciones y se avisa a los miembros."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    _invitar(ana, id_org, "carla@ejemplo.com")
    incorrecta = ana.delete(f"/api/organizaciones/{id_org}", json={"confirmacion": "estudio pérez"})
    assert incorrecta.status_code == 400
    assert "confirmacion" in incorrecta.get_json()["errores"]

    correos.clear()
    respuesta = ana.delete(
        f"/api/organizaciones/{id_org}", json={"confirmacion": " Estudio Pérez "}
    )
    assert respuesta.status_code == 200
    assert beto.get(f"/api/organizaciones/{id_org}").status_code == 404
    with aplicacion.app_context():
        assert Membresia.query.count() == 0
        assert Invitacion.query.count() == 0
    assert [c.destinatario for c in correos] == ["beto@ejemplo.com"]
    assert "fue eliminada" in correos[0].texto
    eliminaciones = entradas_auditoria(aplicacion, "organizacion.eliminacion")
    resultados = [entrada["resultado"] for entrada in eliminaciones]
    assert resultados == ["rechazado", "exitoso"]


def test_un_miembro_no_puede_eliminar(ana, beto):
    """CA22."""
    id_org = _crear_organizacion(ana)
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    respuesta = beto.delete(f"/api/organizaciones/{id_org}", json={"confirmacion": "Estudio Pérez"})
    assert respuesta.status_code == 403
