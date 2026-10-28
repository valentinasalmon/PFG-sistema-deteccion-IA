"""Registro, verificación de correo y recuperación de contraseña.

Cada operación queda registrada en la auditoría junto con su resultado. Las
entradas de las operaciones que cambian datos se confirman en la misma
transacción que el cambio, y los correos se envían después de confirmar.

Desde la funcionalidad 021, el perfil Aseguradora solo se obtiene
registrando una aseguradora del catálogo de la SSN o con la invitación de
una aseguradora (RN36).

Realiza: RF01, RF02, RF05; RN01, RN02, RN03, RN36; RNF01 (CA5), RNF08 (CA1);
RNF06 y CA7 a CA9 de la funcionalidad 003; CA3 a CA5 y CA10 a CA12 de la 021;
RF52 (CA1, CA2) de la 027.
"""
import secrets

from app.modelos.usuario import (
    PERFIL_ABOGADO,
    PERFIL_ASEGURADORA,
    ROL_ADMINISTRADOR,
    ROL_USUARIO,
    Usuario,
)
from app.servicios import auditoria, contrasenias
from app.servicios.errores import ErrorValidacion, NoEncontrado, TokenInvalido
from app.servicios.tokens import (
    PROPOSITO_RECUPERACION,
    PROPOSITO_VERIFICACION,
    huella_contrasenia,
)
from app.utilidades.tiempo import ahora_utc


