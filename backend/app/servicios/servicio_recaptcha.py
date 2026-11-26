"""Comprobación de que quien completa un formulario público es una persona (051).

Protege el registro, el inicio de sesión, el pedido de recuperación de la
contraseña y el reenvío del correo de verificación: los formularios que
cualquiera puede enviar sin una sesión y que un robot usaría para crear
cuentas falsas, probar contraseñas o mandar correos a terceros.

Decisiones (bitácora del 2026-11-26):

- Se rechaza si el token falta, no es válido, es de otra acción o su puntaje
  queda por debajo de ``RECAPTCHA_UMBRAL`` (0,5 por defecto, lo que recomienda Google).
- **Si Google no responde, se deja pasar** y se registra en el log: una caída de
  Google no puede impedir que alguien se registre o entre. El inicio de sesión
  sigue protegido por el bloqueo tras intentos fallidos.

Realiza: RNF02 (seguridad); 051.
"""
import logging

from app.integraciones.recaptcha import UMBRAL_POR_DEFECTO, RecaptchaNoDisponible
from app.servicios.errores import VerificacionHumanaFallida

ACCIONES = ("registro", "inicio_sesion", "recuperacion", "reenvio_verificacion")
MENSAJE_RECHAZO = (
    "No pudimos comprobar que seas una persona. Recargá la página e intentá de nuevo."
)

registro_log = logging.getLogger(__name__)


class ServicioRecaptcha:
    """Exige un token de reCAPTCHA válido en los formularios públicos."""

    def __init__(self, verificador, umbral=UMBRAL_POR_DEFECTO):
        self.verificador = verificador
        self.umbral = umbral

    @property
    def activo(self):
        """Si reCAPTCHA está configurado."""
        return self.verificador.activo

    def configuracion_publica(self):
        """Lo que necesita el navegador: si está activo y la clave del sitio (que es pública)."""
        return {
            "habilitado": self.activo,
            "clave_sitio": self.verificador.clave_sitio if self.activo else None,
        }

    def exigir(self, token, accion, ip=None, agente=None):
        """Comprueba el token de la acción.

        Raises:
            VerificacionHumanaFallida: si falta, no es válido, es de otra acción o
                el puntaje es bajo.
        """
        if not self.activo:
            return
        if accion not in ACCIONES:
            raise ValueError(f"Acción de reCAPTCHA desconocida: {accion}")
        if not token:
            raise VerificacionHumanaFallida(MENSAJE_RECHAZO)
        try:
            evaluacion = self.verificador.evaluar(token[:4000], accion, ip, agente)
        except RecaptchaNoDisponible as falla:
            registro_log.warning("reCAPTCHA no respondió; se deja pasar (%s): %s", accion, falla)
            return
        if (
            not evaluacion.valida
            or evaluacion.accion != accion
            or evaluacion.puntaje < self.umbral
        ):
            registro_log.info(
                "reCAPTCHA rechazó %s: válida=%s acción=%s puntaje=%.2f motivo=%s",
                accion, evaluacion.valida, evaluacion.accion, evaluacion.puntaje,
                evaluacion.motivo,
            )
            raise VerificacionHumanaFallida(MENSAJE_RECHAZO)
