"""Tokens firmados con vencimiento para los enlaces enviados por correo.

Se usan con itsdangerous, sin guardar nada en la base de datos. Cada token
incluye un dato que cambia cuando se usa, y eso lo vuelve de un solo uso
(RNF01 CA5):

- Verificación: deja de servir cuando la cuenta ya está verificada.
- Recuperación: incluye una huella del hash de la contraseña; al cambiarla,
  el token deja de coincidir.
- Cambio de correo: incluye el correo actual; al cambiarlo, deja de coincidir.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.servicios.errores import TokenInvalido

PROPOSITO_VERIFICACION = "verificacion-correo"
PROPOSITO_RECUPERACION = "recuperacion-contrasenia"
PROPOSITO_CAMBIO_CORREO = "cambio-correo"


class GestorTokens:
    """Genera y valida tokens con la clave secreta de la aplicación."""

    def __init__(self, clave_secreta):
        self._serializador = URLSafeTimedSerializer(clave_secreta)

    def generar(self, proposito, datos):
        """Firma ``datos`` para el propósito indicado (el propósito actúa como sal)."""
        return self._serializador.dumps(datos, salt=proposito)

    def leer(self, proposito, token, vigencia):
        """Valida la firma y el vencimiento y devuelve los datos.

        Args:
            vigencia: ``timedelta`` con la antigüedad máxima admitida.

        Raises:
            TokenInvalido: si el token está vencido o fue alterado.
        """
        try:
            return self._serializador.loads(
                token, salt=proposito, max_age=int(vigencia.total_seconds())
            )
        except SignatureExpired as error:
            raise TokenInvalido("El enlace venció. Solicitá uno nuevo.", "vencido") from error
        except BadSignature as error:
            raise TokenInvalido(
                "El enlace no es válido. Solicitá uno nuevo.", "alterado"
            ) from error


def huella_contrasenia(hash_contrasenia):
    """Fragmento del hash que cambia cada vez que cambia la contraseña."""
    return hash_contrasenia[-12:]
