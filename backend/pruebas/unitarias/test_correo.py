"""Pruebas del envío de correo y de la redacción de los mensajes."""
import smtplib

from app.integraciones.correo import Correo, EnviadorMemoria, EnviadorSMTP, crear_enviador
from app.servicios.servicio_correos import ServicioCorreos


class UsuarioFalso:  # pylint: disable=too-few-public-methods
    """Usuario mínimo para redactar correos."""

    nombre = "Ana"
    correo = "ana@ejemplo.com"


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
