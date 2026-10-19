"""Pruebas del registro de auditoría a través de la API.

Criterios de aceptación de la funcionalidad 003: CA1 a CA14. Cada acción de
cuenta y sesión se ejecuta por la API y se comprueba la entrada que deja.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
import json
from datetime import timedelta

import pytest
from sqlalchemy.exc import OperationalError

from app.repositorios.repositorio_auditoria import RepositorioAuditoria
from app.seguridad.autenticacion import CLAVE_INICIO_SESION
from app.utilidades.tiempo import ahora_utc
from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    contar_usuarios,
    datos_registro,
    entradas_auditoria,
    extraer_token,
    obtener_usuario,
)

IP = "203.0.113.7"
OTRA_CONTRASENIA = "OtraSegura987"


@pytest.fixture
def cliente(aplicacion):
    """Cliente cuyas solicitudes llegan desde una dirección IP conocida."""
    cliente_ip = aplicacion.test_client()
    cliente_ip.environ_base["REMOTE_ADDR"] = IP
    return cliente_ip


def _iniciar(cliente, correo="ana@ejemplo.com", contrasenia=CONTRASENIA_VALIDA):
    return cliente.post("/api/sesion", json={"correo": correo, "contrasenia": contrasenia})


def _ultima(aplicacion, accion):
    entradas = entradas_auditoria(aplicacion, accion)
    assert entradas, f"No se registró ninguna entrada de {accion}"
    return entradas[-1]


# --- Contenido de las entradas (CA1, CA2) ---

def test_la_entrada_tiene_todos_los_datos(aplicacion, cliente):
    """CA1: fecha UTC, usuario, IP, acción, recurso, resultado y detalle."""
    antes = ahora_utc()
    cliente.post("/api/cuentas/registro", json=datos_registro())
    usuario = obtener_usuario(aplicacion)
    entrada = _ultima(aplicacion, "cuenta.registro")
    assert antes <= entrada["fecha"] <= ahora_utc()
    assert entrada["id_usuario"] == usuario.id
    assert entrada["ip"] == IP
    assert entrada["tipo_recurso"] == "usuario"
    assert entrada["id_recurso"] == str(usuario.id)
    assert entrada["resultado"] == "exitoso"
    assert entrada["detalle"] == {"perfil": "abogado", "version_terminos": "1.0"}


def test_ninguna_entrada_guarda_secretos(aplicacion, cliente, correos, registrar_y_verificar):
    """CA2: no hay contraseñas, hashes, tokens ni identificadores de sesión."""
    registrar_y_verificar()
    _iniciar(cliente, contrasenia="Incorrecta123")
    _iniciar(cliente)
    cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": CONTRASENIA_VALIDA, "contrasenia_nueva": OTRA_CONTRASENIA},
    )
    cliente.post("/api/cuentas/recuperacion", json={"correo": "ana@ejemplo.com"})
    token = extraer_token(correos[-1])
    cliente.post(
        "/api/cuentas/recuperacion/restablecer",
        json={"token": token, "contrasenia": CONTRASENIA_VALIDA},
    )
    secretos = [
        CONTRASENIA_VALIDA, OTRA_CONTRASENIA, "Incorrecta123", token,
        obtener_usuario(aplicacion).hash_contrasenia,
        *[extraer_token(correo) for correo in correos if "token=" in correo.texto],
    ]
    with cliente.session_transaction() as sesion:
        secretos.append(sesion.sid)
    texto = json.dumps([e["detalle"] for e in entradas_auditoria(aplicacion)])
    assert len(entradas_auditoria(aplicacion)) == 7
    for secreto in secretos:
        assert secreto not in texto


# --- Sesión (CA3 a CA6) ---

def test_inicio_de_sesion_exitoso(aplicacion, cliente, registrar_y_verificar):
    """CA3."""
    registrar_y_verificar()
    _iniciar(cliente)
    entrada = _ultima(aplicacion, "sesion.inicio")
    assert entrada["resultado"] == "exitoso"
    assert entrada["id_usuario"] == obtener_usuario(aplicacion).id


@pytest.mark.parametrize(
    ("credenciales", "motivo"),
    [
        (("ana@ejemplo.com", "Incorrecta123"), "contrasenia_incorrecta"),
        (("nadie@ejemplo.com", CONTRASENIA_VALIDA), "correo_inexistente"),
    ],
)
def test_inicio_de_sesion_fallido_registra_el_motivo(
    aplicacion, cliente, registrar_y_verificar, credenciales, motivo
):
    """CA4: el motivo queda en la auditoría y la respuesta sigue siendo genérica."""
    registrar_y_verificar()
    respuesta = _iniciar(cliente, *credenciales)
    assert respuesta.status_code == 401
    assert respuesta.get_json()["mensaje"] == "El correo o la contraseña no son correctos."
    entrada = _ultima(aplicacion, "sesion.inicio")
    assert entrada["resultado"] == "fallido"
    assert entrada["detalle"]["motivo"] == motivo


def test_correo_inexistente_registra_el_correo_intentado(aplicacion, cliente):
    """CA4 y RNF06 CA7: sin cuenta, el usuario queda vacío y se guarda el correo intentado."""
    _iniciar(cliente, correo="  Nadie@Ejemplo.com ")
    entrada = _ultima(aplicacion, "sesion.inicio")
    assert entrada["id_usuario"] is None
    assert entrada["detalle"] == {
        "motivo": "correo_inexistente", "correo_intentado": "nadie@ejemplo.com",
    }


def test_cuenta_sin_verificar_registra_el_motivo(aplicacion, cliente):
    """CA4."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    _iniciar(cliente)
    assert _ultima(aplicacion, "sesion.inicio")["detalle"]["motivo"] == "cuenta_no_verificada"


