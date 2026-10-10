"""Redacción de los correos de la plataforma.

Arma cada correo a partir de una plantilla Jinja2 (texto y HTML) y lo entrega
al enviador configurado. No conoce Flask: recibe el enviador y la dirección
del frontend por parámetro.

Realiza: RF47 (eventos de cuenta), RNF10 (CA4: textos en español).
"""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.integraciones.correo import Correo

DIRECTORIO_PLANTILLAS = Path(__file__).resolve().parents[1] / "plantillas" / "correos"

_entorno = Environment(
    loader=FileSystemLoader(DIRECTORIO_PLANTILLAS),
    autoescape=select_autoescape(["html"]),
)


class ServicioCorreos:
    """Un método por cada correo que envía la funcionalidad de cuentas."""

    def __init__(self, enviador, url_frontend):
        self.enviador = enviador
        self.url_frontend = url_frontend.rstrip("/")

    def _enviar(self, destinatario, asunto, plantilla, **datos):
        """Renderiza la plantilla en texto y HTML y envía el correo."""
        datos["asunto"] = asunto
        texto = _entorno.get_template(f"{plantilla}.txt").render(**datos)
        html = _entorno.get_template(f"{plantilla}.html").render(**datos)
        return self.enviador.enviar(Correo(destinatario, asunto, texto, html))

    def _enlace(self, ruta, token):
        return f"{self.url_frontend}{ruta}?token={token}"

    def enviar_verificacion(self, usuario, token):
        """Enlace para verificar el correo después del registro (RF02)."""
        return self._enviar(
            usuario.correo, "Verificá tu correo electrónico", "verificacion",
            nombre=usuario.nombre, enlace=self._enlace("/verificar-correo", token),
        )

    def enviar_aviso_registro_existente(self, usuario):
        """Aviso al titular cuando alguien intenta registrarse con su correo (RF01 CA3)."""
        return self._enviar(
            usuario.correo, "Intento de registro con tu correo", "registro_existente",
            nombre=usuario.nombre, enlace=f"{self.url_frontend}/recuperar-contrasenia",
        )

    def enviar_recuperacion(self, usuario, token):
        """Enlace para restablecer la contraseña, válido por 1 hora (RF05)."""
        return self._enviar(
            usuario.correo, "Restablecé tu contraseña", "recuperacion",
            nombre=usuario.nombre, enlace=self._enlace("/restablecer-contrasenia", token),
        )

    def enviar_aviso_contrasenia_cambiada(self, usuario):
        """Aviso de que la contraseña fue cambiada (RF05 CA3, RF06 CA1)."""
        return self._enviar(
            usuario.correo, "Tu contraseña fue cambiada", "contrasenia_cambiada",
            nombre=usuario.nombre, enlace=f"{self.url_frontend}/recuperar-contrasenia",
        )

    def enviar_aviso_bloqueo(self, usuario, minutos):
        """Aviso de bloqueo temporal por intentos fallidos (RNF01 CA3)."""
        return self._enviar(
            usuario.correo, "Tu cuenta fue bloqueada temporalmente", "bloqueo",
            nombre=usuario.nombre, minutos=minutos,
            enlace=f"{self.url_frontend}/recuperar-contrasenia",
        )

    def enviar_confirmacion_cambio_correo(self, usuario, correo_nuevo, token):
        """Enlace a la dirección nueva para confirmar el cambio de correo (RF07 CA2)."""
        return self._enviar(
            correo_nuevo, "Confirmá tu nuevo correo electrónico", "confirmacion_correo",
            nombre=usuario.nombre, enlace=self._enlace("/confirmar-correo", token),
        )

    def enviar_aviso_cambio_correo(self, usuario, correo_nuevo):
        """Aviso a la dirección anterior de que se pidió un cambio de correo (RF07 CA2)."""
        return self._enviar(
            usuario.correo, "Se solicitó cambiar el correo de tu cuenta", "aviso_cambio_correo",
            nombre=usuario.nombre, correo_nuevo=correo_nuevo,
        )
