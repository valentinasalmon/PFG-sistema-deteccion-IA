"""Pruebas del inicio de sesión y del registro con Google (funcionalidad 027).

Google se reemplaza por un *token endpoint* falso: las pruebas recorren el
flujo completo (inicio, vuelta y registro) sin salir a la red.

Criterios: RF52 CA1 a CA3; CA1 a CA9 de la especificación de la 027.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import base64
import json
import time
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest

from app.integraciones.google import ClienteGoogle, ErrorGoogle, crear_cliente_google
from app.servicios import auditoria
from app.servicios.servicio_google import desafio_pkce
from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    ID_SEGUROS_GALICIA,
    contar_usuarios,
    datos_registro,
    entradas_auditoria,
    modificar_usuario,
    obtener_usuario,
)

ID_CLIENTE = "cliente-de-prueba.apps.googleusercontent.com"
SUB = "109876543210"


def token_id(**cambios):
    """Un ID token sin firma con los datos indicados (la firma no se verifica, ADR-0019)."""
    datos = {
        "iss": "https://accounts.google.com", "aud": ID_CLIENTE, "sub": SUB,
        "email": "Ana@Ejemplo.com", "email_verified": True,
        "given_name": "Ana", "family_name": "López", "exp": time.time() + 600,
    }
    datos.update(cambios)
    carga = base64.urlsafe_b64encode(json.dumps(datos).encode()).decode().rstrip("=")
    return f"encabezado.{carga}.firma"


@pytest.fixture
def google(aplicacion, monkeypatch):
    """Configura Google y reemplaza su *token endpoint*.

    Devuelve un diccionario: ``datos`` se mezcla en el ID token que "emite"
    Google, y ``solicitudes`` guarda lo que el backend le envió.
    """
    aplicacion.config["GOOGLE_ID_CLIENTE"] = ID_CLIENTE
    aplicacion.config["GOOGLE_SECRETO_CLIENTE"] = "secreto-de-prueba"
    estado = {"datos": {}, "solicitudes": [], "falla": None}

    def publicar(_cliente, url, datos):
        estado["solicitudes"].append((url, datos))
        if estado["falla"]:
            raise ErrorGoogle(estado["falla"])
        return {"id_token": token_id(**{"nonce": estado["nonce"], **estado["datos"]})}

    monkeypatch.setattr(ClienteGoogle, "_publicar_formulario", publicar)
    return estado


def ir_y_volver(cliente, google, invitacion=None, **parametros):
    """Recorre /inicio y /retorno como lo haría el navegador; devuelve la vuelta."""
    ruta = "/api/google/inicio" + (f"?invitacion={invitacion}" if invitacion else "")
    salida = cliente.get(ruta)
    assert salida.status_code == 302
    consulta = parse_qs(urlparse(salida.headers["Location"]).query)
    google["nonce"] = consulta["nonce"][0]
    google["desafio"] = consulta["code_challenge"][0]
    vuelta = {"state": consulta["state"][0], "code": "codigo-de-google"}
    vuelta.update(parametros)
    return cliente.get("/api/google/retorno", query_string=vuelta)


def destino(respuesta):
    """Ruta y parámetros de la redirección hacia la interfaz."""
    url = urlparse(respuesta.headers["Location"])
    return url.path, parse_qs(url.query)


def completar(cliente, **cambios):
    """Completa el registro pendiente con datos de abogado."""
    datos = {
        "nombre": "Ana", "apellido": "López", "perfil": "abogado",
        "colegio": "CPACF", "acepta_terminos": True,
    }
    datos.update(cambios)
    return cliente.post("/api/google/registro", json=datos)


# --- Disponibilidad ------------------------------------------------------------

def test_sin_configurar_no_esta_disponible(cliente):
    """CA1: sin identificador ni secreto, el botón no se muestra y /inicio vuelve al login."""
    assert cliente.get("/api/google/estado").get_json() == {"habilitado": False}
    respuesta = cliente.get("/api/google/inicio")
    assert destino(respuesta) == ("/iniciar-sesion", {"google": ["no_disponible"]})


def test_configurado_redirige_a_google_con_pkce(cliente, google):
    """CA1: la dirección de Google lleva state, nonce, PKCE S256 y la vuelta a la plataforma."""
    assert cliente.get("/api/google/estado").get_json() == {"habilitado": True}
    salida = urlparse(cliente.get("/api/google/inicio").headers["Location"])
    consulta = parse_qs(salida.query)
    assert salida.netloc == "accounts.google.com"
    assert consulta["client_id"] == [ID_CLIENTE]
    assert consulta["redirect_uri"] == ["http://frontend.prueba/api/google/retorno"]
    assert consulta["code_challenge_method"] == ["S256"]
    assert consulta["scope"] == ["openid email profile"]


# --- Registro nuevo (RF52 CA1) -------------------------------------------------

def test_correo_nuevo_pide_completar_el_registro(aplicacion, cliente, google):
    """CA2: un correo sin cuenta lleva a completar el perfil; todavía no se crea la cuenta."""
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta)[0] == "/registro/google"
    assert contar_usuarios(aplicacion) == 0
    pendiente = cliente.get("/api/google/registro").get_json()
    assert pendiente == {
        "nombre": "Ana", "apellido": "López", "correo": "ana@ejemplo.com", "invitacion": None,
    }
    url, enviado = google["solicitudes"][0]
    assert url.endswith("/token") and enviado["code"] == "codigo-de-google"
    assert desafio_pkce(enviado["code_verifier"]) == google["desafio"]


def test_completar_el_registro_crea_la_cuenta_verificada_e_inicia_sesion(
    aplicacion, cliente, google, correos
):
    """CA3: perfil, institución y Términos obligatorios; sin correo de verificación."""
    ir_y_volver(cliente, google)
    respuesta = completar(cliente)
    assert respuesta.status_code == 201
    assert respuesta.get_json()["usuario"]["perfil"] == "abogado"
    usuario = obtener_usuario(aplicacion)
    assert usuario.verificado and usuario.google_sub == SUB and usuario.colegio == "CPACF"
    assert not correos
    assert cliente.get("/api/sesion").status_code == 200
    registro = entradas_auditoria(aplicacion, auditoria.CUENTA_REGISTRO)[-1]
    assert registro["detalle"]["metodo"] == "google"
    # El registro pendiente se usa una sola vez.
    assert cliente.get("/api/google/registro").status_code == 404


@pytest.mark.parametrize("cambios, campo", [
    ({"acepta_terminos": False}, "acepta_terminos"),
    ({"perfil": "otro"}, "perfil"),
    ({"perfil": "aseguradora"}, "id_aseguradora"),
    ({"correo": "otro@ejemplo.com"}, "correo"),
])
def test_completar_el_registro_valida_los_datos(aplicacion, cliente, google, cambios, campo):
    """CA3: el paso de completar es obligatorio y el correo siempre es el de Google."""
    ir_y_volver(cliente, google)
    respuesta = completar(cliente, **cambios)
    assert respuesta.status_code == 400
    assert campo in respuesta.get_json()["errores"]
    assert contar_usuarios(aplicacion) == 0


def test_registrar_una_aseguradora_con_google(aplicacion, cliente, google):
    """CA3: con Google también se registra una aseguradora del catálogo (RN36)."""
    ir_y_volver(cliente, google)
    respuesta = completar(cliente, perfil="aseguradora", id_aseguradora=ID_SEGUROS_GALICIA)
    assert respuesta.status_code == 201
    assert obtener_usuario(aplicacion).empresa


def test_sin_registro_pendiente_no_se_puede_completar(cliente, google):
    """CA4: no se puede crear una cuenta sin haber pasado por Google."""
    assert cliente.get("/api/google/registro").status_code == 404
    assert completar(cliente).status_code == 404


def test_el_registro_pendiente_vence(aplicacion, cliente, google):
    """CA4: pasado el plazo hay que volver a elegir Google."""
    aplicacion.config["VIGENCIA_REGISTRO_GOOGLE"] = timedelta(seconds=-1)
    ir_y_volver(cliente, google)
    assert completar(cliente).get_json()["codigo"] == "registro_google_vencido"


# --- Cuenta existente (RF52 CA2) ------------------------------------------------

def test_cuenta_vinculada_inicia_sesion_directamente(aplicacion, cliente, google):
    """CA5: la segunda vez entra sin completar nada."""
    ir_y_volver(cliente, google)
    completar(cliente)
    cliente.delete("/api/sesion")
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta)[0] == "/"
    assert cliente.get("/api/sesion").status_code == 200
    inicio = entradas_auditoria(aplicacion, auditoria.SESION_INICIO)[-1]
    assert inicio["resultado"] == "exitoso" and inicio["detalle"]["metodo"] == "google"


def test_correo_existente_se_vincula_y_conserva_la_contrasenia(
    aplicacion, cliente, google, registrar_y_verificar
):
    """CA6: una cuenta verificada con el mismo correo se vincula y la contraseña sigue sirviendo."""
    registrar_y_verificar()
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta)[0] == "/"
    assert obtener_usuario(aplicacion).google_sub == SUB
    assert entradas_auditoria(aplicacion, auditoria.CUENTA_VINCULACION_GOOGLE)
    cliente.delete("/api/sesion")
    credenciales = {"correo": "ana@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA}
    assert cliente.post("/api/sesion", json=credenciales).status_code == 200


def test_cuenta_sin_verificar_se_verifica_y_anula_la_contrasenia(aplicacion, cliente, google):
    """CA6: si alguien registró antes ese correo sin verificarlo, pierde el acceso."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    ir_y_volver(cliente, google)
    usuario = obtener_usuario(aplicacion)
    assert usuario.verificado and usuario.google_sub == SUB
    cliente.delete("/api/sesion")
    credenciales = {"correo": "ana@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA}
    assert cliente.post("/api/sesion", json=credenciales).status_code == 401


def test_correo_no_verificado_en_google_no_se_vincula(
    aplicacion, cliente, google, registrar_y_verificar
):
    """CA6: sin correo verificado por Google, no se vincula ni se inicia sesión."""
    registrar_y_verificar()
    google["datos"] = {"email_verified": False}
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta) == ("/iniciar-sesion", {"google": ["google_no_verificado"]})
    assert obtener_usuario(aplicacion).google_sub is None
    assert cliente.get("/api/sesion").status_code == 401