def test_bloqueo_y_cuenta_bloqueada(aplicacion, cliente, registrar_y_verificar):
    """CA4 y CA5: se registra el bloqueo con su vencimiento y los intentos posteriores."""
    registrar_y_verificar()
    for _ in range(5):
        _iniciar(cliente, contrasenia="Incorrecta123")
    bloqueo = _ultima(aplicacion, "cuenta.bloqueo")
    usuario = obtener_usuario(aplicacion)
    assert bloqueo["resultado"] == "exitoso"
    assert bloqueo["id_recurso"] == str(usuario.id)
    assert bloqueo["detalle"]["intentos"] == 5
    assert bloqueo["detalle"]["bloqueado_hasta"] == usuario.bloqueado_hasta.isoformat()

    _iniciar(cliente)
    assert _ultima(aplicacion, "sesion.inicio")["detalle"]["motivo"] == "cuenta_bloqueada"
    inicios = entradas_auditoria(aplicacion, "sesion.inicio")
    intentos = [entrada["detalle"].get("intentos") for entrada in inicios]
    assert intentos[:5] == [1, 2, 3, 4, 5]


def test_cierre_manual(aplicacion, cliente, sesion_iniciada):
    """CA6."""
    cliente.delete("/api/sesion")
    entrada = _ultima(aplicacion, "sesion.cierre")
    assert entrada["detalle"] == {"motivo": "manual"}
    assert entrada["id_usuario"] == obtener_usuario(aplicacion).id


def test_cierre_por_duracion_maxima(aplicacion, cliente, sesion_iniciada):
    """CA6."""
    with cliente.session_transaction() as sesion:
        sesion[CLAVE_INICIO_SESION] = (ahora_utc() - timedelta(hours=8, minutes=1)).isoformat()
    assert cliente.get("/api/sesion").status_code == 401
    assert _ultima(aplicacion, "sesion.cierre")["detalle"] == {"motivo": "duracion_maxima"}


# --- Registro, verificación y contraseña (CA7 a CA10) ---

def test_registro_con_correo_existente(aplicacion, cliente, registrar_y_verificar):
    """CA7: se registra el intento y la respuesta no lo revela."""
    registrar_y_verificar()
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro(nombre="Otra"))
    assert respuesta.status_code == 201
    entrada = _ultima(aplicacion, "cuenta.registro")
    assert entrada["resultado"] == "rechazado"
    assert entrada["id_usuario"] is None
    assert entrada["id_recurso"] == str(obtener_usuario(aplicacion).id)
    assert entrada["detalle"] == {"motivo": "correo_existente", "verificada": True}
    assert contar_usuarios(aplicacion) == 1


