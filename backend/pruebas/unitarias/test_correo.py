"""Pruebas del envío de correo y de la redacción de los mensajes."""
import smtplib
from datetime import datetime
from types import SimpleNamespace

from app import crear_app
from app.integraciones import correo as modulo_correo
from app.integraciones.cola import ColaSincronica
from app.integraciones.correo import (
    Correo,
    EnviadorEnSegundoPlano,
    EnviadorMemoria,
    EnviadorSMTP,
    crear_enviador,
)
from app.servicios.servicio_correos import ServicioCorreos


class UsuarioFalso:  # pylint: disable=too-few-public-methods
    """Usuario mínimo para redactar correos."""

    nombre = "Ana"
    apellido = "López"
    correo = "ana@ejemplo.com"


ORGANIZACION = SimpleNamespace(id=7, nombre="Estudio Pérez")
INVITACION = SimpleNamespace(
    correo="beto@ejemplo.com", organizacion=ORGANIZACION, vence_en=datetime(2026, 10, 23)
)


def test_correo_de_verificacion_incluye_enlace_al_frontend():
    """El enlace apunta a la pantalla de verificación del frontend con el token."""
    enviador = EnviadorMemoria()
    ServicioCorreos(enviador, "http://frontend/").enviar_verificacion(UsuarioFalso(), "abc.def")
    correo = enviador.enviados[0]
    assert correo.destinatario == "ana@ejemplo.com"
    assert "http://frontend/verificar-correo?token=abc.def" in correo.texto
    assert "http://frontend/verificar-correo?token=abc.def" in correo.html
    assert "Hola, Ana" in correo.texto


def test_todos_los_correos_se_redactan():
    """Cada tipo de correo se arma sin errores de plantilla."""
    enviador = EnviadorMemoria()
    servicio = ServicioCorreos(enviador, "http://frontend")
    usuario = UsuarioFalso()
    servicio.enviar_aviso_registro_existente(usuario)
    servicio.enviar_recuperacion(usuario, "t")
    servicio.enviar_aviso_contrasenia_cambiada(usuario)
    servicio.enviar_aviso_bloqueo(usuario, 15)
    servicio.enviar_confirmacion_cambio_correo(usuario, "nuevo@ejemplo.com", "t")
    servicio.enviar_aviso_cambio_correo(usuario, "nuevo@ejemplo.com")
    assert len(enviador.enviados) == 6
    assert "15 minutos" in enviador.enviados[3].texto
    assert enviador.enviados[4].destinatario == "nuevo@ejemplo.com"


def test_cada_correo_tiene_su_propio_texto():
    """El texto y el HTML de cada correo corresponden a su motivo (evita plantillas cruzadas)."""
    enviador = EnviadorMemoria()
    servicio = ServicioCorreos(enviador, "http://frontend")
    usuario = UsuarioFalso()
    esperados = [
        (lambda: servicio.enviar_verificacion(usuario, "t"), "Gracias por registrarte"),
        (lambda: servicio.enviar_aviso_registro_existente(usuario), "intentó crear una cuenta"),
        (lambda: servicio.enviar_recuperacion(usuario, "t"), "restablecer tu contraseña"),
        (lambda: servicio.enviar_aviso_contrasenia_cambiada(usuario), "fue cambiada"),
        (lambda: servicio.enviar_aviso_bloqueo(usuario, 15), "intentos fallidos"),
        (lambda: servicio.enviar_confirmacion_cambio_correo(usuario, "n@e.com", "t"),
         "nuevo correo"),
        (lambda: servicio.enviar_aviso_cambio_correo(usuario, "n@e.com"), "Se pidió cambiar"),
        (lambda: servicio.enviar_invitacion(INVITACION, usuario, "t", False), "te invitó"),
        (lambda: servicio.enviar_respuesta_invitacion(usuario, INVITACION, True),
         "aceptó la invitación"),
        (lambda: servicio.enviar_respuesta_invitacion(usuario, INVITACION, False),
         "rechazó la invitación"),
        (lambda: servicio.enviar_aviso_desvinculacion(usuario, ORGANIZACION), "te desvinculó"),
        (lambda: servicio.enviar_aviso_cambio_referente(usuario, ORGANIZACION, True, usuario),
         "Ahora sos el Referente"),
        (lambda: servicio.enviar_aviso_cambio_referente(usuario, ORGANIZACION, False, usuario),
         "Designaste a Ana López"),
        (lambda: servicio.enviar_aviso_abandono(usuario, ORGANIZACION, usuario),
         "abandonó la organización"),
        (lambda: servicio.enviar_aviso_eliminacion_organizacion(usuario, "Estudio Pérez"),
         "fue eliminada"),
    ]
    for enviar, frase in esperados:
        enviar()
        correo = enviador.enviados[-1]
        assert frase in correo.texto, correo.asunto
        assert frase in correo.html, correo.asunto
        assert "{%" not in correo.texto and "<p>" not in correo.texto, correo.asunto
        assert correo.html.lstrip().startswith("<!doctype html>"), correo.asunto


