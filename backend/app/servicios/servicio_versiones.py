"""Registro de las versiones desplegadas en Hedera ("host tokenizado", funcionalidad 029).

El script de despliegue llama a ``registrar`` con el commit y la huella del
artefacto. La huella se sella en Hedera con el mismo mecanismo que las
imágenes y los informes. La página pública de verificación de un informe
muestra con qué versión se hizo el análisis y su sello.

Realiza: RF56 (CA1, CA2); RNF07.
"""
from app.modelos.version_sistema import VersionSistema
from app.servicios import auditoria
from app.servicios.errores import ErrorValidacion


def _es_hexadecimal(texto, largo):
    return len(texto) == largo and all(c in "0123456789abcdef" for c in texto)


class ServicioVersiones:
    """Registra versiones desplegadas y las busca por commit."""

    def __init__(self, repositorio, sellos, registro, version_aplicacion):
        """
        Args:
            repositorio: ``RepositorioVersiones``.
            sellos: ``ServicioSellos``.
            registro: ``ServicioAuditoria``.
            version_aplicacion: número de versión de la plataforma.
        """
        self.repositorio = repositorio
        self.sellos = sellos
        self.registro = registro
        self.version_aplicacion = version_aplicacion

    def registrar(self, commit, huella):
        """Registra la versión (una sola vez por commit) y pide su sello en Hedera.

        Returns:
            La ``VersionSistema``, nueva o la que ya existía.
        """
        commit, huella = (commit or "").lower(), (huella or "").lower()
        if not _es_hexadecimal(commit, 40) or not _es_hexadecimal(huella, 64):
            raise ErrorValidacion("El commit o la huella del artefacto no son válidos.")
        version = self.repositorio.por_commit(commit)
        if version is None:
            version = self.repositorio.preparar(VersionSistema(
                version=self.version_aplicacion, commit=commit, huella=huella,
                sello_estado="pendiente" if self.sellos.activo else None,
            ))
            self.registro.registrar(
                auditoria.VERSION_DESPLIEGUE, auditoria.EXITOSO,
                recurso=(auditoria.TIPO_VERSION, version.id),
                detalle={"commit": commit, "sha256": huella, "version": self.version_aplicacion},
            )
            self.repositorio.confirmar()
        if version.sello_estado:
            self.sellos.intentar(version)
        return version

    def por_commit(self, commit):
        """La versión desplegada con ese commit, o None."""
        return self.repositorio.por_commit((commit or "").lower()) if commit else None