def test_verificacion_y_reenvio(aplicacion, cliente, correos):
    """CA8."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    cliente.post("/api/cuentas/verificacion/reenvio", json={"correo": "ana@ejemplo.com"})
    assert _ultima(aplicacion, "cuenta.reenvio_verificacion")["resultado"] == "exitoso"

    cliente.post("/api/cuentas/verificacion", json={"token": extraer_token(correos[-1])})
    assert _ultima(aplicacion, "cuenta.verificacion")["resultado"] == "exitoso"

    cliente.post("/api/cuentas/verificacion/reenvio", json={"correo": "ana@ejemplo.com"})
    reenvio = _ultima(aplicacion, "cuenta.reenvio_verificacion")
    assert (reenvio["resultado"], reenvio["detalle"]["motivo"]) == ("rechazado", "ya_verificada")

    cliente.post("/api/cuentas/verificacion/reenvio", json={"correo": "nadie@ejemplo.com"})
    reenvio = _ultima(aplicacion, "cuenta.reenvio_verificacion")
    assert reenvio["detalle"] == {"motivo": "correo_inexistente", "correo": "nadie@ejemplo.com"}


@pytest.mark.parametrize("caso", ["ya_usado", "alterado", "vencido"])
def test_enlace_de_verificacion_invalido(aplicacion, cliente, correos, caso):
    """CA8: el enlace usado, alterado o vencido se registra como fallido con su motivo."""
    cliente.post("/api/cuentas/registro", json=datos_registro())
    token = extraer_token(correos[-1])
    if caso == "ya_usado":
        cliente.post("/api/cuentas/verificacion", json={"token": token})
    elif caso == "alterado":
        token = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    else:
        aplicacion.config["VIGENCIA_TOKEN_VERIFICACION"] = timedelta(seconds=-1)
    assert cliente.post("/api/cuentas/verificacion", json={"token": token}).status_code == 400
    entrada = _ultima(aplicacion, "cuenta.verificacion")
    assert (entrada["resultado"], entrada["detalle"]["motivo"]) == ("fallido", caso)


def test_recuperacion_y_restablecimiento(aplicacion, cliente, correos, registrar_y_verificar):
    """CA9."""
    registrar_y_verificar()
    cliente.post("/api/cuentas/recuperacion", json={"correo": "nadie@ejemplo.com"})
    assert _ultima(aplicacion, "contrasenia.recuperacion")["detalle"] == {
        "motivo": "correo_inexistente", "correo": "nadie@ejemplo.com",
    }
    cliente.post("/api/cuentas/recuperacion", json={"correo": "ana@ejemplo.com"})
    solicitud = _ultima(aplicacion, "contrasenia.recuperacion")
    assert solicitud["resultado"] == "exitoso"
    assert solicitud["detalle"] == {"correo": "ana@ejemplo.com"}

    token = extraer_token(correos[-1])
    datos = {"token": token, "contrasenia": OTRA_CONTRASENIA}
    assert cliente.post("/api/cuentas/recuperacion/restablecer", json=datos).status_code == 200
    restablecimiento = _ultima(aplicacion, "contrasenia.restablecimiento")
    assert restablecimiento["resultado"] == "exitoso"
    assert restablecimiento["id_usuario"] == obtener_usuario(aplicacion).id

    assert cliente.post("/api/cuentas/recuperacion/restablecer", json=datos).status_code == 400
    fallido = _ultima(aplicacion, "contrasenia.restablecimiento")
    assert (fallido["resultado"], fallido["detalle"]["motivo"]) == ("fallido", "ya_usado")


def test_cambio_de_contrasenia(aplicacion, cliente, sesion_iniciada):
    """CA10: exitoso, y fallido si la contraseña actual es incorrecta."""
    cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": "Incorrecta123", "contrasenia_nueva": OTRA_CONTRASENIA},
    )
    fallido = _ultima(aplicacion, "contrasenia.cambio")
    assert fallido["detalle"] == {"motivo": "contrasenia_incorrecta"}
    cliente.post(
        "/api/perfil/contrasenia",
        json={"contrasenia_actual": CONTRASENIA_VALIDA, "contrasenia_nueva": OTRA_CONTRASENIA},
    )
    assert _ultima(aplicacion, "contrasenia.cambio")["resultado"] == "exitoso"


# --- Perfil y correo (CA11, CA12) ---

def test_edicion_del_perfil_guarda_valor_anterior_y_nuevo(aplicacion, cliente, sesion_iniciada):
    """CA11: solo los campos que cambiaron, con su valor anterior y el nuevo."""
    cliente.patch("/api/perfil", json={"nombre": "Ana María", "apellido": "López", "colegio": ""})
    entrada = _ultima(aplicacion, "perfil.edicion")
    assert entrada["resultado"] == "exitoso"
    assert entrada["detalle"] == {
        "cambios": {
            "nombre": {"anterior": "Ana", "nuevo": "Ana María"},
            "colegio": {"anterior": "CPACF", "nuevo": None},
        }
    }


def test_edicion_sin_cambios_no_registra(aplicacion, cliente, sesion_iniciada):
    """Guardar los mismos datos no es una modificación."""
    cliente.patch("/api/perfil", json={"nombre": "Ana"})
    assert not entradas_auditoria(aplicacion, "perfil.edicion")


@pytest.mark.parametrize(
    ("cambios", "motivo"),
    [
        ({"perfil": "aseguradora"}, "cambio_de_perfil"),
        ({"empresa": "Seguros SA"}, "dato_de_otro_perfil"),
    ],
)
def test_edicion_rechazada(aplicacion, cliente, sesion_iniciada, cambios, motivo):
    """CA11: el intento de cambiar el perfil se registra como rechazado."""
    assert cliente.patch("/api/perfil", json=cambios).status_code == 400
    entrada = _ultima(aplicacion, "perfil.edicion")
    assert (entrada["resultado"], entrada["detalle"]["motivo"]) == ("rechazado", motivo)


def test_cambio_de_correo(aplicacion, cliente, correos, sesion_iniciada):
    """CA12: la solicitud y la confirmación, con el correo anterior y el nuevo."""
    esperado = {"anterior": "ana@ejemplo.com", "nuevo": "ana.nueva@ejemplo.com"}
    cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "ana.nueva@ejemplo.com", "contrasenia": "Mala1234567"},
    )
    assert _ultima(aplicacion, "correo.solicitud_cambio")["resultado"] == "fallido"
    cliente.post(
        "/api/perfil/correo",
        json={"correo_nuevo": "Ana.Nueva@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA},
    )
    solicitud = _ultima(aplicacion, "correo.solicitud_cambio")
    assert (solicitud["resultado"], solicitud["detalle"]) == ("exitoso", esperado)

    token = extraer_token(next(c for c in correos if c.destinatario == "ana.nueva@ejemplo.com"))
    cliente.post("/api/perfil/correo/confirmacion", json={"token": token})
    cambio = _ultima(aplicacion, "correo.cambio")
    assert (cambio["resultado"], cambio["detalle"]) == ("exitoso", esperado)

    cliente.post("/api/perfil/correo/confirmacion", json={"token": token})
    assert _ultima(aplicacion, "correo.cambio")["detalle"] == {"motivo": "ya_usado"}


def test_cambio_a_correo_en_uso(aplicacion, cliente, correos, registrar_y_verificar):
    """CA12: pedir o confirmar un correo de otra cuenta se registra como rechazado."""
    registrar_y_verificar()
    _iniciar(cliente)
    pedido = {"correo_nuevo": "beto@ejemplo.com", "contrasenia": CONTRASENIA_VALIDA}
    cliente.post("/api/perfil/correo", json=pedido)
    token = extraer_token(next(c for c in correos if c.destinatario == "beto@ejemplo.com"))
    aplicacion.test_client().post(
        "/api/cuentas/registro", json=datos_registro(correo="beto@ejemplo.com")
    )
    cliente.post("/api/perfil/correo/confirmacion", json={"token": token})
    assert _ultima(aplicacion, "correo.cambio")["detalle"]["motivo"] == "correo_en_uso"
    cliente.post("/api/perfil/correo", json=pedido)
    assert _ultima(aplicacion, "correo.solicitud_cambio")["resultado"] == "rechazado"


# --- Integridad (CA13, CA14) ---

def test_la_api_no_permite_modificar_ni_eliminar_la_auditoria(aplicacion):
    """CA13: no hay ninguna ruta de la API sobre la auditoría."""
    rutas = [regla.rule for regla in aplicacion.url_map.iter_rules()]
    assert not [ruta for ruta in rutas if "auditoria" in ruta]


def _fallar_al_guardar(monkeypatch):
    def agregar(_self, _entrada):
        raise OperationalError("INSERT INTO auditoria", {}, Exception("disco lleno"))

    monkeypatch.setattr(RepositorioAuditoria, "agregar", agregar)


def test_si_la_entrada_no_se_guarda_la_cuenta_no_se_crea(aplicacion, cliente, correos, monkeypatch):
    """CA14: la acción se cancela, no se envía el correo y el mensaje es genérico."""
    _fallar_al_guardar(monkeypatch)
    respuesta = cliente.post("/api/cuentas/registro", json=datos_registro())
    assert respuesta.status_code == 500
    assert respuesta.get_json() == {
        "mensaje": "Ocurrió un error inesperado. Intentá de nuevo.", "codigo": "error_interno",
    }
    assert contar_usuarios(aplicacion) == 0
    assert not correos


def test_si_la_entrada_no_se_guarda_no_se_edita_el_perfil(
    aplicacion, cliente, sesion_iniciada, monkeypatch
):
    """CA14."""
    _fallar_al_guardar(monkeypatch)
    assert cliente.patch("/api/perfil", json={"nombre": "Otra"}).status_code == 500
    assert obtener_usuario(aplicacion).nombre == "Ana"


def test_si_la_entrada_no_se_guarda_la_sesion_no_se_abre_ni_se_cierra(
    aplicacion, cliente, registrar_y_verificar, monkeypatch
):
    """CA14: sin rastro en la auditoría no hay inicio ni cierre de sesión."""
    registrar_y_verificar()
    with monkeypatch.context() as parche:
        _fallar_al_guardar(parche)
        assert _iniciar(cliente).status_code == 500
    assert cliente.get("/api/sesion").status_code == 401

    _iniciar(cliente)
    _fallar_al_guardar(monkeypatch)
    assert cliente.delete("/api/sesion").status_code == 500
    assert cliente.get("/api/sesion").status_code == 200
