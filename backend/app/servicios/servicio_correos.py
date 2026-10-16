"""Redacción de los correos de la plataforma.

Arma cada correo a partir de una plantilla Jinja2 (texto y HTML) y lo entrega
al enviador configurado. No conoce Flask: recibe el enviador y la dirección
del frontend por parámetro.

Realiza: RF47 (eventos de cuenta y de organizaciones), RNF10 (CA4: textos en español).
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
    """Un método por cada correo que envía la plataforma."""

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

    # --- Organizaciones (funcionalidad 004) ---

    def _enlace_organizacion(self, organizacion):
        return f"{self.url_frontend}/organizaciones/{organizacion.id}"

    def enviar_invitacion(self, invitacion, invitante, token, registrado):
        """Invitación a sumarse a una organización (RF12 CA1 y CA2).

        Args:
            registrado: True si el correo ya tiene una cuenta; cambia la indicación final.
        """
        return self._enviar(
            invitacion.correo, f"Te invitaron a {invitacion.organizacion.nombre}", "invitacion",
            invitante=f"{invitante.nombre} {invitante.apellido}",
            organizacion=invitacion.organizacion.nombre, correo=invitacion.correo,
            vence=invitacion.vence_en.strftime("%d/%m/%Y"), registrado=registrado,
            enlace=self._enlace("/invitaciones/responder", token),
        )

    def enviar_respuesta_invitacion(self, referente, invitacion, aceptada):
        """Aviso al Referente de que una invitación fue aceptada o rechazada (RF13 CA1)."""
        accion = "aceptó" if aceptada else "rechazó"
        return self._enviar(
            referente.correo, f"{invitacion.correo} {accion} la invitación",
            "invitacion_respondida",
            nombre=referente.nombre, invitado=invitacion.correo, aceptada=aceptada,
            organizacion=invitacion.organizacion.nombre,
            enlace=self._enlace_organizacion(invitacion.organizacion),
        )

    def enviar_aviso_desvinculacion(self, usuario, organizacion, desactivada=False):
        """Aviso a quien fue desvinculado de una organización (RF14 CA1).

        Args:
            desactivada: True si la cuenta quedó desactivada por no tener aseguradora (RN39).
        """
        return self._enviar(
            usuario.correo, f"Ya no sos miembro de {organizacion.nombre}", "desvinculacion",
            nombre=usuario.nombre, organizacion=organizacion.nombre, desactivada=desactivada,
        )

    def enviar_aviso_cambio_referente(self, usuario, organizacion, es_nuevo, nuevo_referente):
        """Aviso del cambio de Referente al designado y al anterior (RF15 CA2)."""
        asunto = (
            f"Ahora sos Referente de {organizacion.nombre}" if es_nuevo
            else f"Cambió el Referente de {organizacion.nombre}"
        )
        return self._enviar(
            usuario.correo, asunto, "cambio_referente",
            nombre=usuario.nombre, organizacion=organizacion.nombre, es_nuevo=es_nuevo,
            nuevo_referente=f"{nuevo_referente.nombre} {nuevo_referente.apellido}",
            enlace=self._enlace_organizacion(organizacion),
        )

    def enviar_aviso_abandono(self, referente, organizacion, miembro):
        """Aviso al Referente de que un miembro abandonó la organización (RF17 CA1)."""
        return self._enviar(
            referente.correo, f"{miembro.nombre} {miembro.apellido} abandonó {organizacion.nombre}",
            "abandono",
            nombre=referente.nombre, organizacion=organizacion.nombre,
            miembro=f"{miembro.nombre} {miembro.apellido}",
            enlace=self._enlace_organizacion(organizacion),
        )

    def enviar_aviso_eliminacion_organizacion(
        self, usuario, nombre_organizacion, desactivada=False
    ):
        """Aviso a cada miembro de que la organización fue eliminada (RF18 CA2)."""
        return self._enviar(
            usuario.correo, f"Se eliminó la organización {nombre_organizacion}",
            "organizacion_eliminada",
            nombre=usuario.nombre, organizacion=nombre_organizacion, desactivada=desactivada,
        )

    # --- Aseguradoras (funcionalidad 021) ---

    def enviar_aviso_aseguradora_aprobada(self, usuario, organizacion):
        """Aviso al Referente de que el Administrador aprobó su aseguradora (CA8 de la 021)."""
        return self._enviar(
            usuario.correo, f"{organizacion.nombre} ya está aprobada", "aseguradora_aprobada",
            nombre=usuario.nombre, organizacion=organizacion.nombre,
            enlace=self._enlace_organizacion(organizacion),
        )

    def enviar_aviso_aseguradora_rechazada(self, usuario, nombre_organizacion, motivo):
        """Aviso al Referente de que su aseguradora fue rechazada, con el motivo (CA9)."""
        return self._enviar(
            usuario.correo, f"No se aprobó el registro de {nombre_organizacion}",
            "aseguradora_rechazada",
            nombre=usuario.nombre, organizacion=nombre_organizacion, motivo=motivo,
        )
