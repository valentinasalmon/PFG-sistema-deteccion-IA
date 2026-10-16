"""Accesorios (fixtures) compartidos por todas las pruebas de pytest."""
import re

import pytest

from app import crear_app
from app.extensiones import db
from app.modelos.entrada_auditoria import EntradaAuditoria
from app.modelos.usuario import Usuario

CONTRASENIA_VALIDA = "Segura12345"


@pytest.fixture
def aplicacion():
    """Aplicación de pruebas con la base de datos en memoria creada y vacía.

    El contexto de la aplicación se abre solo para crear y borrar las tablas.
    Así cada solicitud del cliente de pruebas abre su propio contexto, como en
    producción; si quedara abierto, todas las solicitudes compartirían ``g`` y
    la sesión de la base, y Flask-Login reutilizaría el usuario de una
    solicitud anterior.
    """
    app = crear_app("pruebas")
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()
        # Cierra las conexiones para no dejar bases en memoria abiertas.
        db.engine.dispose()


def obtener_usuario(aplicacion, correo="ana@ejemplo.com"):  # pylint: disable=redefined-outer-name
    """Lee un usuario de la base en un contexto propio, como lo vería otra solicitud."""
    with aplicacion.app_context():
        return Usuario.query.filter_by(correo=correo).first()


def contar_usuarios(aplicacion):  # pylint: disable=redefined-outer-name
    """Cantidad de cuentas guardadas."""
    with aplicacion.app_context():
        return Usuario.query.count()


def modificar_usuario(  # pylint: disable=redefined-outer-name
    aplicacion, campos, correo="ana@ejemplo.com"
):
    """Cambia campos de un usuario directamente en la base.

    Sirve, por ejemplo, para simular el paso del tiempo en un bloqueo.
    """
    with aplicacion.app_context():
        usuario = Usuario.query.filter_by(correo=correo).first()
        for campo, valor in campos.items():
            setattr(usuario, campo, valor)
        db.session.commit()


def entradas_auditoria(aplicacion, accion=None):  # pylint: disable=redefined-outer-name
    """Entradas de auditoría guardadas, en orden, como diccionarios.

    Args:
        accion: si se indica, solo las de esa acción.
    """
    with aplicacion.app_context():
        consulta = EntradaAuditoria.query.order_by(EntradaAuditoria.id)
        if accion is not None:
            consulta = consulta.filter_by(accion=accion)
        return [
            {
                "fecha": entrada.fecha,
                "id_usuario": entrada.id_usuario,
                "ip": entrada.ip,
                "accion": entrada.accion,
                "tipo_recurso": entrada.tipo_recurso,
                "id_recurso": entrada.id_recurso,
                "resultado": entrada.resultado,
                "detalle": entrada.detalle,
            }
            for entrada in consulta
        ]


@pytest.fixture
def cliente(aplicacion):  # pylint: disable=redefined-outer-name
    """Cliente HTTP de prueba para invocar la API sin levantar un servidor."""
    return aplicacion.test_client()


@pytest.fixture
def correos(aplicacion):  # pylint: disable=redefined-outer-name
    """Lista de correos "enviados" durante la prueba (enviador en memoria)."""
    return aplicacion.extensions["enviador_correo"].enviados


def extraer_token(correo):
    """Obtiene el token del enlace incluido en un correo."""
    return re.search(r"token=([\w.\-]+)", correo.texto).group(1)


def datos_registro(**cambios):
    """Datos válidos de registro, con los cambios indicados."""
    datos = {
        "nombre": "Ana",
        "apellido": "López",
        "correo": "ana@ejemplo.com",
        "contrasenia": CONTRASENIA_VALIDA,
        "perfil": "abogado",
        "colegio": "CPACF",
        "acepta_terminos": True,
    }
    datos.update(cambios)
    return datos


@pytest.fixture
def registrar_y_verificar(cliente, correos):  # pylint: disable=redefined-outer-name
    """Registra una cuenta y la verifica; devuelve los datos usados."""

    def _registrar(**cambios):
        datos = datos_registro(**cambios)
        cliente.post("/api/cuentas/registro", json=datos)
        token = extraer_token(correos[-1])
        cliente.post("/api/cuentas/verificacion", json={"token": token})
        return datos

    return _registrar


@pytest.fixture
def sesion_iniciada(cliente, registrar_y_verificar):  # pylint: disable=redefined-outer-name
    """Cliente con una sesión iniciada; devuelve los datos de la cuenta."""
    datos = registrar_y_verificar()
    respuesta = cliente.post(
        "/api/sesion", json={"correo": datos["correo"], "contrasenia": datos["contrasenia"]}
    )
    assert respuesta.status_code == 200
    return datos
