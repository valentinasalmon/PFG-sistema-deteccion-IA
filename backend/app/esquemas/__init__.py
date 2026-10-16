"""Validación de los datos que recibe la API (RNF04 CA1).

Los esquemas se definen con pydantic. ``validar`` traduce los errores de
pydantic, que están en inglés, a mensajes en español por campo.
"""
from pydantic import ValidationError

from app.servicios.errores import ErrorValidacion

MENSAJES_POR_TIPO = {
    "missing": "Este campo es obligatorio.",
    "string_type": "Este campo debe ser un texto.",
    "string_too_short": "Este campo no puede estar vacío.",
    "string_too_long": "El texto es demasiado largo.",
    "literal_error": "El valor elegido no es válido.",
    "bool_type": "El valor no es válido.",
    "bool_parsing": "El valor no es válido.",
    "extra_forbidden": "Este campo no está permitido.",
}
CAMPOS_CORREO = {"correo", "correo_nuevo"}


def _mensaje(error):
    campo = str(error["loc"][0]) if error["loc"] else ""
    if error["type"] == "value_error":
        if campo in CAMPOS_CORREO:
            return "El correo electrónico no es válido."
        return error["msg"].removeprefix("Value error, ")
    return MENSAJES_POR_TIPO.get(error["type"], "El valor no es válido.")


def validar(esquema, datos):
    """Valida ``datos`` con el esquema pydantic indicado.

    Returns:
        La instancia del esquema con los datos limpios.

    Raises:
        ErrorValidacion: con un mensaje en español por cada campo inválido.
    """
    try:
        return esquema.model_validate(datos or {})
    except ValidationError as error:
        errores = {}
        for detalle in error.errors():
            campo = str(detalle["loc"][0]) if detalle["loc"] else "general"
            errores.setdefault(campo, _mensaje(detalle))
        raise ErrorValidacion("Revisá los datos marcados.", errores) from error