def test_cuenta_desactivada_no_ingresa(aplicacion, cliente, google, registrar_y_verificar):
    """CA7: la cuenta desactivada (RN39) tampoco entra con Google."""
    registrar_y_verificar()
    modificar_usuario(aplicacion, {"activo": False})
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta) == ("/iniciar-sesion", {"google": ["cuenta_desactivada"]})
    assert cliente.get("/api/sesion").status_code == 401


def test_administrador_por_configuracion(aplicacion, cliente, google, registrar_y_verificar):
    """CA5: la promoción a Administrador también se aplica al entrar con Google."""
    registrar_y_verificar()
    aplicacion.config["ADMINISTRADORES"] = frozenset({"ana@ejemplo.com"})
    ir_y_volver(cliente, google)
    assert obtener_usuario(aplicacion).rol == "administrador"


# --- Rechazos (RF52 CA3) ---------------------------------------------------------

def test_state_distinto_se_rechaza(aplicacion, cliente, google):
    """CA8: un state que no es el de la sesión se rechaza y queda en la auditoría."""
    respuesta = ir_y_volver(cliente, google, state="otro")
    assert destino(respuesta) == ("/iniciar-sesion", {"google": ["google_error"]})
    fallo = entradas_auditoria(aplicacion, auditoria.SESION_INICIO)[-1]
    assert fallo["resultado"] == "fallido" and fallo["detalle"]["motivo"] == "state_invalido"


