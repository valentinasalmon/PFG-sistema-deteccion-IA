"""Excepciones del dominio.

Los servicios las lanzan sin saber nada de HTTP; la capa de rutas las
traduce a respuestas JSON con el código de estado adecuado.
"""


class ErrorDominio(Exception):
    """Base de los errores de negocio.

    Attributes:
        mensaje: texto en español para mostrar a la persona usuaria.
        codigo: identificador estable para que el frontend distinga el caso;
            puede precisarse al lanzar el error (por ejemplo, ``limite_del_plan``).
        errores: detalle por campo, cuando corresponde.
    """

    codigo = "error"

    def __init__(self, mensaje, errores=None, codigo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.errores = errores or {}
        if codigo is not None:
            self.codigo = codigo


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


class AccesoDenegado(ErrorDominio):
    """La persona pertenece al recurso pero su rol no le permite la operación (403)."""

    codigo = "acceso_denegado"


class NoEncontrado(ErrorDominio):
    """El recurso no existe o la persona no tiene acceso a él (404).

    Se usa la misma respuesta en ambos casos para no revelar qué recursos
    existen (RF16 CA2).
    """

    codigo = "no_encontrado"