class ServicioCuentas:  # pylint: disable=too-many-instance-attributes
    """Ciclo de vida de una cuenta antes de iniciar sesión."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, correos, tokens, configuracion, registro,
        organizaciones=None, catalogo=None,
    ):
        """
        Args:
            registro: ``ServicioAuditoria`` donde se registra cada operación.
            organizaciones: ``ServicioOrganizaciones``, para registrar una
                aseguradora o sumarse con una invitación.
            catalogo: ``CatalogoAseguradoras`` de la SSN.
        """
        self.repositorio = repositorio
        self.correos = correos
        self.tokens = tokens
        self.configuracion = configuracion
        self.registro = registro
        self.organizaciones = organizaciones
        self.catalogo = catalogo

    def _origen_aseguradora(self, solicitud):
        """Valida de dónde sale el perfil Aseguradora (RN36).

        Returns:
            ``(invitacion, aseguradora)``: la invitación usada para registrarse
            o la aseguradora elegida del catálogo; ambas pueden ser None.
        """
        invitacion = None
        if solicitud.token_invitacion:
            invitacion = self.organizaciones.invitacion_para_registro(
                solicitud.token_invitacion, solicitud.correo
            )
            if invitacion.organizacion.es_aseguradora:
                solicitud.perfil = PERFIL_ASEGURADORA
                solicitud.empresa = invitacion.organizacion.nombre
                return invitacion, None
        if solicitud.perfil != PERFIL_ASEGURADORA:
            return invitacion, None
        aseguradora = (
            self.catalogo.obtener(solicitud.id_aseguradora)
            if solicitud.id_aseguradora is not None else None
        )
        if aseguradora is None:
            mensaje = "Elegí tu aseguradora del listado de la Superintendencia de Seguros."
            raise ErrorValidacion(mensaje, {"id_aseguradora": mensaje})
        self.organizaciones.exigir_aseguradora_libre(aseguradora)
        solicitud.empresa = aseguradora.denominacion
        return invitacion, aseguradora

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
        _, aseguradora = self._origen_aseguradora(solicitud)
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
        if aseguradora is not None:
            self.organizaciones.crear_aseguradora(usuario, aseguradora)
        self.repositorio.guardar(usuario)
        self._enviar_verificacion(usuario)

    def _hash_inutilizable(self):
        """Hash de una contraseña aleatoria que nadie conoce.

        Las cuentas creadas o vinculadas con Google no tienen contraseña
        propia; si la persona quiere una, la define con "¿Olvidaste tu
        contraseña?", que demuestra el acceso al correo.
        """
        return contrasenias.generar_hash(
            secrets.token_urlsafe(32), self.configuracion["BCRYPT_COSTO"]
        )

    def registrar_con_google(self, solicitud, identidad):
        """Crea una cuenta ya verificada con los datos de Google y los que completa la persona.

        Google ya verificó el correo, así que no se envía la verificación
        (RF52 CA1). El perfil, la institución y la aceptación de los Términos
        los completa la persona, igual que en el registro común (RN01, RN36).

        Args:
            solicitud: ``SolicitudRegistroGoogle`` ya validada.
            identidad: diccionario con ``sub`` y ``correo`` de Google.

        Raises:
            ErrorValidacion: si el correo ya tiene una cuenta o falta la aseguradora.
        """
        solicitud = solicitud.model_copy(update={"correo": identidad["correo"]})
        _, aseguradora = self._origen_aseguradora(solicitud)
        if self.repositorio.obtener_por_correo(solicitud.correo) is not None:
            raise ErrorValidacion(
                "Ya existe una cuenta con ese correo. Volvé a ingresar con Google.",
                codigo="correo_existente",
            )
        ahora = ahora_utc()
        usuario = Usuario(
            nombre=solicitud.nombre,
            apellido=solicitud.apellido,
            correo=solicitud.correo,
            hash_contrasenia=self._hash_inutilizable(),
            perfil=solicitud.perfil,
            colegio=(solicitud.colegio or None) if solicitud.perfil == PERFIL_ABOGADO else None,
            empresa=(solicitud.empresa or None) if solicitud.perfil == PERFIL_ASEGURADORA else None,
            version_terminos=self.configuracion["VERSION_TERMINOS"],
            aceptacion_terminos_en=ahora,
            correo_verificado_en=ahora,
            google_sub=identidad["sub"],
        )
        self.repositorio.preparar(usuario)
        self.registro.registrar(
            auditoria.CUENTA_REGISTRO, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
            detalle={
                "perfil": usuario.perfil, "version_terminos": usuario.version_terminos,
                "metodo": "google",
            },
        )
        if aseguradora is not None:
            self.organizaciones.crear_aseguradora(usuario, aseguradora)
        incorporaciones = (
            self.organizaciones.incorporar_al_verificar(usuario) if self.organizaciones else []
        )
        self.repositorio.guardar(usuario)
        if incorporaciones:
            self.organizaciones.avisar_incorporaciones(incorporaciones)
        return usuario

    def vincular_google(self, usuario, sub):
        """Vincula la cuenta de Google a una cuenta existente con el mismo correo (RF52 CA2).

        Solo se llama si Google informa el correo como verificado. Si la cuenta
        todavía no estaba verificada, queda verificada y su contraseña se
        reemplaza por una aleatoria, y se cierran sus sesiones: así nadie que
        la haya registrado antes con ese correo ajeno conserva el acceso.
        """
        usuario.google_sub = sub
        sin_verificar = not usuario.verificado
        if sin_verificar:
            usuario.correo_verificado_en = ahora_utc()
            usuario.hash_contrasenia = self._hash_inutilizable()
            usuario.version_sesion += 1
        self.registro.registrar(
            auditoria.CUENTA_VINCULACION_GOOGLE, auditoria.EXITOSO,
            usuario=usuario, recurso=usuario,
            detalle={"correo_verificado": sin_verificar, "contrasenia_anulada": sin_verificar},
        )
        incorporaciones = (
            self.organizaciones.incorporar_al_verificar(usuario)
            if sin_verificar and self.organizaciones else []
        )
        self.repositorio.guardar(usuario)
        if incorporaciones:
            self.organizaciones.avisar_incorporaciones(incorporaciones)

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
        incorporaciones = (
            self.organizaciones.incorporar_al_verificar(usuario) if self.organizaciones else []
        )
        self.repositorio.guardar(usuario)
        if incorporaciones:
            self.organizaciones.avisar_incorporaciones(incorporaciones)

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

    def preparar_cuenta_de_prueba(  # pylint: disable=too-many-arguments
        self, correo, contrasenia, *, administradora=True, nombre=("Valentina", "Prueba"),
        estudio="Estudio de prueba evidentIA",
    ):
        """Deja lista una cuenta para recorrer las pantallas (022 y 028).

        Crea, o restablece si ya existe, una cuenta Abogado verificada, activa y
        sin bloqueos, y le crea un estudio jurídico si no tiene ninguna
        organización. Solo se usa desde la terminal:

        - ``flask administracion cuenta-de-prueba``: con rol de Administrador,
          para desarrollo; se rechaza en producción.
        - ``flask administracion cuenta-de-demostracion``: abogada sin rol de
          Administrador, para mostrar la plataforma (028); la contraseña se
          escribe en la terminal y debe cumplir la política.

        Returns:
            La cuenta preparada.
        """
        usuario = self.repositorio.obtener_por_correo(correo.lower())
        if usuario is None:
            usuario = Usuario(
                nombre=nombre[0], apellido=nombre[1], correo=correo.lower(),
                hash_contrasenia="", perfil=PERFIL_ABOGADO, colegio="CPACF",
                version_terminos=self.configuracion["VERSION_TERMINOS"],
                aceptacion_terminos_en=ahora_utc(),
            )
            self.repositorio.preparar(usuario)
        usuario.hash_contrasenia = contrasenias.generar_hash(
            contrasenia, self.configuracion["BCRYPT_COSTO"]
        )
        usuario.correo_verificado_en = usuario.correo_verificado_en or ahora_utc()
        usuario.intentos_fallidos, usuario.bloqueado_hasta = 0, None
        usuario.activo = True
        usuario.rol = ROL_ADMINISTRADOR if administradora else ROL_USUARIO
        self.repositorio.guardar(usuario)
        if not self.organizaciones.listar(usuario):
            self.organizaciones.crear(usuario, {"nombre": estudio, "tipo": "estudio_juridico"})
        return usuario

    def promover_administrador(self, correo):
        """Da el rol de Administrador a una cuenta verificada (funcionalidad 021).

        Solo se usa desde la terminal del servidor (``flask administracion
        promover``): la interfaz nunca ofrece crear administradores.

        Raises:
            NoEncontrado: si no hay una cuenta verificada con ese correo.
        """
        usuario = self.repositorio.obtener_por_correo(correo)
        if usuario is None or not usuario.verificado:
            raise NoEncontrado("No hay una cuenta verificada con ese correo.")
        if usuario.rol != ROL_ADMINISTRADOR:
            usuario.rol = ROL_ADMINISTRADOR
            self.registro.registrar(
                auditoria.CUENTA_PROMOCION_ADMINISTRADOR, auditoria.EXITOSO, recurso=usuario,
                detalle={"origen": "terminal"},
            )
            self.repositorio.guardar(usuario)
        return usuario
