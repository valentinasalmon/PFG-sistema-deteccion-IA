"""Pruebas de las organizaciones de aseguradoras a través de la API.

Criterios de aceptación de la funcionalidad 021: CA2 a CA19 (CA1 es de la
interfaz). Reglas RN35 a RN39.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
# Las pruebas de varias personas reciben muchos accesorios.
# pylint: disable=too-many-arguments,too-many-positional-arguments
import pytest

from app.extensiones import db
from app.modelos.organizacion import Organizacion
from app.modelos.usuario import Usuario
from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    ID_EL_SURCO,
    ID_SEGUROS_GALICIA,
    datos_registro,
    entradas_auditoria,
    extraer_token,
    obtener_usuario,
)

GALICIA = "SEGUROS GALICIA S.A."


def _ultimo_correo(correos, destinatario):
    return next(c for c in reversed(correos) if c.destinatario == destinatario)


@pytest.fixture
def nuevo_cliente(aplicacion):
    """Fábrica de clientes HTTP independientes (una persona por cliente)."""
    return aplicacion.test_client


def _verificar(cliente, correos, correo):
    token = extraer_token(_ultimo_correo(correos, correo))
    return cliente.post("/api/cuentas/verificacion", json={"token": token})


def _iniciar(cliente, correo):
    return cliente.post("/api/sesion", json={"correo": correo, "contrasenia": CONTRASENIA_VALIDA})


def _registrar_aseguradora(
    cliente, correos, correo="rita@galicia.com", id_aseguradora=ID_SEGUROS_GALICIA
):
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(
        correo=correo, nombre="Rita", perfil="aseguradora", colegio=None,
        id_aseguradora=id_aseguradora,
    ))
    assert respuesta.status_code == 201, respuesta.get_json()
    _verificar(cliente, correos, correo)
    assert _iniciar(cliente, correo).status_code == 200
    return cliente


@pytest.fixture
def administrador(aplicacion, nuevo_cliente, correos):
    """Cliente con la sesión de un Administrador, promovido desde la terminal."""
    cliente = nuevo_cliente()
    cliente.post("/api/cuentas/registro", json=datos_registro(correo="admin@plataforma.com"))
    _verificar(cliente, correos, "admin@plataforma.com")
    resultado = aplicacion.test_cli_runner().invoke(
        args=["administracion", "promover", "admin@plataforma.com"]
    )
    assert "es Administrador" in resultado.output
    _iniciar(cliente, "admin@plataforma.com")
    return cliente


@pytest.fixture
def rita(nuevo_cliente, correos):
    """Referente de Seguros Galicia, con la aseguradora todavía pendiente."""
    return _registrar_aseguradora(nuevo_cliente(), correos)


def _organizacion_de(cliente):
    return cliente.get("/api/organizaciones").get_json()["organizaciones"][0]


def _aprobar(administrador, cliente_referente):
    id_org = _organizacion_de(cliente_referente)["id"]
    ruta = f"/api/administracion/organizaciones/{id_org}/aprobacion"
    assert administrador.post(ruta).status_code == 200
    return id_org


# --- Catálogo y registro (CA2 a CA5) ---

def test_el_catalogo_tiene_las_aseguradoras_sin_reaseguradoras(cliente):
    """CA2: 192 aseguradoras ordenadas, sin sesión."""
    aseguradoras = cliente.get("/api/catalogos/aseguradoras").get_json()["aseguradoras"]
    assert len(aseguradoras) == 192
    galicia = next(a for a in aseguradoras if a["id"] == ID_SEGUROS_GALICIA)
    assert galicia == {
        "id": 25, "denominacion": GALICIA, "cuit": "30500000127", "actividad": "Seguros Generales",
    }
    assert not [a for a in aseguradoras if a["actividad"].startswith("Reaseg")]
    nombres = [a["denominacion"] for a in aseguradoras]
    assert nombres == sorted(nombres, key=str.upper)


def test_registrar_una_aseguradora_crea_la_organizacion_pendiente(aplicacion, rita):
    """CA3: cuenta Aseguradora y organización con denominación y CUIT del catálogo."""
    organizacion = _organizacion_de(rita)
    assert organizacion["nombre"] == GALICIA
    assert organizacion["tipo"] == "aseguradora"
    assert organizacion["cuit"] == "30500000127"
    assert organizacion["estado"] == "pendiente"
    assert organizacion["mi_rol"] == "referente"
    usuario = obtener_usuario(aplicacion, "rita@galicia.com")
    assert (usuario.perfil, usuario.empresa, usuario.activo) == ("aseguradora", GALICIA, True)
    creacion = entradas_auditoria(aplicacion, "organizacion.creacion")[-1]
    assert creacion["detalle"]["origen"] == "registro"


def test_una_aseguradora_ya_registrada_se_rechaza(aplicacion, rita, nuevo_cliente):
    """CA4 (RN36): se indica pedir una invitación y no se crea la cuenta."""
    respuesta = nuevo_cliente().post("/api/cuentas/registro", json=datos_registro(
        correo="otra@galicia.com", perfil="aseguradora", colegio=None,
        id_aseguradora=ID_SEGUROS_GALICIA,
    ))
    cuerpo = respuesta.get_json()
    assert (respuesta.status_code, cuerpo["codigo"]) == (409, "aseguradora_registrada")
    assert "Pedile a su Referente que te invite" in cuerpo["errores"]["id_aseguradora"]
    assert obtener_usuario(aplicacion, "otra@galicia.com") is None


@pytest.mark.parametrize("id_aseguradora", [None, 999999])
def test_aseguradora_sin_catalogo_ni_invitacion_se_rechaza(aplicacion, cliente, id_aseguradora):
    """CA5 (RN35)."""
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(
        perfil="aseguradora", colegio=None, empresa="Inventada SA", id_aseguradora=id_aseguradora,
    ))
    assert respuesta.status_code == 400
    assert "id_aseguradora" in respuesta.get_json()["errores"]
    assert obtener_usuario(aplicacion) is None


def test_un_correo_existente_no_crea_otra_aseguradora(
    aplicacion, cliente, correos, registrar_y_verificar
):
    """El registro con un correo ya usado no revela nada y no crea la organización."""
    registrar_y_verificar()
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(
        perfil="aseguradora", colegio=None, id_aseguradora=ID_EL_SURCO,
    ))
    assert respuesta.status_code == 201
    with aplicacion.app_context():
        assert Organizacion.query.count() == 0


# --- Aprobación (CA6 a CA9) ---

def test_pendiente_no_puede_invitar(rita):
    """CA6 (RN37)."""
    id_org = _organizacion_de(rita)["id"]
    respuesta = rita.post(
        f"/api/organizaciones/{id_org}/invitaciones", json={"correo": "x@galicia.com"}
    )
    assert respuesta.status_code == 409
    assert respuesta.get_json()["codigo"] == "organizacion_pendiente"


def test_el_administrador_ve_las_pendientes(administrador, rita):
    """CA7: denominación, CUIT, Referente y fecha."""
    pendientes = administrador.get("/api/administracion/aseguradoras-pendientes").get_json()
    assert len(pendientes["aseguradoras"]) == 1
    pendiente = pendientes["aseguradoras"][0]
    assert (pendiente["nombre"], pendiente["cuit"]) == (GALICIA, "30500000127")
    assert pendiente["referente"] == {
        "nombre": "Rita López", "correo": "rita@galicia.com", "verificado": True,
    }
    assert pendiente["creada_en"]


def test_quien_no_es_administrador_no_ve_las_pendientes(rita):
    """CA7."""
    respuesta = rita.get("/api/administracion/aseguradoras-pendientes")
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (403, "acceso_denegado")
    assert rita.post("/api/administracion/organizaciones/1/aprobacion").status_code == 403


def test_aprobar_activa_y_avisa(aplicacion, correos, administrador, rita):
    """CA8."""
    id_org = _aprobar(administrador, rita)
    assert _organizacion_de(rita)["estado"] == "activa"
    aviso = _ultimo_correo(correos, "rita@galicia.com")
    assert "aprobó el registro" in aviso.texto
    invitar = rita.post(
        f"/api/organizaciones/{id_org}/invitaciones", json={"correo": "x@galicia.com"}
    )
    assert invitar.status_code == 201
    assert entradas_auditoria(aplicacion, "organizacion.aprobacion")[-1]["resultado"] == "exitoso"
    otra_vez = administrador.post(f"/api/administracion/organizaciones/{id_org}/aprobacion")
    assert otra_vez.status_code == 404


def test_rechazar_elimina_y_desactiva(aplicacion, correos, administrador, rita):
    """CA9: la organización se elimina, el Referente se desactiva y se le avisa el motivo."""
    id_org = _organizacion_de(rita)["id"]
    respuesta = administrador.post(
        f"/api/administracion/organizaciones/{id_org}/rechazo",
        json={"motivo": "No pudimos confirmar que trabajes en la empresa."},
    )
    assert respuesta.status_code == 200
    with aplicacion.app_context():
        assert db.session.get(Organizacion, id_org) is None
    assert obtener_usuario(aplicacion, "rita@galicia.com").activo is False
    aviso = _ultimo_correo(correos, "rita@galicia.com")
    assert "No pudimos confirmar" in aviso.texto
    assert rita.get("/api/sesion").status_code == 401  # sus sesiones se cerraron
    assert administrador.post(
        f"/api/administracion/organizaciones/{id_org}/rechazo", json={"motivo": "x"}
    ).status_code == 404


def test_rechazar_exige_motivo(administrador, rita):
    """CA9."""
    id_org = _organizacion_de(rita)["id"]
    respuesta = administrador.post(f"/api/administracion/organizaciones/{id_org}/rechazo", json={})
    assert respuesta.status_code == 400


def test_promover_un_correo_inexistente_falla(aplicacion):
    """El comando de terminal informa si no hay una cuenta verificada."""
    resultado = aplicacion.test_cli_runner().invoke(args=["administracion", "promover", "x@y.com"])
    assert resultado.exit_code != 0
    assert "No hay una cuenta verificada" in resultado.output


# --- Empleados (CA10 a CA12) ---

@pytest.fixture
def galicia_activa(administrador, rita):
    """Seguros Galicia aprobada; devuelve su identificador."""
    return _aprobar(administrador, rita)


def _invitar(rita, id_org, correo, cargo=None):
    respuesta = rita.post(
        f"/api/organizaciones/{id_org}/invitaciones", json={"correo": correo, "cargo": cargo}
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()["invitacion"]["id"]


def _registrar_con_invitacion(cliente, correos, invitado, **cambios):
    token = extraer_token(_ultimo_correo(correos, invitado))
    datos = datos_registro(
        correo=invitado, nombre="Eva", perfil="abogado", colegio="CPACF", token_invitacion=token,
    )
    datos.update(cambios)
    return cliente.post("/api/cuentas/registro", json=datos)


def test_empleado_se_registra_con_la_invitacion_y_queda_incorporado(
    aplicacion, correos, nuevo_cliente, rita, galicia_activa
):
    """CA10 y CA11: perfil y empresa fijados por la invitación; al verificar, queda adentro."""
    _invitar(rita, galicia_activa, "eva@galicia.com", cargo="Liquidadora")
    eva = nuevo_cliente()
    assert _registrar_con_invitacion(eva, correos, "eva@galicia.com").status_code == 201
    usuario = obtener_usuario(aplicacion, "eva@galicia.com")
    assert (usuario.perfil, usuario.empresa, usuario.colegio) == ("aseguradora", GALICIA, None)

    _verificar(eva, correos, "eva@galicia.com")
    _iniciar(eva, "eva@galicia.com")
    organizaciones = eva.get("/api/organizaciones").get_json()["organizaciones"]
    assert [(o["nombre"], o["mi_rol"]) for o in organizaciones] == [(GALICIA, "miembro")]
    miembros = rita.get(f"/api/organizaciones/{galicia_activa}/miembros").get_json()["miembros"]
    assert {m["correo"]: m["cargo"] for m in miembros}["eva@galicia.com"] == "Liquidadora"
    assert "aceptó la invitación" in _ultimo_correo(correos, "rita@galicia.com").texto


def test_registro_con_invitacion_y_otro_correo_se_rechaza(
    correos, nuevo_cliente, rita, galicia_activa
):
    """CA12."""
    _invitar(rita, galicia_activa, "eva@galicia.com")
    respuesta = _registrar_con_invitacion(
        nuevo_cliente(), correos, "eva@galicia.com", correo="intrusa@ejemplo.com"
    )
    assert respuesta.status_code == 400
    assert "eva@galicia.com" in respuesta.get_json()["errores"]["correo"]


def test_registro_con_una_invitacion_cancelada_se_rechaza(
    correos, nuevo_cliente, rita, galicia_activa
):
    """Una invitación que ya no está vigente no sirve para registrarse."""
    id_inv = _invitar(rita, galicia_activa, "eva@galicia.com")
    rita.delete(f"/api/organizaciones/{galicia_activa}/invitaciones/{id_inv}")
    respuesta = _registrar_con_invitacion(nuevo_cliente(), correos, "eva@galicia.com")
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "invitacion_no_vigente")


def test_invitacion_de_un_estudio_no_fija_el_perfil(
    aplicacion, correos, nuevo_cliente, registrar_y_verificar, cliente
):
    """La invitación de un estudio jurídico solo precarga el correo: el perfil se elige."""
    registrar_y_verificar()
    _iniciar(cliente, "ana@ejemplo.com")
    id_org = cliente.post(
        "/api/organizaciones", json={"nombre": "Estudio", "tipo": "estudio_juridico"}
    ).get_json()["organizacion"]["id"]
    cliente.post(f"/api/organizaciones/{id_org}/invitaciones", json={"correo": "eva@ejemplo.com"})
    assert _registrar_con_invitacion(nuevo_cliente(), correos, "eva@ejemplo.com").status_code == 201
    assert obtener_usuario(aplicacion, "eva@ejemplo.com").perfil == "abogado"


# --- Cuentas desactivadas (CA13 a CA16) ---

@pytest.fixture
def eva(correos, nuevo_cliente, rita, galicia_activa):
    """Empleada de Seguros Galicia con la sesión iniciada."""
    _invitar(rita, galicia_activa, "eva@galicia.com")
    cliente = nuevo_cliente()
    _registrar_con_invitacion(cliente, correos, "eva@galicia.com")
    _verificar(cliente, correos, "eva@galicia.com")
    _iniciar(cliente, "eva@galicia.com")
    return cliente


def test_al_desvincular_la_cuenta_se_desactiva(aplicacion, correos, rita, eva, galicia_activa):
    """CA13: se desactiva, se cierran sus sesiones y el aviso lo dice."""
    id_eva = obtener_usuario(aplicacion, "eva@galicia.com").id
    assert rita.delete(f"/api/organizaciones/{galicia_activa}/miembros/{id_eva}").status_code == 200
    assert obtener_usuario(aplicacion, "eva@galicia.com").activo is False
    assert eva.get("/api/sesion").status_code == 401
    assert "tu cuenta quedó desactivada" in _ultimo_correo(correos, "eva@galicia.com").texto
    entrada = entradas_auditoria(aplicacion, "cuenta.desactivacion")[-1]
    assert entrada["id_recurso"] == str(id_eva)


def test_al_abandonar_la_cuenta_se_desactiva_y_la_sesion_se_cierra(aplicacion, eva, galicia_activa):
    """CA13."""
    respuesta = eva.post(f"/api/organizaciones/{galicia_activa}/abandono", json={})
    cuerpo = respuesta.get_json()
    assert cuerpo["cuenta_desactivada"] is True
    assert "Tu cuenta quedó desactivada" in cuerpo["mensaje"]
    assert eva.get("/api/sesion").status_code == 401
    cierre = entradas_auditoria(aplicacion, "sesion.cierre")[-1]
    assert cierre["detalle"] == {"motivo": "cuenta_desactivada"}


def test_al_eliminar_la_organizacion_se_desactivan_todos(
    aplicacion, correos, rita, eva, galicia_activa
):
    """CA13: el Referente y los empleados quedan desactivados."""
    respuesta = rita.delete(f"/api/organizaciones/{galicia_activa}", json={"confirmacion": GALICIA})
    assert respuesta.get_json()["cuenta_desactivada"] is True
    assert obtener_usuario(aplicacion, "rita@galicia.com").activo is False
    assert obtener_usuario(aplicacion, "eva@galicia.com").activo is False
    assert "tu cuenta quedó desactivada" in _ultimo_correo(correos, "eva@galicia.com").texto
    assert rita.get("/api/sesion").status_code == 401


def test_cuenta_desactivada_no_inicia_sesion(aplicacion, nuevo_cliente, rita, eva, galicia_activa):
    """CA14: con la contraseña correcta se informa; con una incorrecta, mensaje genérico."""
    eva.post(f"/api/organizaciones/{galicia_activa}/abandono", json={})
    otro = nuevo_cliente()
    correcta = _iniciar(otro, "eva@galicia.com")
    assert (correcta.status_code, correcta.get_json()["codigo"]) == (403, "cuenta_desactivada")
    incorrecta = otro.post(
        "/api/sesion", json={"correo": "eva@galicia.com", "contrasenia": "Incorrecta123"}
    )
    assert incorrecta.status_code == 401
    assert incorrecta.get_json()["codigo"] == "credenciales_invalidas"
    assert otro.get("/api/sesion").status_code == 401


def test_cuenta_desactivada_con_invitacion_entra_y_se_reactiva(
    aplicacion, correos, nuevo_cliente, administrador, eva, galicia_activa
):
    """CA15: otra aseguradora la invita; puede entrar, acepta y se reactiva."""
    eva.post(f"/api/organizaciones/{galicia_activa}/abandono", json={})
    surco = _registrar_aseguradora(nuevo_cliente(), correos, "sol@surco.com", ID_EL_SURCO)
    id_surco = _aprobar(administrador, surco)
    id_inv = _invitar(surco, id_surco, "eva@galicia.com")

    otro = nuevo_cliente()
    respuesta = _iniciar(otro, "eva@galicia.com")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["usuario"]["activo"] is False
    assert otro.post(f"/api/invitaciones/{id_inv}/aceptacion").status_code == 200
    assert obtener_usuario(aplicacion, "eva@galicia.com").activo is True
    assert entradas_auditoria(aplicacion, "cuenta.reactivacion")[-1]["resultado"] == "exitoso"


def test_un_abogado_que_deja_una_aseguradora_no_se_desactiva(
    aplicacion, cliente, registrar_y_verificar, rita, galicia_activa
):
    """CA16: conserva su espacio personal."""
    registrar_y_verificar()
    _iniciar(cliente, "ana@ejemplo.com")
    id_inv = _invitar(rita, galicia_activa, "ana@ejemplo.com")
    cliente.post(f"/api/invitaciones/{id_inv}/aceptacion")
    respuesta = cliente.post(f"/api/organizaciones/{galicia_activa}/abandono", json={})
    assert respuesta.get_json()["cuenta_desactivada"] is False
    assert obtener_usuario(aplicacion).activo is True
    assert cliente.get("/api/sesion").status_code == 200


def test_una_empleada_en_dos_aseguradoras_sigue_activa_al_dejar_una(
    aplicacion, correos, nuevo_cliente, administrador, eva, galicia_activa
):
    """RN38: solo se desactiva al quedarse sin ninguna aseguradora."""
    surco = _registrar_aseguradora(nuevo_cliente(), correos, "sol@surco.com", ID_EL_SURCO)
    id_surco = _aprobar(administrador, surco)
    id_inv = _invitar(surco, id_surco, "eva@galicia.com")
    eva.post(f"/api/invitaciones/{id_inv}/aceptacion")
    respuesta = eva.post(f"/api/organizaciones/{galicia_activa}/abandono", json={})
    assert respuesta.get_json()["cuenta_desactivada"] is False
    assert obtener_usuario(aplicacion, "eva@galicia.com").activo is True


# --- Creación y edición de organizaciones (CA17, CA18) ---

def test_una_aseguradora_no_crea_organizaciones(rita):
    """CA17 (RN39)."""
    respuesta = rita.post("/api/organizaciones", json={"nombre": "X", "tipo": "estudio_juridico"})
    assert respuesta.status_code == 403


def test_un_abogado_solo_crea_estudios(cliente, registrar_y_verificar):
    """CA17 (RN39)."""
    registrar_y_verificar()
    _iniciar(cliente, "ana@ejemplo.com")
    respuesta = cliente.post("/api/organizaciones", json={"nombre": "X", "tipo": "aseguradora"})
    assert respuesta.status_code == 400
    assert "tipo" in respuesta.get_json()["errores"]


def test_la_aseguradora_edita_el_contacto_pero_no_el_nombre_ni_el_tipo(rita, galicia_activa):
    """CA18."""
    ruta = f"/api/organizaciones/{galicia_activa}"
    assert rita.patch(ruta, json={"nombre": "Otra"}).status_code == 400
    assert rita.patch(ruta, json={"tipo": "estudio_juridico"}).status_code == 400
    respuesta = rita.patch(ruta, json={"telefono": "0800-888", "nombre": GALICIA})
    assert respuesta.status_code == 200
    assert respuesta.get_json()["organizacion"]["telefono"] == "0800-888"


# --- Auditoría (CA19) ---

def test_auditoria_de_aseguradoras(aplicacion, administrador, rita, eva, galicia_activa):
    """CA19: aprobación, desactivación, promoción y alta quedan registradas."""
    eva.post(f"/api/organizaciones/{galicia_activa}/abandono", json={})
    acciones = {e["accion"] for e in entradas_auditoria(aplicacion)}
    assert {
        "organizacion.creacion", "organizacion.aprobacion", "cuenta.desactivacion",
        "cuenta.promocion_administrador", "invitacion.aceptacion",
    } <= acciones
    with aplicacion.app_context():
        administradores = Usuario.query.filter_by(rol="administrador").count()
    assert administradores == 1
