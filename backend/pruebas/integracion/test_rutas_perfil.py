"""Pruebas del perfil propio: datos, contraseña y correo.

Criterios de aceptación de la funcionalidad 002: CA16 a CA19.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
from datetime import timedelta

from pruebas.conftest import CONTRASENIA_VALIDA, extraer_token, obtener_usuario

NUEVA = "OtraClave2026"


def _iniciar(cliente, correo="ana@ejemplo.com", contrasenia=CONTRASENIA_VALIDA):
    return cliente.post("/api/sesion", json={"correo": correo, "contrasenia": contrasenia})


def test_ver_perfil(cliente, sesion_iniciada):
    """El perfil muestra los datos propios, incluido el perfil elegido."""
    usuario = cliente.get("/api/perfil").get_json()["usuario"]
    assert usuario["perfil"] == "abogado" and usuario["colegio"] == "CPACF"
    assert "empresa" not in usuario


def test_editar_nombre_apellido_y_colegio(aplicacion, cliente, sesion_iniciada):
    """CA17: los cambios se guardan; un texto vacío borra el colegio."""
    respuesta = cliente.patch("/api/perfil", json={"nombre": " Ana María ", "apellido": "Gómez"})
    assert respuesta.status_code == 200
    assert respuesta.get_json()["usuario"]["nombre"] == "Ana María"
    cliente.patch("/api/perfil", json={"colegio": ""})
    assert obtener_usuario(aplicacion).colegio is None


def test_no_se_puede_cambiar_el_perfil(aplicacion, cliente, sesion_iniciada):
    """CA19 y RN01: el perfil elegido al registrarse no se modifica."""
    respuesta = cliente.patch("/api/perfil", json={"perfil": "aseguradora"})
    assert respuesta.status_code == 400
    assert "perfil" in respuesta.get_json()["errores"]
    assert obtener_usuario(aplicacion).perfil == "abogado"


def test_abogado_no_puede_cargar_empresa(cliente, sesion_iniciada):
    """RN02: la empresa corresponde solo al perfil Aseguradora."""
    respuesta = cliente.patch("/api/perfil", json={"empresa": "Seguros SA"})
    assert respuesta.status_code == 400
    assert "empresa" in respuesta.get_json()["errores"]


def test_aseguradora_no_puede_cargar_colegio(cliente, registrar_y_verificar):
    """RN02: el colegio corresponde solo al perfil Abogado."""
    registrar_y_verificar(perfil="aseguradora", colegio=None, empresa="Seguros SA")
    _iniciar(cliente)
    assert cliente.get("/api/perfil").get_json()["usuario"]["empresa"] == "Seguros SA"
    respuesta = cliente.patch("/api/perfil", json={"colegio": "CPACF"})
    assert respuesta.status_code == 400


def test_editar_con_campo_desconocido_se_rechaza(aplicacion, cliente, sesion_iniciada):
    """RNF04 CA1: no se aceptan campos fuera del esquema (por ejemplo, el rol)."""
    respuesta = cliente.patch("/api/perfil", json={"rol": "administrador"})
    assert respuesta.status_code == 400
    assert obtener_usuario(aplicacion).rol == "usuario"


def test_cambiar_contrasenia(aplicacion, cliente, correos, sesion_iniciada):
    """CA16: con la actual correcta cambia, avisa y cierra las demás sesiones."""
    otro_dispositivo = aplicacion.test_client()
    _iniciar(otro_dispositivo)
    correos.clear()
    respuesta = cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": CONTRASENIA_VALIDA, "contrasenia_nueva": NUEVA},
    )
    assert respuesta.status_code == 200
    assert len(correos) == 1
    assert cliente.get("/api/sesion").status_code == 200
    assert otro_dispositivo.get("/api/sesion").status_code == 401
    cliente.delete("/api/sesion")
    assert _iniciar(cliente, contrasenia=NUEVA).status_code == 200


def test_cambiar_contrasenia_con_actual_incorrecta_se_rechaza(cliente, sesion_iniciada):
    """CA16: con la actual incorrecta se rechaza."""
    respuesta = cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": "Incorrecta123", "contrasenia_nueva": NUEVA},
    )
    assert respuesta.status_code == 400
    assert "contrasenia_actual" in respuesta.get_json()["errores"]


def test_cambiar_contrasenia_por_la_misma_o_debil_se_rechaza(cliente, sesion_iniciada):
    """La nueva debe cumplir la política y ser distinta de la actual."""
    misma = cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": CONTRASENIA_VALIDA, "contrasenia_nueva": CONTRASENIA_VALIDA},
    )
    debil = cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": CONTRASENIA_VALIDA, "contrasenia_nueva": "1234567890"},
    )
    assert misma.status_code == debil.status_code == 400
    assert "contrasenia_nueva" in debil.get_json()["errores"]


def test_cambio_de_correo_queda_pendiente_hasta_confirmar(
    aplicacion, cliente, correos, sesion_iniciada
):
    """CA18: confirmación en la dirección nueva y aviso a la anterior."""
    correos.clear()
    respuesta = cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "ana.nueva@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA},
    )
    assert respuesta.status_code == 200
    destinatarios = {correo.destinatario for correo in correos}
    assert destinatarios == {"ana.nueva@ejemplo.com", "ana@ejemplo.com"}
    assert obtener_usuario(aplicacion) is not None

    confirmacion = next(c for c in correos if c.destinatario == "ana.nueva@ejemplo.com")
    token = extraer_token(confirmacion)
    assert cliente.post("/api/perfil/correo/confirmacion", json={"token": token}).status_code == 200
    assert obtener_usuario(aplicacion, "ana.nueva@ejemplo.com") is not None

    # El enlace es de un solo uso.
    assert cliente.post("/api/perfil/correo/confirmacion", json={"token": token}).status_code == 400


def test_cambio_de_correo_exige_contrasenia_y_correo_distinto(cliente, sesion_iniciada):
    """Se pide la contraseña y se rechaza el mismo correo."""
    sin_contrasenia = cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "otra@ejemplo.com", "contrasenia": "Incorrecta123"},
    )
    mismo = cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "ANA@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA},
    )
    assert sin_contrasenia.status_code == mismo.status_code == 400


def test_cambio_a_correo_en_uso_se_rechaza(aplicacion, cliente, correos, registrar_y_verificar):
    """No se puede tomar un correo de otra cuenta, ni al pedirlo ni al confirmarlo."""
    registrar_y_verificar()
    _iniciar(cliente)
    correos.clear()
    cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "beto@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA},
    )
    token = extraer_token(next(c for c in correos if c.destinatario == "beto@ejemplo.com"))

    otro = aplicacion.test_client()
    otro.post("/api/cuentas/registro", json={
        "nombre": "Beto", "apellido": "Paz", "correo": "beto@ejemplo.com",
        "contrasenia": CONTRASENIA_VALIDA, "perfil": "aseguradora", "acepta_terminos": True,
    })
    assert cliente.post("/api/perfil/correo/confirmacion", json={"token": token}).status_code == 409

    en_uso = cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "beto@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA},
    )
    assert en_uso.status_code == 409


def test_confirmacion_de_correo_vencida_se_rechaza(aplicacion, cliente, correos, sesion_iniciada):
    """El enlace de cambio de correo vence a las 24 horas."""
    cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "ana.nueva@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA},
    )
    token = extraer_token(next(c for c in correos if c.destinatario == "ana.nueva@ejemplo.com"))
    aplicacion.config["VIGENCIA_TOKEN_CAMBIO_CORREO"] = timedelta(seconds=-1)
    assert cliente.post("/api/perfil/correo/confirmacion", json={"token": token}).status_code == 400
