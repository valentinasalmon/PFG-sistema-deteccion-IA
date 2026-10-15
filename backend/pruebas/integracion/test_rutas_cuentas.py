"""Pruebas de registro, verificación y recuperación de contraseña.

Criterios de aceptación de la funcionalidad 002: CA1 a CA6 y CA13 a CA15.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
from datetime import timedelta

from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    contar_usuarios,
    datos_registro,
    extraer_token,
    modificar_usuario,
    obtener_usuario,
)

NUEVA = "OtraClave2026"


def _iniciar(cliente, correo="ana@ejemplo.com", contrasenia=CONTRASENIA_VALIDA):
    return cliente.post("/api/sesion", json={"correo": correo, "contrasenia": contrasenia})


# --- Registro (RF01) ---------------------------------------------------------

def test_registro_valido_queda_pendiente_y_envia_verificacion(aplicacion, cliente, correos):
    """CA1: la cuenta queda sin verificar y llega el correo de verificación."""
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro())
    assert respuesta.status_code == 201
    usuario = obtener_usuario(aplicacion)
    assert usuario is not None and not usuario.verificado
    assert len(correos) == 1
    assert correos[0].destinatario == "ana@ejemplo.com"
    assert "/verificar-correo?token=" in correos[0].texto


def test_registro_sin_aceptar_terminos_se_rechaza(aplicacion, cliente, correos):
    """CA2: la aceptación de los términos es obligatoria."""
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(acepta_terminos=False))
    assert respuesta.status_code == 400
    assert "aceptar" in respuesta.get_json()["errores"]["acepta_terminos"]
    assert obtener_usuario(aplicacion) is None and not correos


def test_registro_con_correo_existente_responde_igual_y_avisa(
    aplicacion, cliente, correos, registrar_y_verificar
):
    """CA3: misma respuesta que un registro nuevo y aviso al titular."""
    registrar_y_verificar()
    correos.clear()
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(nombre="Otra"))
    assert respuesta.status_code == 201
    assert contar_usuarios(aplicacion) == 1
    assert len(correos) == 1 and correos[0].asunto == "Intento de registro con tu correo"


def test_registro_con_correo_no_verificado_reenvia_verificacion(cliente, correos):
    """CA3: si la cuenta existente no está verificada, se reenvía la verificación."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(correo="ANA@ejemplo.com"))
    assert respuesta.status_code == 201
    assert len(correos) == 2 and "token=" in correos[1].texto


def test_registro_con_contrasenia_debil_indica_la_condicion(cliente):
    """CA4: la política de contraseñas se aplica e informa el motivo."""
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(contrasenia="corta1"))
    assert respuesta.status_code == 400
    assert "10 caracteres" in respuesta.get_json()["errores"]["contrasenia"]


def test_registro_con_datos_invalidos_se_rechaza(cliente):
    """RNF04 CA1: correo con formato inválido y perfil inexistente."""
    respuesta = cliente.post(
        "/api/cuentas/registro", json=datos_registro(correo="no-es-correo", perfil="otro")
    )
    errores = respuesta.get_json()["errores"]
    assert respuesta.status_code == 400
    assert set(errores) == {"correo", "perfil"}


def test_registro_sin_cuerpo_se_rechaza(cliente):
    """Una solicitud sin JSON informa los campos obligatorios."""
    respuesta = cliente.post("/api/cuentas/registro", data="texto")
    assert respuesta.status_code == 400
    assert respuesta.get_json()["errores"]["nombre"] == "Este campo es obligatorio."


def test_registro_guarda_version_y_fecha_de_los_terminos(cliente, aplicacion):
    """CA5: consentimiento con versión y fecha (Ley 25.326)."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    usuario = obtener_usuario(aplicacion)
    assert usuario.version_terminos == aplicacion.config["VERSION_TERMINOS"]
    assert usuario.aceptacion_terminos_en is not None


def test_registro_guarda_solo_el_dato_del_perfil(aplicacion, cliente):
    """RN02: un abogado guarda colegio y no empresa."""
    cliente.post("/api/cuentas/registro", json=datos_registro(empresa="Seguros SA"))
    usuario = obtener_usuario(aplicacion)
    assert usuario.colegio == "CPACF" and usuario.empresa is None


# --- Verificación (RF02) -----------------------------------------------------

def test_enlace_de_verificacion_activa_la_cuenta(aplicacion, cliente, correos):
    """CA6: el enlace vigente activa la cuenta."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    respuesta = cliente.post(
        "/api/cuentas/verificacion", json={"token": extraer_token(correos[0])}
    )
    assert respuesta.status_code == 200
    assert obtener_usuario(aplicacion).verificado


def test_enlace_de_verificacion_usado_se_rechaza(cliente, correos):
    """CA6: un enlace ya usado informa el motivo."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    token = extraer_token(correos[0])
    cliente.post("/api/cuentas/verificacion", json={"token": token})
    respuesta = cliente.post("/api/cuentas/verificacion", json={"token": token})
    assert respuesta.status_code == 400
    assert respuesta.get_json()["codigo"] == "enlace_invalido"
    assert "ya fue utilizado" in respuesta.get_json()["mensaje"]


def test_enlace_de_verificacion_vencido_se_rechaza(cliente, correos, aplicacion):
    """CA6: un enlace de más de 24 horas informa que venció."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    aplicacion.config["VIGENCIA_TOKEN_VERIFICACION"] = timedelta(seconds=-1)
    respuesta = cliente.post(
        "/api/cuentas/verificacion", json={"token": extraer_token(correos[0])}
    )
    assert respuesta.status_code == 400
    assert "venció" in respuesta.get_json()["mensaje"]
    assert not obtener_usuario(aplicacion).verificado


