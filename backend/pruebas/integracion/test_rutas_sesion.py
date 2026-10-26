"""Pruebas de inicio y cierre de sesión.

Criterios de aceptación de la funcionalidad 002: CA7 a CA12, CA21 y CA22.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
from datetime import timedelta

from app.seguridad.autenticacion import CLAVE_INICIO_SESION
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import CONTRASENIA_VALIDA, datos_registro, modificar_usuario, obtener_usuario

MENSAJE_GENERICO = "El correo o la contraseña no son correctos."


def _iniciar(cliente, correo="ana@ejemplo.com", contrasenia=CONTRASENIA_VALIDA):
    return cliente.post("/api/sesion", json={"correo": correo, "contrasenia": contrasenia})


def test_inicio_de_sesion_valido_devuelve_el_usuario(cliente, registrar_y_verificar):
    """CA7: con credenciales válidas se accede y se obtiene el nombre."""
    registrar_y_verificar()
    respuesta = _iniciar(cliente, correo="  ANA@ejemplo.com ")
    cuerpo = respuesta.get_json()
    assert respuesta.status_code == 200
    assert cuerpo["usuario"]["nombre"] == "Ana"
    assert "hash_contrasenia" not in cuerpo["usuario"]
    assert cuerpo["csrf"]
    assert cliente.get("/api/sesion").get_json()["usuario"]["correo"] == "ana@ejemplo.com"


def test_credenciales_invalidas_dan_mensaje_generico(cliente, registrar_y_verificar):
    """CA8: el mensaje no revela si falló el correo o la contraseña."""
    registrar_y_verificar()
    mala_contrasenia = _iniciar(cliente, contrasenia="Incorrecta123")
    correo_inexistente = _iniciar(cliente, correo="nadie@ejemplo.com")
    assert mala_contrasenia.status_code == correo_inexistente.status_code == 401
    assert mala_contrasenia.get_json() == correo_inexistente.get_json()
    assert mala_contrasenia.get_json()["mensaje"] == MENSAJE_GENERICO


def test_contrasenia_muy_larga_no_produce_error_del_servidor(cliente, registrar_y_verificar):
    """Una contraseña de más de 72 bytes se trata como incorrecta, no como error 500."""
    registrar_y_verificar()
    assert _iniciar(cliente, contrasenia="a1" * 60).status_code == 401
    assert _iniciar(cliente, correo="nadie@ejemplo.com", contrasenia="a1" * 60).status_code == 401


def test_cuenta_no_verificada_no_inicia_sesion(cliente):
    """CA9: se rechaza y el código permite ofrecer el reenvío."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    respuesta = _iniciar(cliente)
    assert respuesta.status_code == 403
    assert respuesta.get_json()["codigo"] == "cuenta_no_verificada"
    assert cliente.get("/api/sesion").status_code == 401


def test_cinco_intentos_fallidos_bloquean_quince_minutos(
    aplicacion, cliente, correos, registrar_y_verificar
):
    """CA10: bloqueo de 15 minutos y aviso por correo al titular."""
    registrar_y_verificar()
    correos.clear()
    for _ in range(5):
        _iniciar(cliente, contrasenia="Incorrecta123")

    usuario = obtener_usuario(aplicacion)
    restante = usuario.bloqueado_hasta - ahora_utc()
    assert timedelta(minutes=14) < restante <= timedelta(minutes=15)
    assert len(correos) == 1 and "15 minutos" in correos[0].texto

    # Bloqueada, ni siquiera la contraseña correcta permite entrar y el mensaje es el mismo.
    bloqueada = _iniciar(cliente)
    assert bloqueada.status_code == 401
    assert bloqueada.get_json()["mensaje"] == MENSAJE_GENERICO

    # Pasado el bloqueo, la contraseña correcta vuelve a funcionar.
    modificar_usuario(aplicacion, {"bloqueado_hasta": ahora_utc() - timedelta(seconds=1)})
    assert _iniciar(cliente).status_code == 200


