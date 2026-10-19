"""Pruebas de la validación de entradas con mensajes en español (RNF04 CA1)."""
import pytest

from app.esquemas import validar
from app.esquemas.cuentas import SolicitudInicioSesion, SolicitudRegistro
from app.servicios.errores import ErrorValidacion


def _registro(**cambios):
    datos = {
        "nombre": "Ana", "apellido": "López", "correo": "ana@ejemplo.com",
        "contrasenia": "Segura12345", "perfil": "abogado", "acepta_terminos": True,
    }
    datos.update(cambios)
    return datos


def test_registro_valido():
    """Datos correctos producen la solicitud con los espacios recortados."""
    solicitud = validar(SolicitudRegistro, _registro(nombre="  Ana  "))
    assert solicitud.nombre == "Ana"


def test_errores_en_espanol_por_campo():
    """Cada campo inválido tiene su mensaje en español."""
    with pytest.raises(ErrorValidacion) as error:
        validar(SolicitudRegistro, _registro(correo="no-es-correo", perfil="perito", nombre=""))
    errores = error.value.errores
    assert errores["correo"] == "El correo electrónico no es válido."
    assert errores["perfil"] == "El valor elegido no es válido."
    assert errores["nombre"] == "Este campo no puede estar vacío."


def test_terminos_no_aceptados():
    """La aceptación de los términos es obligatoria (CA2)."""
    with pytest.raises(ErrorValidacion) as error:
        validar(SolicitudRegistro, _registro(acepta_terminos=False))
    assert "Términos de Uso" in error.value.errores["acepta_terminos"]


def test_campo_faltante_y_campo_desconocido():
    """Se informan los campos obligatorios ausentes y los no permitidos."""
    datos = _registro(rol="administrador")
    del datos["apellido"]
    with pytest.raises(ErrorValidacion) as error:
        validar(SolicitudRegistro, datos)
    assert error.value.errores["apellido"] == "Este campo es obligatorio."
    assert error.value.errores["rol"] == "Este campo no está permitido."


def test_cuerpo_vacio():
    """Una solicitud sin cuerpo informa los campos obligatorios."""
    with pytest.raises(ErrorValidacion):
        validar(SolicitudRegistro, None)


def test_las_contrasenias_conservan_los_espacios():
    """A las contraseñas no se les quitan espacios; al resto de los textos, sí."""
    datos = {"correo": " ana@ejemplo.com ", "contrasenia": " Clave 1 "}
    solicitud = validar(SolicitudInicioSesion, datos)
    assert solicitud.contrasenia == " Clave 1 "
    assert solicitud.correo == "ana@ejemplo.com"


def test_registro_informa_todos_los_errores_juntos():
    """La política de contraseñas se informa junto con los demás errores del formulario."""
    with pytest.raises(ErrorValidacion) as error:
        validar(SolicitudRegistro, _registro(contrasenia="corta1", acepta_terminos=False))
    assert set(error.value.errores) == {"contrasenia", "acepta_terminos"}