def test_enlace_de_verificacion_de_cuenta_inexistente_se_rechaza(aplicacion, cliente, correos):
    """Un enlace de una cuenta cuyo correo cambió ya no sirve."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    token = extraer_token(correos[0])
    modificar_usuario(aplicacion, {"correo": "otra@ejemplo.com"})
    respuesta = cliente.post("/api/cuentas/verificacion", json={"token": token})
    assert respuesta.status_code == 400


def test_reenvio_de_verificacion(cliente, correos):
    """CA6 y CA9: se puede pedir otro enlace; no revela si la cuenta existe."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    ruta = "/api/cuentas/verificacion/reenvio"
    existente = cliente.post(ruta, json={"correo": "ana@ejemplo.com"})
    inexistente = cliente.post(ruta, json={"correo": "x@ejemplo.com"})
    assert existente.get_json() == inexistente.get_json()
    assert len(correos) == 2


# --- Recuperación (RF05) -----------------------------------------------------

def test_recuperacion_envia_enlace_solo_a_correos_registrados(
    cliente, correos, registrar_y_verificar
):
    """CA13: mismo mensaje en ambos casos; solo se envía si el correo existe."""
    registrar_y_verificar()
    correos.clear()
    existente = cliente.post("/api/cuentas/recuperacion", json={"correo": "ana@ejemplo.com"})
    inexistente = cliente.post("/api/cuentas/recuperacion", json={"correo": "nadie@ejemplo.com"})
    assert existente.status_code == inexistente.status_code == 200
    assert existente.get_json() == inexistente.get_json()
    assert len(correos) == 1
    assert "/restablecer-contrasenia?token=" in correos[0].texto


def test_restablecer_cambia_contrasenia_y_cierra_sesiones(
    aplicacion, cliente, correos, sesion_iniciada
):
    """CA14: la contraseña cambia, el enlace se invalida y se cierran las sesiones."""
    otro_dispositivo = aplicacion.test_client()
    _iniciar(otro_dispositivo)
    cliente.post("/api/cuentas/recuperacion", json={"correo": sesion_iniciada["correo"]})
    token = extraer_token(correos[-1])

    respuesta = cliente.post(
        "/api/cuentas/recuperacion/restablecer", json={"token": token, "contrasenia": NUEVA}
    )
    assert respuesta.status_code == 200
    assert cliente.get("/api/sesion").status_code == 401
    assert otro_dispositivo.get("/api/sesion").status_code == 401
    assert _iniciar(cliente, contrasenia=NUEVA).status_code == 200
    assert "contraseña" in correos[-1].asunto.lower()

    reutilizado = cliente.post(
        "/api/cuentas/recuperacion/restablecer",
        json={"token": token, "contrasenia": "Distinta2027"},
    )
    assert reutilizado.status_code == 400


def test_restablecer_con_enlace_vencido_o_alterado_se_rechaza(
    cliente, correos, aplicacion, registrar_y_verificar
):
    """CA15: enlaces vencidos o alterados se rechazan."""
    registrar_y_verificar()
    cliente.post("/api/cuentas/recuperacion", json={"correo": "ana@ejemplo.com"})
    token = extraer_token(correos[-1])

    alterado = cliente.post(
        "/api/cuentas/recuperacion/restablecer", json={"token": token + "x", "contrasenia": NUEVA}
    )
    assert alterado.status_code == 400

    aplicacion.config["VIGENCIA_TOKEN_RECUPERACION"] = timedelta(seconds=-1)
    vencido = cliente.post(
        "/api/cuentas/recuperacion/restablecer", json={"token": token, "contrasenia": NUEVA}
    )
    assert vencido.status_code == 400
    assert "venció" in vencido.get_json()["mensaje"]


def test_restablecer_con_contrasenia_debil_no_consume_el_enlace(
    cliente, correos, registrar_y_verificar
):
    """La política se aplica y el enlace sigue sirviendo para un segundo intento."""
    registrar_y_verificar()
    cliente.post("/api/cuentas/recuperacion", json={"correo": "ana@ejemplo.com"})
    token = extraer_token(correos[-1])
    debil = cliente.post(
        "/api/cuentas/recuperacion/restablecer",
        json={"token": token, "contrasenia": "solo-letras-aqui"},
    )
    assert debil.status_code == 400
    valida = cliente.post(
        "/api/cuentas/recuperacion/restablecer", json={"token": token, "contrasenia": NUEVA}
    )
    assert valida.status_code == 200


def test_restablecer_verifica_y_desbloquea_la_cuenta(aplicacion, cliente, correos):
    """El enlace demuestra acceso al correo: verifica la cuenta y quita el bloqueo."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    for _ in range(5):
        _iniciar(cliente, contrasenia="Incorrecta123")
    cliente.post("/api/cuentas/recuperacion", json={"correo": "ana@ejemplo.com"})
    token = extraer_token(correos[-1])
    cliente.post(
        "/api/cuentas/recuperacion/restablecer", json={"token": token, "contrasenia": NUEVA}
    )
    usuario = obtener_usuario(aplicacion)
    assert usuario.verificado and usuario.bloqueado_hasta is None
    assert _iniciar(cliente, contrasenia=NUEVA).status_code == 200
