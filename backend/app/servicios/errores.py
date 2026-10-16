"""Excepciones del dominio.

Los servicios las lanzan sin saber nada de HTTP; la capa de rutas las
traduce a respuestas JSON con el código de estado adecuado.
"""


class ErrorDominio(Exception):
    """Base de los errores de negocio.

    Attributes:
        mensaje: texto en español para mostrar a la persona usuaria.
        codigo: identificador estable para que el frontend distinga el caso.
        errores: detalle por campo, cuando corresponde.
    """

    codigo = "error"

    def __init__(self, mensaje, errores=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.errores = errores or {}


class ErrorValidacion(ErrorDominio):
    """Los datos recibidos no cumplen las reglas (400)."""

    codigo = "datos_invalidos"


class CredencialesInvalidas(ErrorDominio):
    """Correo o contraseña incorrectos, o cuenta bloqueada (401)."""

    codigo = "credenciales_invalidas"


class CuentaNoVerificada(ErrorDominio):
    """La cuenta existe y la contraseña es correcta, pero falta verificar el correo (403)."""

    codigo = "cuenta_no_verificada"


class TokenInvalido(ErrorDominio):
    """El enlace recibido por correo está vencido, alterado o ya fue usado (400).

    Attributes:
        motivo: ``vencido``, ``alterado`` o ``ya_usado``; se guarda en la
            auditoría y no se muestra a la persona usuaria.
    """

    codigo = "enlace_invalido"

    def __init__(self, mensaje, motivo="ya_usado"):
        super().__init__(mensaje)
        self.motivo = motivo


class ConflictoDatos(ErrorDominio):
    """La operación choca con datos existentes, por ejemplo un correo ya usado (409)."""

    codigo = "conflicto"
