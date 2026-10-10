"""Política de contraseñas y hash con bcrypt.

Realiza: RNF01 (CA1 y CA2).
"""
from pathlib import Path

import bcrypt

from app.servicios.errores import ErrorValidacion

LONGITUD_MINIMA = 10
# bcrypt solo procesa los primeros 72 bytes y, desde la versión 5, rechaza
# contraseñas más largas. Se informa como una regla más de la política.
BYTES_MAXIMOS = 72
ARCHIVO_COMUNES = Path(__file__).resolve().parents[2] / "recursos" / "contrasenias_comunes.txt"


def _cargar_contrasenias_comunes():
    """Lee la lista de contraseñas comunes (ignora comentarios y líneas vacías)."""
    lineas = ARCHIVO_COMUNES.read_text(encoding="utf-8").splitlines()
    return {
        linea.strip().lower()
        for linea in lineas
        if linea.strip() and not linea.startswith("#")
    }


CONTRASENIAS_COMUNES = _cargar_contrasenias_comunes()


def problema_de_politica(contrasenia):
    """Devuelve la primera condición de la política que la contraseña no cumple.

    Returns:
        El mensaje en español, o None si la contraseña es válida.
    """
    if len(contrasenia) < LONGITUD_MINIMA:
        return f"La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres."
    if len(contrasenia.encode("utf-8")) > BYTES_MAXIMOS:
        return "La contraseña es demasiado larga: usá como máximo 72 caracteres."
    if not any(caracter.isalpha() for caracter in contrasenia):
        return "La contraseña debe incluir al menos una letra."
    if not any(caracter.isdigit() for caracter in contrasenia):
        return "La contraseña debe incluir al menos un número."
    if contrasenia.lower() in CONTRASENIAS_COMUNES:
        return "Esa contraseña es demasiado común. Elegí otra."
    return None


def validar_politica(contrasenia, campo="contrasenia"):
    """Verifica que la contraseña cumpla la política (RNF01 CA2).

    Raises:
        ErrorValidacion: con la primera condición incumplida.
    """
    problema = problema_de_politica(contrasenia)
    if problema is not None:
        raise ErrorValidacion(problema, {campo: problema})


def generar_hash(contrasenia, costo):
    """Devuelve el hash bcrypt de la contraseña con el costo indicado (RNF01 CA1)."""
    return bcrypt.hashpw(contrasenia.encode("utf-8"), bcrypt.gensalt(rounds=costo)).decode("utf-8")


def verificar(contrasenia, hash_guardado):
    """True si la contraseña corresponde al hash guardado.

    Una contraseña de más de 72 bytes nunca pudo guardarse, así que no
    coincide (y se evita el error que lanzaría bcrypt).
    """
    if len(contrasenia.encode("utf-8")) > BYTES_MAXIMOS:
        return False
    return bcrypt.checkpw(contrasenia.encode("utf-8"), hash_guardado.encode("utf-8"))