def test_fabrica_de_enviadores():
    """La fábrica elige la implementación según la configuración."""
    assert isinstance(crear_enviador({"PROVEEDOR_CORREO": "memoria"}), EnviadorMemoria)
    smtp = crear_enviador({
        "PROVEEDOR_CORREO": "smtp", "SERVIDOR_CORREO": "localhost", "PUERTO_CORREO": 1025,
        "REMITENTE_CORREO": "a@b.c", "USUARIO_CORREO": "", "CONTRASENIA_CORREO": "",
        "USAR_TLS_CORREO": False,
    })
    assert isinstance(smtp, EnviadorSMTP)


def test_smtp_sin_servidor_no_interrumpe(monkeypatch):
    """Si el servidor SMTP no responde, se devuelve False sin lanzar errores (RF47 CA1)."""

    def conexion_rechazada(*_args, **_kwargs):
        raise ConnectionRefusedError("sin servidor")

    monkeypatch.setattr(smtplib, "SMTP", conexion_rechazada)
    enviador = EnviadorSMTP("localhost", 1, "a@b.c")
    assert enviador.enviar(Correo("x@y.z", "Asunto", "texto", "<p>html</p>")) is False


def test_smtp_con_tls_y_autenticacion(monkeypatch):
    """Con TLS y usuario configurados se usan STARTTLS y LOGIN antes de enviar."""
    llamadas = []

    class SMTPFalso:
        """Servidor SMTP simulado que registra las operaciones."""

        def __init__(self, *_args, **_kwargs):
            llamadas.append("conectar")

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def starttls(self):
            """Simula STARTTLS."""
            llamadas.append("starttls")

        def login(self, usuario, _contrasenia):
            """Simula la autenticación."""
            llamadas.append(f"login:{usuario}")

        def send_message(self, mensaje):
            """Simula el envío."""
            llamadas.append(f"enviar:{mensaje['To']}")

    monkeypatch.setattr(smtplib, "SMTP", SMTPFalso)
    enviador = EnviadorSMTP("smtp.ejemplo", 587, "a@b.c", "usuario", "clave", usar_tls=True)
    assert enviador.enviar(Correo("x@y.z", "Asunto", "texto", "<p>html</p>")) is True
    assert llamadas == ["conectar", "starttls", "login:usuario", "enviar:x@y.z"]


# --- Envío en segundo plano (funcionalidad 013, RF47 CA1 y CA3) ---

class EnviadorQueFalla:
    """Falla las primeras veces que se le pide entregar un correo."""

    def __init__(self, fallas):
        self.fallas = fallas
        self.entregados = []

    def entregar(self, correo):
        """Falla mientras queden fallas; después guarda el correo."""
        if self.fallas:
            self.fallas -= 1
            raise smtplib.SMTPServerDisconnected("sin conexión")
        self.entregados.append(correo)


CORREO = Correo("ana@ejemplo.com", "Asunto", "texto", "<p>html</p>")


def test_en_segundo_plano_reintenta_hasta_entregar(aplicacion):
    """Dos fallas del servidor y la tercera vez se entrega."""
    directo = EnviadorQueFalla(2)
    aplicacion.extensions["enviador_directo"] = directo
    with aplicacion.app_context():
        assert EnviadorEnSegundoPlano(ColaSincronica()).enviar(CORREO) is True
    assert directo.entregados == [CORREO]


def test_en_segundo_plano_una_falla_no_interrumpe(aplicacion, caplog, monkeypatch):
    """Agotados los reintentos, se registra en el log y no se propaga (RF47 CA1)."""
    # Las pruebas de migraciones configuran el log de Alembic y apagan los existentes.
    monkeypatch.setattr(modulo_correo.registro, "disabled", False)
    aplicacion.extensions["enviador_directo"] = EnviadorQueFalla(3)
    with aplicacion.app_context():
        assert EnviadorEnSegundoPlano(ColaSincronica()).enviar(CORREO) is False
    assert "No se pudo encolar el correo 'Asunto'" in caplog.text


def test_la_aplicacion_envia_en_segundo_plano_salvo_en_pruebas(monkeypatch):
    """Con SMTP los correos van a la cola ``correos``; en pruebas, a la memoria."""
    monkeypatch.setenv("URL_BASE_DATOS", "sqlite://")
    monkeypatch.setenv("COLA_ANALISIS", "sincronica")
    aplicacion = crear_app("desarrollo")

    assert isinstance(aplicacion.extensions["enviador_correo"], EnviadorEnSegundoPlano)
    assert isinstance(aplicacion.extensions["enviador_directo"], EnviadorSMTP)
    assert aplicacion.extensions["enviador_correo"].reintentos == (30, 120)
    assert isinstance(crear_app("pruebas").extensions["enviador_correo"], EnviadorMemoria)
