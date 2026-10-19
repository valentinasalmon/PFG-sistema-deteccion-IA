"""Pruebas de la política de contraseñas y del hash (RNF01 CA1 y CA2, CA4 y CA20)."""
import pytest

from app.servicios import contrasenias
from app.servicios.errores import ErrorValidacion


@pytest.mark.parametrize(
    "contrasenia, fragmento",
    [
        ("Corta1", "al menos 10 caracteres"),
        ("1234567890", "al menos una letra"),
        ("SoloLetrasLargas", "al menos un número"),
        ("Password123", "demasiado común"),
        ("ARGENTINA123", "demasiado común"),
        ("a1" * 37, "demasiado larga"),
        ("contraseñaúnica1" + "ñ" * 30, "demasiado larga"),
    ],
)
def test_contrasenias_rechazadas(contrasenia, fragmento):
    """Cada condición incumplida se informa con su motivo (CA4)."""
    with pytest.raises(ErrorValidacion, match=fragmento):
        contrasenias.validar_politica(contrasenia)


def test_contrasenia_valida():
    """Una contraseña que cumple todo no lanza errores."""
    contrasenias.validar_politica("Segura12345")


def test_hash_bcrypt_con_costo_indicado():
    """El hash es bcrypt con el costo pedido y verifica la contraseña (CA20)."""
    hash_generado = contrasenias.generar_hash("Segura12345", 12)
    assert hash_generado.startswith("$2b$12$")
    assert contrasenias.verificar("Segura12345", hash_generado)
    assert not contrasenias.verificar("Otra123456", hash_generado)


def test_contrasenia_de_mas_de_72_bytes_no_verifica():
    """bcrypt no admite más de 72 bytes: la verificación responde False sin fallar."""
    hash_generado = contrasenias.generar_hash("Segura12345", 4)
    assert not contrasenias.verificar("a1" * 40, hash_generado)