def test_un_acierto_reinicia_el_contador_de_intentos(aplicacion, cliente, registrar_y_verificar):
    """Los intentos fallidos deben ser consecutivos para bloquear."""
    registrar_y_verificar()
    for _ in range(4):
        _iniciar(cliente, contrasenia="Incorrecta123")
    _iniciar(cliente)
    _iniciar(cliente, contrasenia="Incorrecta123")
    assert obtener_usuario(aplicacion).bloqueado_hasta is None


def test_cerrar_sesion_invalida_la_cookie(cliente, sesion_iniciada):
    """CA11: reutilizar la cookie después de cerrar sesión no funciona."""
    cookie = cliente.get_cookie("sesion").value
    assert cliente.delete("/api/sesion").status_code == 200
    cliente.set_cookie("sesion", cookie)
    assert cliente.get("/api/sesion").status_code == 401


def test_sesion_iniciada_hace_mas_de_ocho_horas_se_cierra(cliente, sesion_iniciada):
    """CA12: la duración máxima se aplica aunque haya actividad."""
    with cliente.session_transaction() as sesion:
        sesion[CLAVE_INICIO_SESION] = (ahora_utc() - timedelta(hours=8, minutes=1)).isoformat()
    assert cliente.get("/api/sesion").status_code == 401


def test_sesion_activa_dentro_del_maximo_sigue_valida(cliente, sesion_iniciada):
    """CA12: antes de las 8 horas la sesión sigue abierta."""
    with cliente.session_transaction() as sesion:
        sesion[CLAVE_INICIO_SESION] = (ahora_utc() - timedelta(hours=7)).isoformat()
    assert cliente.get("/api/sesion").status_code == 200


def test_inactividad_configurada_en_treinta_minutos(aplicacion):
    """CA12: la sesión vence tras 30 minutos sin solicitudes y cada solicitud renueva el plazo."""
    assert aplicacion.config["PERMANENT_SESSION_LIFETIME"] == timedelta(minutes=30)
    assert aplicacion.config["SESSION_REFRESH_EACH_REQUEST"] is True


def test_identificador_de_sesion_cambia_al_iniciar(cliente, registrar_y_verificar):
    """RNF01 CA6: la sesión anterior al inicio no se reutiliza (fijación de sesión)."""
    registrar_y_verificar()
    cliente.get("/api/sesion/csrf")
    anterior = cliente.get_cookie("sesion").value
    _iniciar(cliente)
    assert cliente.get_cookie("sesion").value != anterior


def test_cookie_de_sesion_tiene_atributos_seguros(cliente, registrar_y_verificar):
    """CA21: HttpOnly y SameSite=Lax (cambiado por la 027, ADR-0019)."""
    registrar_y_verificar()
    cabecera = _iniciar(cliente).headers["Set-Cookie"]
    assert "HttpOnly" in cabecera
    assert "SameSite=Lax" in cabecera


def test_sin_sesion_la_api_responde_401(cliente):
    """CA22: las rutas protegidas responden 401 en JSON."""
    for metodo, ruta in [("get", "/api/sesion"), ("delete", "/api/sesion"), ("get", "/api/perfil")]:
        respuesta = getattr(cliente, metodo)(ruta)
        assert respuesta.status_code == 401
        assert respuesta.get_json()["codigo"] == "sesion_requerida"


def test_identificador_de_sesion_alterado_no_autentica(cliente, sesion_iniciada):
    """Un identificador de usuario con formato inválido no abre sesión."""
    with cliente.session_transaction() as sesion:
        sesion["_user_id"] = "no-valido"
    assert cliente.get("/api/sesion").status_code == 401


def test_rutas_inexistentes_y_metodos_no_permitidos_responden_json(cliente):
    """Los errores de la API también se devuelven en JSON."""
    assert cliente.get("/api/no-existe").get_json()["codigo"] == "no_encontrado"
    assert cliente.put("/api/sesion").get_json()["codigo"] == "metodo_no_permitido"
