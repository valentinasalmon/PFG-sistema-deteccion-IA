"""Gestión del perfil propio: datos personales, contraseña y correo.

Cada operación queda registrada en la auditoría; la edición del perfil
guarda el valor anterior y el nuevo de cada campo modificado.

Realiza: RF06, RF07; RN01, RN02, RN04; RNF06 y CA10 a CA12 de la
funcionalidad 003.
"""
from app.modelos.usuario import PERFIL_ABOGADO, PERFIL_ASEGURADORA
from app.servicios import auditoria, contrasenias
from app.servicios.errores import ConflictoDatos, ErrorValidacion, TokenInvalido
from app.servicios.tokens import PROPOSITO_CAMBIO_CORREO


class ServicioPerfil:
    """Operaciones que una persona realiza sobre su propia cuenta."""

    def __init__(self, repositorio, correos, tokens, configuracion, registro):
        """
        Args:
            registro: ``ServicioAuditoria`` donde se registra cada operación.
        """
        self.registro = registro
        self.repositorio = repositorio
        self.correos = correos
        self.tokens = tokens
        self.configuracion = configuracion

    def _rechazar_edicion(self, usuario, motivo, campo, mensaje):
        """Registra la edición rechazada y lanza el error de validación."""
        self.registro.registrar(
            auditoria.PERFIL_EDICION, auditoria.RECHAZADO, usuario=usuario, recurso=usuario,
            detalle={"motivo": motivo, "campo": campo}, confirmar=True,
        )
        raise ErrorValidacion(mensaje, {campo: mensaje})

    def actualizar_datos(self, usuario, cambios):
        """Modifica nombre, apellido y colegio o empresa (RF07 CA1).

        Args:
            cambios: diccionario solo con los campos enviados.

        Raises:
            ErrorValidacion: si se intenta cambiar el perfil (RN01, RF07 CA4) o
                un dato que no corresponde al perfil.
        """
        if "perfil" in cambios:
            self._rechazar_edicion(
                usuario, "cambio_de_perfil", "perfil",
                "El perfil no puede modificarse después del registro.",
            )
        if "colegio" in cambios and usuario.perfil != PERFIL_ABOGADO:
            self._rechazar_edicion(
                usuario, "dato_de_otro_perfil", "colegio",
                "El colegio de abogados solo corresponde al perfil Abogado.",
            )
        if "empresa" in cambios and usuario.perfil != PERFIL_ASEGURADORA:
            self._rechazar_edicion(
                usuario, "dato_de_otro_perfil", "empresa",
                "La empresa solo corresponde al perfil Aseguradora.",
            )

        modificados = {}
        for campo in ("nombre", "apellido", "colegio", "empresa"):
            if campo not in cambios:
                continue
            # Un texto vacío borra el dato opcional.
            nuevo = cambios[campo] if campo in ("nombre", "apellido") else cambios[campo] or None
            anterior = getattr(usuario, campo)
            if nuevo != anterior:
                modificados[campo] = {"anterior": anterior, "nuevo": nuevo}
                setattr(usuario, campo, nuevo)
        if modificados:
            self.registro.registrar(
                auditoria.PERFIL_EDICION, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
                detalle={"cambios": modificados},
            )
        return self.repositorio.guardar(usuario)

    def _exigir_contrasenia(self, usuario, contrasenia, campo, accion):
        """Verifica la contraseña actual; si no coincide, registra el intento fallido."""
        if not contrasenias.verificar(contrasenia, usuario.hash_contrasenia):
            self.registro.registrar(
                accion, auditoria.FALLIDO, usuario=usuario, recurso=usuario,
                detalle={"motivo": "contrasenia_incorrecta"}, confirmar=True,
            )
            mensaje = "La contraseña actual no es correcta."
            raise ErrorValidacion(mensaje, {campo: mensaje})

    def cambiar_contrasenia(self, usuario, actual, nueva):
        """Cambia la contraseña verificando la actual (RF06) y avisa por correo.

        Incrementa la versión de sesión: las sesiones abiertas en otros
        dispositivos dejan de valer. La ruta renueva la sesión actual para
        que quien hizo el cambio no tenga que volver a ingresar.
        """
        self._exigir_contrasenia(
            usuario, actual, "contrasenia_actual", auditoria.CONTRASENIA_CAMBIO
        )
        contrasenias.validar_politica(nueva, campo="contrasenia_nueva")
        if actual == nueva:
            mensaje = "La contraseña nueva debe ser distinta de la actual."
            raise ErrorValidacion(mensaje, {"contrasenia_nueva": mensaje})
        usuario.hash_contrasenia = contrasenias.generar_hash(
            nueva, self.configuracion["BCRYPT_COSTO"]
        )
        usuario.version_sesion += 1
        self.registro.registrar(
            auditoria.CONTRASENIA_CAMBIO, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
            detalle={"otras_sesiones_cerradas": True},
        )
        self.repositorio.guardar(usuario)
        self.correos.enviar_aviso_contrasenia_cambiada(usuario)
        return usuario

    def solicitar_cambio_correo(self, usuario, correo_nuevo, contrasenia):
        """Envía el enlace de confirmación a la dirección nueva (RF07 CA2).

        Pide la contraseña para que nadie con una sesión ajena abierta pueda
        apoderarse de la cuenta cambiando el correo.
        """
        self._exigir_contrasenia(
            usuario, contrasenia, "contrasenia", auditoria.CORREO_SOLICITUD_CAMBIO
        )
        correo_nuevo = correo_nuevo.lower()
        if correo_nuevo == usuario.correo:
            mensaje = "El correo nuevo es igual al actual."
            raise ErrorValidacion(mensaje, {"correo_nuevo": mensaje})
        detalle = {"anterior": usuario.correo, "nuevo": correo_nuevo}
        if self.repositorio.existe_correo(correo_nuevo):
            self.registro.registrar(
                auditoria.CORREO_SOLICITUD_CAMBIO, auditoria.RECHAZADO, usuario=usuario,
                recurso=usuario, detalle={**detalle, "motivo": "correo_en_uso"}, confirmar=True,
            )
            mensaje = "Ese correo ya está en uso."
            raise ConflictoDatos(mensaje, {"correo_nuevo": mensaje})
        self.registro.registrar(
            auditoria.CORREO_SOLICITUD_CAMBIO, auditoria.EXITOSO, usuario=usuario,
            recurso=usuario, detalle=detalle, confirmar=True,
        )
        token = self.tokens.generar(
            PROPOSITO_CAMBIO_CORREO,
            {"id": usuario.id, "correo_actual": usuario.correo, "correo_nuevo": correo_nuevo},
        )
        self.correos.enviar_confirmacion_cambio_correo(usuario, correo_nuevo, token)
        self.correos.enviar_aviso_cambio_correo(usuario, correo_nuevo)

    def confirmar_cambio_correo(self, token):
        """Aplica el cambio de correo al abrir el enlace enviado a la dirección nueva."""
        try:
            datos = self.tokens.leer(
                PROPOSITO_CAMBIO_CORREO, token, self.configuracion["VIGENCIA_TOKEN_CAMBIO_CORREO"]
            )
            usuario = self.repositorio.obtener_por_id(datos["id"])
            if usuario is None or usuario.correo != datos["correo_actual"]:
                raise TokenInvalido("Este enlace ya fue utilizado o no es válido.")
        except TokenInvalido as error:
            self.registro.registrar(
                auditoria.CORREO_CAMBIO, auditoria.FALLIDO,
                detalle={"motivo": error.motivo}, confirmar=True,
            )
            raise
        detalle = {"anterior": usuario.correo, "nuevo": datos["correo_nuevo"]}
        if self.repositorio.existe_correo(datos["correo_nuevo"]):
            self.registro.registrar(
                auditoria.CORREO_CAMBIO, auditoria.RECHAZADO, usuario=usuario, recurso=usuario,
                detalle={**detalle, "motivo": "correo_en_uso"}, confirmar=True,
            )
            raise ConflictoDatos("Ese correo ya está en uso.")
        usuario.correo = datos["correo_nuevo"]
        self.registro.registrar(
            auditoria.CORREO_CAMBIO, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
            detalle=detalle,
        )
        self.repositorio.guardar(usuario)