def test_vuelta_sin_inicio_se_rechaza(cliente, google):
    """CA8: llegar a /retorno sin haber pasado por /inicio no inicia sesión."""
    respuesta = cliente.get("/api/google/retorno?state=x&code=y")
    assert destino(respuesta)[1] == {"google": ["google_error"]}


def test_cancelar_en_google(aplicacion, cliente, google):
    """CA8: si la persona cancela en Google, vuelve al login con un aviso."""
    respuesta = ir_y_volver(cliente, google, error="access_denied")
    assert destino(respuesta)[1] == {"google": ["google_cancelado"]}


def test_google_rechaza_el_codigo(aplicacion, cliente, google):
    """CA8: un código rechazado por Google no inicia sesión."""
    google["falla"] = "400"
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta)[1] == {"google": ["google_error"]}
    fallo = entradas_auditoria(aplicacion, auditoria.SESION_INICIO)[-1]
    assert fallo["detalle"]["motivo"] == "token_invalido"


@pytest.mark.parametrize("datos", [
    {"aud": "otra-aplicacion"},
    {"iss": "https://otro.example"},
    {"exp": time.time() - 3600},
    {"nonce": "otro"},
])
def test_id_token_invalido_se_rechaza(cliente, google, datos):
    """CA8: audiencia, emisor, vencimiento y nonce se validan."""
    google["datos"] = datos
    respuesta = ir_y_volver(cliente, google)
    assert destino(respuesta)[1] == {"google": ["google_error"]}


# --- Cliente de Google -----------------------------------------------------------

def test_cliente_sin_secreto_no_se_crea():
    """Sin identificador o secreto, el cliente no existe y el botón no se muestra."""
    assert crear_cliente_google({"GOOGLE_ID_CLIENTE": "x", "URL_FRONTEND": "h"}) is None


@pytest.mark.parametrize("token", ["sin-puntos", "a.no-es-base64!.c", "a.WzFd.c"])
def test_token_mal_formado(token):
    """Un ID token que no es un JWT con un objeto JSON se rechaza."""
    cliente = ClienteGoogle(ID_CLIENTE, "s", "http://h")
    with pytest.raises(ErrorGoogle):
        cliente.identidad_del_token(token, "n")


def test_respuesta_sin_id_token(monkeypatch):
    """Si Google no devuelve el ID token, es un error."""
    cliente = ClienteGoogle(ID_CLIENTE, "s", "http://h")
    monkeypatch.setattr(ClienteGoogle, "_publicar_formulario", lambda *_: {})
    with pytest.raises(ErrorGoogle):
        cliente.canjear_codigo("c", "v", "n")


def test_publicar_formulario_traduce_los_errores_de_red(monkeypatch):
    """Los errores de red y HTTP se informan como ErrorGoogle."""
    from urllib import error  # pylint: disable=import-outside-toplevel

    def fallar(*_args, **_kwargs):
        raise error.URLError("sin red")

    monkeypatch.setattr("app.integraciones.google.request.urlopen", fallar)
    cliente = ClienteGoogle(ID_CLIENTE, "s", "http://h")
    with pytest.raises(ErrorGoogle):
        cliente.canjear_codigo("c", "v", "n")
