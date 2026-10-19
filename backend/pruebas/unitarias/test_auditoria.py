"""Pruebas unitarias del registro de auditoría.

Criterios de aceptación de la funcionalidad 003: CA2 (sin secretos) y CA13
(solo inserción).
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import pytest

from app.extensiones import db
from app.modelos.entrada_auditoria import EntradaAuditoria, RegistroInmutable
from app.repositorios.repositorio_auditoria import RepositorioAuditoria
from app.servicios import auditoria
from app.servicios.auditoria import ServicioAuditoria, limpiar_detalle


class RepositorioEnMemoria:
    """Doble del repositorio que guarda las entradas en una lista."""

    def __init__(self):
        self.entradas = []
        self.confirmaciones = 0

    def agregar(self, entrada):
        """Guarda la entrada en la lista."""
        self.entradas.append(entrada)
        return entrada

    def confirmar(self):
        """Cuenta las confirmaciones."""
        self.confirmaciones += 1


def test_limpiar_detalle_quita_claves_sensibles_en_cualquier_nivel():
    """CA2: contraseñas, hashes, huellas, tokens, cookies y sesiones no llegan a la auditoría."""
    detalle = {
        "motivo": "x",
        "contrasenia_nueva": "a",
        "Hash_Contrasenia": "b",
        "huella": "c",
        "token": "d",
        "cookie": "e",
        "csrf": "f",
        "id_sesion": "g",
        "cambios": {"nombre": {"anterior": "A", "nuevo": "B"}, "password": "h"},
        "lista": [{"token_verificacion": "i", "correo": "j"}],
    }
    assert limpiar_detalle(detalle) == {
        "motivo": "x",
        "cambios": {"nombre": {"anterior": "A", "nuevo": "B"}},
        "lista": [{"correo": "j"}],
    }


def test_registrar_arma_la_entrada_con_el_origen():
    """CA1: IP del origen, resultado, recurso y detalle limpio; sin confirmar por defecto."""
    repositorio = RepositorioEnMemoria()
    servicio = ServicioAuditoria(repositorio, {"ip": "198.51.100.4"})
    entrada = servicio.registrar(
        auditoria.SESION_INICIO, auditoria.FALLIDO, recurso=("caso", 15),
        detalle={"motivo": "m", "token": "secreto"},
    )
    assert repositorio.entradas == [entrada]
    assert repositorio.confirmaciones == 0
    assert (entrada.ip, entrada.accion) == ("198.51.100.4", "sesion.inicio")
    assert entrada.resultado == "fallido"
    assert (entrada.tipo_recurso, entrada.id_recurso) == ("caso", "15")
    assert entrada.id_usuario is None
    assert entrada.detalle == {"motivo": "m"}


def test_registrar_sin_origen_ni_recurso_y_confirmando():
    """Sin solicitud (por ejemplo, una tarea programada) la IP queda vacía."""
    repositorio = RepositorioEnMemoria()
    entrada = ServicioAuditoria(repositorio).registrar(
        auditoria.SESION_CIERRE, auditoria.EXITOSO, recurso=("tarea", None), confirmar=True
    )
    assert entrada.ip is None
    assert (entrada.tipo_recurso, entrada.id_recurso, entrada.detalle) == ("tarea", None, {})
    assert repositorio.confirmaciones == 1


def test_el_repositorio_solo_permite_agregar():
    """CA13: no hay operaciones públicas para modificar ni eliminar entradas.

    La única consulta, ``de_usuario``, es de lectura (copia de datos, funcionalidad 019).
    """
    publicos = {nombre for nombre in dir(RepositorioAuditoria) if not nombre.startswith("_")}
    assert publicos == {"agregar", "confirmar", "de_usuario"}


@pytest.fixture
def entrada_guardada(aplicacion):
    """Una entrada de auditoría ya confirmada en la base, dentro de un contexto abierto."""
    with aplicacion.app_context():
        ServicioAuditoria(RepositorioAuditoria(), {"ip": "127.0.0.1"}).registrar(
            auditoria.SESION_INICIO, auditoria.EXITOSO, confirmar=True
        )
        yield db.session.get(EntradaAuditoria, 1)
        db.session.rollback()


def test_una_entrada_no_puede_modificarse(entrada_guardada):
    """CA13: el modelo rechaza cualquier modificación."""
    entrada_guardada.resultado = "fallido"
    with pytest.raises(RegistroInmutable):
        db.session.commit()


def test_una_entrada_no_puede_eliminarse(entrada_guardada):
    """CA13: el modelo rechaza la eliminación."""
    db.session.delete(entrada_guardada)
    with pytest.raises(RegistroInmutable):
        db.session.commit()
