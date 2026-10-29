"""Esquemas de entrada y salida de cuentas, sesión y perfil.

Realiza: RNF04 (CA1).
"""
from typing import Annotated, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

from app.modelos.usuario import PERFIL_ABOGADO, PERFIL_ASEGURADORA
from app.servicios.contrasenias import problema_de_politica

TextoCorto = Field(min_length=1, max_length=100)
TextoInstitucion = Field(default=None, max_length=150)
# Las contraseñas se toman tal cual: no se les quitan los espacios.
Contrasenia = Annotated[
    str, StringConstraints(strip_whitespace=False, min_length=1, max_length=128)
]


def _exigir_politica(contrasenia):
    """Aplica la política al validar el formulario, junto con el resto de los campos.

    Así la persona ve todos los problemas de una vez. El servicio vuelve a
    aplicarla, porque la regla pertenece al dominio y no a la API.
    """
    problema = problema_de_politica(contrasenia)
    if problema is not None:
        raise ValueError(problema)
    return contrasenia


class EsquemaBase(BaseModel):
    """Configuración común: quita espacios de los textos (salvo contraseñas) y
    rechaza campos desconocidos."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class SolicitudRegistro(EsquemaBase):
    """Datos del formulario de registro (RF01)."""

    nombre: str = TextoCorto
    apellido: str = TextoCorto
    correo: EmailStr
    contrasenia: Contrasenia
    perfil: Literal["abogado", "aseguradora"]
    colegio: Optional[str] = TextoInstitucion
    empresa: Optional[str] = TextoInstitucion
    acepta_terminos: bool
    # Funcionalidad 021: aseguradora elegida del catálogo de la SSN, o el
    # token de la invitación con la que la persona se suma a una organización.
    id_aseguradora: Optional[int] = None
    token_invitacion: Optional[str] = Field(default=None, max_length=500)

    _politica = field_validator("contrasenia")(_exigir_politica)

    @field_validator("acepta_terminos")
    @classmethod
    def exigir_aceptacion(cls, valor):
        """La aceptación expresa de los términos es obligatoria (RF01 CA2)."""
        if not valor:
            raise ValueError("Tenés que aceptar los Términos de Uso y la Política de Privacidad.")
        return valor


class SolicitudRegistroGoogle(EsquemaBase):
    """Datos que completa quien entra con Google por primera vez (RF52 CA1).

    El correo no se recibe del navegador: lo informa Google y el servicio lo
    toma de la sesión. Tampoco hay contraseña.
    """

    nombre: str = TextoCorto
    apellido: str = TextoCorto
    perfil: Literal["abogado", "aseguradora"]
    colegio: Optional[str] = TextoInstitucion
    empresa: Optional[str] = TextoInstitucion
    acepta_terminos: bool
    id_aseguradora: Optional[int] = None
    token_invitacion: Optional[str] = Field(default=None, max_length=500)
    # Lo completa el servicio con el correo de Google; no se acepta del navegador.
    correo: Optional[str] = None

    @field_validator("correo")
    @classmethod
    def rechazar_correo(cls, valor):
        """El correo siempre es el que informó Google."""
        if valor is not None:
            raise ValueError("El correo es el de tu cuenta de Google y no se puede cambiar.")
        return valor

    @field_validator("acepta_terminos")
    @classmethod
    def exigir_aceptacion(cls, valor):
        """La aceptación expresa de los términos es obligatoria (RF01 CA2)."""
        return SolicitudRegistro.exigir_aceptacion(valor)


class SolicitudInicioSesion(EsquemaBase):
    """Credenciales de inicio de sesión (RF03)."""

    correo: str = Field(min_length=1, max_length=254)
    contrasenia: Contrasenia


class SolicitudCorreo(EsquemaBase):
    """Un correo electrónico (reenvío de verificación, recuperación)."""

    correo: EmailStr


class SolicitudToken(EsquemaBase):
    """Un token recibido en un enlace por correo."""

    token: str = Field(min_length=1, max_length=500)


class SolicitudRestablecimiento(EsquemaBase):
    """Contraseña nueva a partir del enlace de recuperación (RF05)."""

    token: str = Field(min_length=1, max_length=500)
    contrasenia: Contrasenia

    _politica = field_validator("contrasenia")(_exigir_politica)


class SolicitudCambioContrasenia(EsquemaBase):
    """Cambio de contraseña desde el perfil (RF06)."""

    contrasenia_actual: Contrasenia
    contrasenia_nueva: Contrasenia

    _politica = field_validator("contrasenia_nueva")(_exigir_politica)


class SolicitudCambioCorreo(EsquemaBase):
    """Pedido de cambio de correo (RF07 CA2)."""

    correo_nuevo: EmailStr
    contrasenia: Contrasenia


class SolicitudActualizacionPerfil(BaseModel):
    """Datos personales editables (RF07 CA1). Todos son opcionales.

    Admite ``perfil`` solo para poder rechazarlo con un mensaje claro (RF07 CA4).
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(default=None, min_length=1, max_length=100)
    colegio: Optional[str] = TextoInstitucion
    empresa: Optional[str] = TextoInstitucion
    perfil: Optional[str] = None


def usuario_a_dict(usuario):
    """Representación pública del usuario. Nunca incluye el hash de la contraseña.

    ``en_organizacion`` le permite a la interfaz mostrar el menú según
    corresponda (funcionalidad 028).
    """
    datos = {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "correo": usuario.correo,
        "perfil": usuario.perfil,
        "rol": usuario.rol,
        "activo": usuario.activo,
        "en_organizacion": bool(usuario.membresias),
    }
    if usuario.perfil == PERFIL_ABOGADO:
        datos["colegio"] = usuario.colegio
    if usuario.perfil == PERFIL_ASEGURADORA:
        datos["empresa"] = usuario.empresa
    return datos
