"""Inicio de sesión y registro con Google (funcionalidad 027, ADR-0019).

Decide qué pasa cuando Google devuelve a la persona:

- Si su cuenta de Google ya está vinculada, inicia sesión.
- Si no, pero el correo ya tiene una cuenta y Google lo informa como
  verificado, vincula las cuentas e inicia sesión (RF52 CA2).
- Si el correo no tiene cuenta, la persona completa el perfil (Abogado o
  Aseguradora), la institución y la aceptación de los Términos antes de
  entrar (RF52 CA1). Ese paso es obligatorio la primera vez.

Todo inicio, rechazo, registro y vinculación queda en la auditoría (RF52 CA3).

Realiza: RF52; RN01, RN02, RN36.
"""
import base64
import hashlib
import secrets
from datetime import datetime

from app.integraciones.google import ErrorGoogle
from app.servicios.errores import InicioGoogleRechazado, NoEncontrado
from app.utilidades.tiempo import ahora_utc

MENSAJE_ERROR = "No pudimos ingresar con Google. Probá de nuevo o usá tu correo y contraseña."
MENSAJE_NO_VERIFICADO = (
    "Google no confirmó tu correo electrónico. Verificalo en Google o registrate con "
    "correo y contraseña."
)


def _aleatorio():
    """Texto aleatorio de 256 bits, apto para URL."""
    return secrets.token_urlsafe(32)


def desafio_pkce(verificador):
    """Desafío PKCE (S256) del verificador: SHA-256 en base64 URL sin relleno."""
    resumen = hashlib.sha256(verificador.encode("ascii")).digest()
    return base64.urlsafe_b64encode(resumen).decode("ascii").rstrip("=")


class ServicioGoogle:
    """Orquesta el inicio con Google sobre los servicios de cuentas y de sesión."""

    def __init__(self, cliente, repositorio, cuentas, sesion, configuracion):
        """
        Args:
            cliente: ``ClienteGoogle``, o None si Google no está configurado.
            cuentas: ``ServicioCuentas``, para registrar y vincular cuentas.
            sesion: ``ServicioSesion``, para completar el inicio de sesión.
        """
        self.cliente = cliente
        self.repositorio = repositorio
        self.cuentas = cuentas
        self.sesion = sesion
        self.configuracion = configuracion

    @property
    def habilitado(self):
        """True si la plataforma tiene configurado el cliente de Google."""
        return self.cliente is not None

    def _exigir_habilitado(self):
        if not self.habilitado:
            raise NoEncontrado("El inicio de sesión con Google no está disponible.")

    def preparar_inicio(self):
        """Datos del flujo que se guardan en la sesión y dirección de Google.

        Returns:
            ``(url, flujo)``: ``flujo`` tiene ``estado``, ``nonce`` y
            ``verificador``, que hay que comparar a la vuelta.
        """
        self._exigir_habilitado()
        flujo = {"estado": _aleatorio(), "nonce": _aleatorio(), "verificador": _aleatorio()}
        url = self.cliente.url_autorizacion(
            flujo["estado"], flujo["nonce"], desafio_pkce(flujo["verificador"])
        )
        return url, flujo

    def obtener_identidad(self, flujo, estado, codigo, error_google=None):
        """Valida la vuelta desde Google y devuelve la identidad de la persona.

        Args:
            flujo: lo que devolvió ``preparar_inicio`` (guardado en la sesión).
            estado, codigo, error_google: parámetros ``state``, ``code`` y
                ``error`` que Google agrega a la dirección de vuelta.

        Raises:
            InicioGoogleRechazado: si la persona canceló, el ``state`` no
                coincide, Google rechazó el código o el correo no está verificado.
        """
        self._exigir_habilitado()
        if error_google:
            self.sesion.registrar_rechazo_google("cancelado_en_google")
            raise InicioGoogleRechazado(MENSAJE_ERROR, codigo="google_cancelado")
        if not flujo or not estado or not secrets.compare_digest(
            str(flujo.get("estado", "")), str(estado)
        ):
            self.sesion.registrar_rechazo_google("state_invalido")
            raise InicioGoogleRechazado(MENSAJE_ERROR)
        try:
            identidad = self.cliente.canjear_codigo(codigo, flujo["verificador"], flujo["nonce"])
        except ErrorGoogle as falla:
            self.sesion.registrar_rechazo_google("token_invalido")
            raise InicioGoogleRechazado(MENSAJE_ERROR) from falla
        if not identidad.correo_verificado:
            self.sesion.registrar_rechazo_google("correo_no_verificado", identidad.correo)
            raise InicioGoogleRechazado(MENSAJE_NO_VERIFICADO, codigo="google_no_verificado")
        return identidad

    def ingresar(self, identidad):
        """Inicia sesión con la identidad de Google, si ya hay una cuenta para ella.

        Returns:
            El usuario que inicia sesión, o None si hay que completar el registro.

        Raises:
            CuentaDesactivada: igual que en el inicio con contraseña (RN39).
        """
        usuario = self.repositorio.obtener_por_google(identidad.sub)
        if usuario is None:
            usuario = self.repositorio.obtener_por_correo(identidad.correo)
            if usuario is None:
                return None
            self.cuentas.vincular_google(usuario, identidad.sub)
        return self.sesion.autenticar_con_google(usuario)

    def datos_pendientes(self, identidad, invitacion=None):
        """Lo que se guarda en la sesión mientras la persona completa el registro.

        Args:
            invitacion: token de la invitación con la que llegó la persona, si
                eligió Google desde el enlace de una invitación (021).
        """
        vigencia = self.configuracion["VIGENCIA_REGISTRO_GOOGLE"]
        return {
            "sub": identidad.sub,
            "correo": identidad.correo,
            "nombre": identidad.nombre,
            "apellido": identidad.apellido,
            "invitacion": invitacion,
            "vence": (ahora_utc() + vigencia).isoformat(),
        }

    @staticmethod
    def vigente(pendiente):
        """True si hay un registro con Google pendiente y no venció."""
        if not pendiente:
            return False
        try:
            return datetime.fromisoformat(pendiente["vence"]) > ahora_utc()
        except (KeyError, ValueError):
            return False

    def completar_registro(self, pendiente, solicitud):
        """Crea la cuenta con lo que completó la persona e inicia sesión (RF52 CA1).

        Raises:
            NoEncontrado: si no hay un registro con Google pendiente o venció.
            ErrorValidacion: si faltan datos o el correo ya tiene cuenta.
        """
        if not self.vigente(pendiente):
            raise NoEncontrado(
                "Pasó demasiado tiempo. Volvé a elegir \"Continuar con Google\".",
                codigo="registro_google_vencido",
            )
        usuario = self.cuentas.registrar_con_google(solicitud, pendiente)
        return self.sesion.autenticar_con_google(usuario)
