"""Pruebas del repositorio de salud contra la base de datos de pruebas."""
from sqlalchemy.exc import OperationalError

from app.extensiones import db
from app.repositorios.repositorio_salud import RepositorioSalud


def test_base_de_datos_disponible(aplicacion):
    """Con la base de pruebas activa, la verificación devuelve True."""
    with aplicacion.app_context():
        assert RepositorioSalud().verificar_conexion() is True


def test_base_de_datos_caida(aplicacion, monkeypatch):
    """CA3: si la consulta falla, la verificación devuelve False."""

    def consulta_que_falla(*_args, **_kwargs):
        raise OperationalError("SELECT 1", {}, Exception("conexión rechazada"))

    with aplicacion.app_context():
        monkeypatch.setattr(db.session, "execute", consulta_que_falla)
        assert RepositorioSalud().verificar_conexion() is False
