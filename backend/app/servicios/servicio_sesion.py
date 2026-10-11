"""Autenticación con bloqueo por intentos fallidos.

Realiza: RF03 (CA1, CA2, CA3); RNF01 (CA3).
"""
from functools import lru_cache

from app.servicios import contrasenias
from app.servicios.errores import CredencialesInvalidas, CuentaNoVerificada
from app.utilidades.tiempo import ahora_utc

MENSAJE_CREDENCIALES = "El correo o la contraseña no son correctos."


@lru_cache(maxsize=4)
def _hash_ficticio(costo):
    """Hash de relleno para que un correo inexistente tarde lo mismo que uno real."""
    return contrasenias.generar_hash("contrasenia-ficticia-1", costo)


class ServicioSesion:
    """Valida credenciales y mantiene el contador de intentos fallidos."""

    def __init__(self, repositorio, correos, configuracion):
        self.repositorio = repositorio
        self.correos = correos
        self.configuracion = configuracion

    def autenticar(self, correo, contrasenia):
        """Devuelve el usuario si las credenciales son válidas.

        El mensaje de error es el mismo si el correo no existe, si la
        contraseña es incorrecta o si la cuenta está bloqueada, para no
        revelar qué cuentas existen (RF03 CA2).

        Raises:
            CredencialesInvalidas: credenciales incorrectas o cuenta bloqueada.
            CuentaNoVerificada: la contraseña es correcta pero falta verificar el correo.
        """
        usuario = self.repositorio.obtener_por_correo(correo)
        if usuario is None:
            contrasenias.verificar(contrasenia, _hash_ficticio(self.configuracion["BCRYPT_COSTO"]))
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)

        if usuario.bloqueado_hasta is not None and usuario.bloqueado_hasta > ahora_utc():
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)

        if not contrasenias.verificar(contrasenia, usuario.hash_contrasenia):
            self._registrar_intento_fallido(usuario)
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)

        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        self.repositorio.guardar(usuario)

        if not usuario.verificado:
            raise CuentaNoVerificada(
                "Tenés que verificar tu correo antes de iniciar sesión. "
                "Podés pedir que te reenviemos el enlace."
            )
        return usuario

    def _registrar_intento_fallido(self, usuario):
        """Suma un intento fallido y bloquea la cuenta al llegar al límite (RNF01 CA3)."""
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= self.configuracion["INTENTOS_ANTES_DE_BLOQUEO"]:
            duracion = self.configuracion["DURACION_BLOQUEO"]
            usuario.bloqueado_hasta = ahora_utc() + duracion
            usuario.intentos_fallidos = 0
            self.repositorio.guardar(usuario)
            self.correos.enviar_aviso_bloqueo(usuario, int(duracion.total_seconds() // 60))
        else:
            self.repositorio.guardar(usuario)

    def obtener_usuario_de_sesion(self, identificador):
        """Recupera el usuario a partir del identificador guardado en la sesión.

        El identificador tiene la forma ``"id:version_sesion"``. Si la versión
        ya no coincide (por ejemplo, porque se restableció la contraseña), la
        sesión deja de ser válida (CA14).
        """
        try:
            id_texto, version_texto = identificador.split(":")
            usuario = self.repositorio.obtener_por_id(int(id_texto))
        except (ValueError, AttributeError):
            return None
        if usuario is None or str(usuario.version_sesion) != version_texto:
            return None
        return usuario
