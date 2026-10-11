"""Gestión del perfil propio: datos personales, contraseña y correo.

Realiza: RF06, RF07; RN01, RN02, RN04.
"""
from app.modelos.usuario import PERFIL_ABOGADO, PERFIL_ASEGURADORA
from app.servicios import contrasenias
from app.servicios.errores import ConflictoDatos, ErrorValidacion, TokenInvalido
from app.servicios.tokens import PROPOSITO_CAMBIO_CORREO


class ServicioPerfil:
    """Operaciones que una persona realiza sobre su propia cuenta."""

    def __init__(self, repositorio, correos, tokens, configuracion):
        self.repositorio = repositorio
        self.correos = correos
        self.tokens = tokens
        self.configuracion = configuracion

    def actualizar_datos(self, usuario, cambios):
        """Modifica nombre, apellido y colegio o empresa (RF07 CA1).

        Args:
            cambios: diccionario solo con los campos enviados.

        Raises:
            ErrorValidacion: si se intenta cambiar el perfil (RN01, RF07 CA4) o
                un dato que no corresponde al perfil.
        """
        if "perfil" in cambios:
            mensaje = "El perfil no puede modificarse después del registro."
            raise ErrorValidacion(mensaje, {"perfil": mensaje})
        if "colegio" in cambios and usuario.perfil != PERFIL_ABOGADO:
            mensaje = "El colegio de abogados solo corresponde al perfil Abogado."
            raise ErrorValidacion(mensaje, {"colegio": mensaje})
        if "empresa" in cambios and usuario.perfil != PERFIL_ASEGURADORA:
            mensaje = "La empresa solo corresponde al perfil Aseguradora."
            raise ErrorValidacion(mensaje, {"empresa": mensaje})

        for campo in ("nombre", "apellido"):
            if campo in cambios:
                setattr(usuario, campo, cambios[campo])
        for campo in ("colegio", "empresa"):
            if campo in cambios:
                # Un texto vacío borra el dato opcional.
                setattr(usuario, campo, cambios[campo] or None)
        return self.repositorio.guardar(usuario)

    def _exigir_contrasenia(self, usuario, contrasenia, campo):
        if not contrasenias.verificar(contrasenia, usuario.hash_contrasenia):
            mensaje = "La contraseña actual no es correcta."
            raise ErrorValidacion(mensaje, {campo: mensaje})

    def cambiar_contrasenia(self, usuario, actual, nueva):
        """Cambia la contraseña verificando la actual (RF06) y avisa por correo.

        Incrementa la versión de sesión: las sesiones abiertas en otros
        dispositivos dejan de valer. La ruta renueva la sesión actual para
        que quien hizo el cambio no tenga que volver a ingresar.
        """
        self._exigir_contrasenia(usuario, actual, "contrasenia_actual")
        contrasenias.validar_politica(nueva, campo="contrasenia_nueva")
        if actual == nueva:
            mensaje = "La contraseña nueva debe ser distinta de la actual."
            raise ErrorValidacion(mensaje, {"contrasenia_nueva": mensaje})
        usuario.hash_contrasenia = contrasenias.generar_hash(
            nueva, self.configuracion["BCRYPT_COSTO"]
        )
        usuario.version_sesion += 1
        self.repositorio.guardar(usuario)
        self.correos.enviar_aviso_contrasenia_cambiada(usuario)
        return usuario

    def solicitar_cambio_correo(self, usuario, correo_nuevo, contrasenia):
        """Envía el enlace de confirmación a la dirección nueva (RF07 CA2).

        Pide la contraseña para que nadie con una sesión ajena abierta pueda
        apoderarse de la cuenta cambiando el correo.
        """
        self._exigir_contrasenia(usuario, contrasenia, "contrasenia")
        correo_nuevo = correo_nuevo.lower()
        if correo_nuevo == usuario.correo:
            mensaje = "El correo nuevo es igual al actual."
            raise ErrorValidacion(mensaje, {"correo_nuevo": mensaje})
        if self.repositorio.existe_correo(correo_nuevo):
            mensaje = "Ese correo ya está en uso."
            raise ConflictoDatos(mensaje, {"correo_nuevo": mensaje})
        token = self.tokens.generar(
            PROPOSITO_CAMBIO_CORREO,
            {"id": usuario.id, "correo_actual": usuario.correo, "correo_nuevo": correo_nuevo},
        )
        self.correos.enviar_confirmacion_cambio_correo(usuario, correo_nuevo, token)
        self.correos.enviar_aviso_cambio_correo(usuario, correo_nuevo)

    def confirmar_cambio_correo(self, token):
        """Aplica el cambio de correo al abrir el enlace enviado a la dirección nueva."""
        datos = self.tokens.leer(
            PROPOSITO_CAMBIO_CORREO, token, self.configuracion["VIGENCIA_TOKEN_CAMBIO_CORREO"]
        )
        usuario = self.repositorio.obtener_por_id(datos["id"])
        if usuario is None or usuario.correo != datos["correo_actual"]:
            raise TokenInvalido("Este enlace ya fue utilizado o no es válido.")
        if self.repositorio.existe_correo(datos["correo_nuevo"]):
            raise ConflictoDatos("Ese correo ya está en uso.")
        usuario.correo = datos["correo_nuevo"]
        self.repositorio.guardar(usuario)
