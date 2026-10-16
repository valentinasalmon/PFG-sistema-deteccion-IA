"""Registro, verificación de correo y recuperación de contraseña.

Cada operación queda registrada en la auditoría junto con su resultado. Las
entradas de las operaciones que cambian datos se confirman en la misma
transacción que el cambio, y los correos se envían después de confirmar.

Realiza: RF01, RF02, RF05; RN01, RN02, RN03; RNF01 (CA5), RNF08 (CA1);
RNF06 y CA7 a CA9 de la funcionalidad 003.
"""
from app.modelos.usuario import PERFIL_ABOGADO, PERFIL_ASEGURADORA, Usuario
from app.servicios import auditoria, contrasenias
from app.servicios.errores import TokenInvalido
from app.servicios.tokens import (
    PROPOSITO_RECUPERACION,
    PROPOSITO_VERIFICACION,
    huella_contrasenia,
)
from app.utilidades.tiempo import ahora_utc


class ServicioCuentas:
    """Ciclo de vida de una cuenta antes de iniciar sesión."""

    def __init__(self, repositorio, correos, tokens, configuracion, registro):
        """
        Args:
            registro: ``ServicioAuditoria`` donde se registra cada operación.
        """
        self.repositorio = repositorio
        self.correos = correos
        self.tokens = tokens
        self.configuracion = configuracion
        self.registro = registro

    def registrar(self, solicitud):
        """Crea una cuenta pendiente de verificación y envía el correo de verificación.

        Si el correo ya existe, no revela ese hecho (RF01 CA3): si la cuenta
        no está verificada reenvía la verificación, y si lo está avisa al
        titular. En todos los casos la respuesta al visitante es la misma,
        pero la auditoría registra el intento (CA7 de la 003).

        Args:
            solicitud: ``SolicitudRegistro`` ya validada.
        """
        contrasenias.validar_politica(solicitud.contrasenia)
        existente = self.repositorio.obtener_por_correo(solicitud.correo)
        if existente is not None:
            self.registro.registrar(
                auditoria.CUENTA_REGISTRO, auditoria.RECHAZADO, recurso=existente,
                detalle={"motivo": "correo_existente", "verificada": existente.verificado},
                confirmar=True,
            )
            if existente.verificado:
                self.correos.enviar_aviso_registro_existente(existente)
            else:
                self._enviar_verificacion(existente)
            return

        usuario = Usuario(
            nombre=solicitud.nombre,
            apellido=solicitud.apellido,
            correo=solicitud.correo.lower(),
            hash_contrasenia=contrasenias.generar_hash(
                solicitud.contrasenia, self.configuracion["BCRYPT_COSTO"]
            ),
            perfil=solicitud.perfil,
            colegio=(solicitud.colegio or None) if solicitud.perfil == PERFIL_ABOGADO else None,
            empresa=(solicitud.empresa or None) if solicitud.perfil == PERFIL_ASEGURADORA else None,
            version_terminos=self.configuracion["VERSION_TERMINOS"],
            aceptacion_terminos_en=ahora_utc(),
        )
        self.repositorio.preparar(usuario)
        self.registro.registrar(
            auditoria.CUENTA_REGISTRO, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
            detalle={"perfil": usuario.perfil, "version_terminos": usuario.version_terminos},
        )
        self.repositorio.guardar(usuario)
        self._enviar_verificacion(usuario)

    def _enviar_verificacion(self, usuario):
        token = self.tokens.generar(
            PROPOSITO_VERIFICACION, {"id": usuario.id, "correo": usuario.correo}
        )
        self.correos.enviar_verificacion(usuario, token)

    def _registrar_enlace_invalido(self, accion, error, usuario=None):
        """Registra como fallido el uso de un enlace inválido, con su motivo."""
        self.registro.registrar(
            accion, auditoria.FALLIDO, usuario=usuario, recurso=usuario,
            detalle={"motivo": error.motivo}, confirmar=True,
        )

    def verificar_correo(self, token):
        """Activa la cuenta a partir del enlace de verificación (RF02).

        Raises:
            TokenInvalido: si el enlace venció, fue alterado o ya se usó.
        """
        usuario = None
        try:
            datos = self.tokens.leer(
                PROPOSITO_VERIFICACION, token, self.configuracion["VIGENCIA_TOKEN_VERIFICACION"]
            )
            usuario = self.repositorio.obtener_por_id(datos["id"])
            if usuario is None or usuario.correo != datos["correo"]:
                usuario = None
                raise TokenInvalido("El enlace no es válido. Solicitá uno nuevo.", "no_corresponde")
            if usuario.verificado:
                raise TokenInvalido("Este enlace ya fue utilizado. Tu cuenta ya está verificada.")
        except TokenInvalido as error:
            self._registrar_enlace_invalido(auditoria.CUENTA_VERIFICACION, error, usuario)
            raise
        usuario.correo_verificado_en = ahora_utc()
        self.registro.registrar(
            auditoria.CUENTA_VERIFICACION, auditoria.EXITOSO, usuario=usuario, recurso=usuario
        )
        self.repositorio.guardar(usuario)

    def reenviar_verificacion(self, correo):
        """Reenvía el correo de verificación si la cuenta existe y no está verificada.

        No informa si el correo existe, para no revelar qué cuentas hay, pero
        la auditoría registra el pedido con el correo indicado (CA8 de la 003).
        """
        usuario = self.repositorio.obtener_por_correo(correo)
        if usuario is None or usuario.verificado:
            motivo = "correo_inexistente" if usuario is None else "ya_verificada"
            self.registro.registrar(
                auditoria.CUENTA_REENVIO_VERIFICACION, auditoria.RECHAZADO, recurso=usuario,
                detalle={"motivo": motivo, "correo": correo.strip().lower()}, confirmar=True,
            )
            return
        self.registro.registrar(
            auditoria.CUENTA_REENVIO_VERIFICACION, auditoria.EXITOSO, recurso=usuario,
            detalle={"correo": usuario.correo}, confirmar=True,
        )
        self._enviar_verificacion(usuario)

    def solicitar_recuperacion(self, correo):
        """Envía el enlace de recuperación si el correo existe (RF05 CA1 y CA2).

        Registra la solicitud con el correo indicado, exista o no (CA9 de la 003).
        """
        usuario = self.repositorio.obtener_por_correo(correo)
        if usuario is None:
            self.registro.registrar(
                auditoria.CONTRASENIA_RECUPERACION, auditoria.RECHAZADO,
                detalle={"motivo": "correo_inexistente", "correo": correo.strip().lower()},
                confirmar=True,
            )
            return
        self.registro.registrar(
            auditoria.CONTRASENIA_RECUPERACION, auditoria.EXITOSO, recurso=usuario,
            detalle={"correo": usuario.correo}, confirmar=True,
        )
        token = self.tokens.generar(
            PROPOSITO_RECUPERACION,
            {"id": usuario.id, "huella": huella_contrasenia(usuario.hash_contrasenia)},
        )
        self.correos.enviar_recuperacion(usuario, token)

    def restablecer_contrasenia(self, token, contrasenia_nueva):
        """Define una contraseña nueva a partir del enlace de recuperación (RF05 CA3).

        Además cierra todas las sesiones abiertas, desbloquea la cuenta y,
        como el enlace demuestra el acceso al correo, la deja verificada.

        Raises:
            TokenInvalido: si el enlace venció, fue alterado o ya se usó.
            ErrorValidacion: si la contraseña no cumple la política.
        """
        try:
            datos = self.tokens.leer(
                PROPOSITO_RECUPERACION, token, self.configuracion["VIGENCIA_TOKEN_RECUPERACION"]
            )
            usuario = self.repositorio.obtener_por_id(datos["id"])
            if usuario is None or huella_contrasenia(usuario.hash_contrasenia) != datos["huella"]:
                raise TokenInvalido(
                    "Este enlace ya fue utilizado o no es válido. Solicitá uno nuevo."
                )
        except TokenInvalido as error:
            self._registrar_enlace_invalido(auditoria.CONTRASENIA_RESTABLECIMIENTO, error)
            raise
        contrasenias.validar_politica(contrasenia_nueva)

        usuario.hash_contrasenia = contrasenias.generar_hash(
            contrasenia_nueva, self.configuracion["BCRYPT_COSTO"]
        )
        usuario.version_sesion += 1
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        verificada_ahora = not usuario.verificado
        if verificada_ahora:
            usuario.correo_verificado_en = ahora_utc()
        self.registro.registrar(
            auditoria.CONTRASENIA_RESTABLECIMIENTO, auditoria.EXITOSO,
            usuario=usuario, recurso=usuario,
            detalle={"sesiones_cerradas": True, "correo_verificado": verificada_ahora},
        )
        self.repositorio.guardar(usuario)
        self.correos.enviar_aviso_contrasenia_cambiada(usuario)
