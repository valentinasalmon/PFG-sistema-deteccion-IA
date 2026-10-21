"""Envío de correo electrónico (patrón Strategy).

Tres implementaciones intercambiables con la misma interfaz ``enviar``:

- ``EnviadorSMTP``: envía por SMTP. En desarrollo apunta a Mailpit y en
  producción a la interfaz SMTP de Amazon SES (RF47).
- ``EnviadorEnSegundoPlano``: encola el correo para que lo envíe el proceso
  trabajador con ``EnviadorSMTP``, con reintentos (funcionalidad 013).
- ``EnviadorMemoria``: guarda los correos en una lista; se usa en las pruebas.

Realiza: RF47 (CA1, CA3); RNF18 (CA2).
"""
import logging
import smtplib
from dataclasses import asdict, dataclass
from email.message import EmailMessage

registro = logging.getLogger(__name__)


@dataclass
class Correo:
    """Mensaje listo para enviar."""

    destinatario: str
    asunto: str
    texto: str
    html: str


class EnviadorSMTP:
    """Envía correos por SMTP, opcionalmente con STARTTLS y autenticación."""

    TIEMPO_ESPERA_SEGUNDOS = 10

    def __init__(self, servidor, puerto, remitente, usuario="", contrasenia="", usar_tls=False):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        self.servidor = servidor
        self.puerto = puerto
        self.remitente = remitente
        self.usuario = usuario
        self.contrasenia = contrasenia
        self.usar_tls = usar_tls

    def enviar(self, correo):
        """Envía el correo. Devuelve True si se entregó al servidor SMTP.

        Una falla de envío no debe interrumpir la operación que la originó
        (RF47 CA1): se registra en el log y se devuelve False.
        """
        try:
            self.entregar(correo)
            return True
        except (OSError, smtplib.SMTPException):
            registro.exception("No se pudo enviar el correo '%s'", correo.asunto)
            return False

    def entregar(self, correo):
        """Envía el correo y, si falla, deja pasar la excepción para reintentarlo.

        Raises:
            OSError, smtplib.SMTPException: si el servidor no lo aceptó.
        """
        mensaje = EmailMessage()
        mensaje["From"] = self.remitente
        mensaje["To"] = correo.destinatario
        mensaje["Subject"] = correo.asunto
        mensaje.set_content(correo.texto)
        mensaje.add_alternative(correo.html, subtype="html")
        with smtplib.SMTP(self.servidor, self.puerto, timeout=self.TIEMPO_ESPERA_SEGUNDOS) as smtp:
            if self.usar_tls:
                smtp.starttls()
            if self.usuario:
                smtp.login(self.usuario, self.contrasenia)
            smtp.send_message(mensaje)


class EnviadorEnSegundoPlano:
    """Encola cada correo para enviarlo fuera de la solicitud (RF47 CA1 y CA3).

    La operación que origina el correo no espera al servidor de correo ni se
    revierte si el envío falla: el trabajo ``app.tareas.correos.entregar_correo``
    lo entrega y la cola lo reintenta a los segundos indicados en ``reintentos``.
    """

    TRABAJO = "app.tareas.correos.entregar_correo"

    def __init__(self, cola, reintentos=(30, 120)):
        self.cola = cola
        self.reintentos = tuple(reintentos)

    def enviar(self, correo):
        """Encola el correo; devuelve False solo si no se pudo encolar."""
        try:
            self.cola.encolar_con_reintentos(self.TRABAJO, self.reintentos, asdict(correo))
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            registro.exception("No se pudo encolar el correo '%s'", correo.asunto)
            return False


class EnviadorMemoria:
    """Guarda los correos en memoria en lugar de enviarlos (pruebas)."""

    def __init__(self):
        self.enviados = []

    def enviar(self, correo):
        """Agrega el correo a la lista ``enviados``."""
        self.enviados.append(correo)
        return True


def crear_enviador(configuracion):
    """Fábrica: elige el enviador según ``PROVEEDOR_CORREO`` de la configuración."""
    if configuracion["PROVEEDOR_CORREO"] == "memoria":
        return EnviadorMemoria()
    return EnviadorSMTP(
        servidor=configuracion["SERVIDOR_CORREO"],
        puerto=configuracion["PUERTO_CORREO"],
        remitente=configuracion["REMITENTE_CORREO"],
        usuario=configuracion["USUARIO_CORREO"],
        contrasenia=configuracion["CONTRASENIA_CORREO"],
        usar_tls=configuracion["USAR_TLS_CORREO"],
    )
