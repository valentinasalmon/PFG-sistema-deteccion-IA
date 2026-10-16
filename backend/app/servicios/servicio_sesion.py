"""Autenticación con bloqueo por intentos fallidos.

Cada intento de inicio de sesión, cada bloqueo y cada cierre de sesión
quedan registrados en la auditoría. La persona sigue viendo el mensaje
genérico; el motivo real del fallo solo queda en la auditoría.

Realiza: RF03 (CA1, CA2, CA3, CA4); RF04; RNF01 (CA3); RNF06 (CA7) y CA3 a
CA6 de la funcionalidad 003.
"""
from functools import lru_cache

from app.servicios import auditoria, contrasenias
from app.servicios.errores import CredencialesInvalidas, CuentaNoVerificada
from app.utilidades.tiempo import ahora_utc

MENSAJE_CREDENCIALES = "El correo o la contraseña no son correctos."

MOTIVO_CIERRE_MANUAL = "manual"
MOTIVO_CIERRE_DURACION_MAXIMA = "duracion_maxima"


@lru_cache(maxsize=4)
def _hash_ficticio(costo):
    """Hash de relleno para que un correo inexistente tarde lo mismo que uno real."""
    return contrasenias.generar_hash("contrasenia-ficticia-1", costo)


class ServicioSesion:
    """Valida credenciales y mantiene el contador de intentos fallidos."""

    def __init__(self, repositorio, correos, configuracion, registro):
        """
        Args:
            registro: ``ServicioAuditoria`` donde se registra cada intento.
        """
        self.repositorio = repositorio
        self.correos = correos
        self.configuracion = configuracion
        self.registro = registro

    def _registrar_fallo(self, motivo, usuario=None, correo=None):
        """Registra un inicio de sesión fallido con su motivo y lo confirma."""
        detalle = {"motivo": motivo}
        if correo is not None:
            detalle["correo_intentado"] = correo
        self.registro.registrar(
            auditoria.SESION_INICIO, auditoria.FALLIDO, usuario=usuario, recurso=usuario,
            detalle=detalle, confirmar=True,
        )

    def autenticar(self, correo, contrasenia):
        """Devuelve el usuario si las credenciales son válidas.

        El mensaje de error es el mismo si el correo no existe, si la
        contraseña es incorrecta o si la cuenta está bloqueada, para no
        revelar qué cuentas existen (RF03 CA2). La auditoría registra el
        motivo y, si el correo no existe, el correo intentado (RNF06 CA7).

        Raises:
            CredencialesInvalidas: credenciales incorrectas o cuenta bloqueada.
            CuentaNoVerificada: la contraseña es correcta pero falta verificar el correo.
        """
        usuario = self.repositorio.obtener_por_correo(correo)
        if usuario is None:
            contrasenias.verificar(contrasenia, _hash_ficticio(self.configuracion["BCRYPT_COSTO"]))
            self._registrar_fallo("correo_inexistente", correo=correo.strip().lower())
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)

        if usuario.bloqueado_hasta is not None and usuario.bloqueado_hasta > ahora_utc():
            self._registrar_fallo("cuenta_bloqueada", usuario)
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)

        if not contrasenias.verificar(contrasenia, usuario.hash_contrasenia):
            self._registrar_intento_fallido(usuario)
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)

        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        if not usuario.verificado:
            self.registro.registrar(
                auditoria.SESION_INICIO, auditoria.FALLIDO, usuario=usuario, recurso=usuario,
                detalle={"motivo": "cuenta_no_verificada"},
            )
            self.repositorio.guardar(usuario)
            raise CuentaNoVerificada(
                "Tenés que verificar tu correo antes de iniciar sesión. "
                "Podés pedir que te reenviemos el enlace."
            )
        self.registro.registrar(
            auditoria.SESION_INICIO, auditoria.EXITOSO, usuario=usuario, recurso=usuario
        )
        self.repositorio.guardar(usuario)
        return usuario

    def _registrar_intento_fallido(self, usuario):
        """Suma un intento fallido y bloquea la cuenta al llegar al límite (RNF01 CA3).

        El intento y, si corresponde, el bloqueo se registran en la auditoría
        en la misma transacción que el contador (CA4 y CA5 de la 003).
        """
        usuario.intentos_fallidos += 1
        self.registro.registrar(
            auditoria.SESION_INICIO, auditoria.FALLIDO, usuario=usuario, recurso=usuario,
            detalle={"motivo": "contrasenia_incorrecta", "intentos": usuario.intentos_fallidos},
        )
        if usuario.intentos_fallidos >= self.configuracion["INTENTOS_ANTES_DE_BLOQUEO"]:
            duracion = self.configuracion["DURACION_BLOQUEO"]
            usuario.bloqueado_hasta = ahora_utc() + duracion
            self.registro.registrar(
                auditoria.CUENTA_BLOQUEO, auditoria.EXITOSO, recurso=usuario,
                detalle={
                    "intentos": usuario.intentos_fallidos,
                    "bloqueado_hasta": usuario.bloqueado_hasta.isoformat(),
                },
            )
            usuario.intentos_fallidos = 0
            self.repositorio.guardar(usuario)
            self.correos.enviar_aviso_bloqueo(usuario, int(duracion.total_seconds() // 60))
        else:
            self.repositorio.guardar(usuario)

    def registrar_cierre(self, usuario, motivo):
        """Registra el cierre de la sesión del usuario (RF04; CA6 de la 003).

        Args:
            motivo: ``MOTIVO_CIERRE_MANUAL`` o ``MOTIVO_CIERRE_DURACION_MAXIMA``.
        """
        self.registro.registrar(
            auditoria.SESION_CIERRE, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
            detalle={"motivo": motivo}, confirmar=True,
        )

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
