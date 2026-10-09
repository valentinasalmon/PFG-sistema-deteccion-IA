"""Clases de configuración, una por entorno (patrón Strategy).

Los valores se leen de variables de entorno con nombres en español. Los
atributos de la clase usan los nombres que exigen Flask y sus extensiones
(por ejemplo ``SECRET_KEY`` o ``SQLALCHEMY_DATABASE_URI``), ya que son
impuestos por esas bibliotecas.

Variables de entorno:
    ENTORNO          desarrollo | pruebas | produccion
    CLAVE_SECRETA    Clave para firmar sesiones y tokens.
    URL_BASE_DATOS   Cadena de conexión a PostgreSQL.
    URL_REDIS        Cadena de conexión a Redis.

Realiza: RNF03 (CA3), RNF22.
"""
import os


class ErrorConfiguracion(Exception):
    """La configuración es inválida o está incompleta."""


class ConfiguracionBase:
    """Valores comunes a todos los entornos.

    Cada subclase redefine solo lo que cambia. ``VARIABLES_OBLIGATORIAS``
    enumera las variables de entorno sin las cuales la aplicación no debe
    arrancar en ese entorno.
    """

    NOMBRE = "base"
    VERSION_APLICACION = "0.1.0"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VARIABLES_OBLIGATORIAS = ()

    def __init__(self):
        """Lee los valores desde las variables de entorno."""
        self.SECRET_KEY = os.getenv("CLAVE_SECRETA")  # pylint: disable=invalid-name
        self.SQLALCHEMY_DATABASE_URI = os.getenv(  # pylint: disable=invalid-name
            "URL_BASE_DATOS"
        )
        self.URL_REDIS = os.getenv(  # pylint: disable=invalid-name
            "URL_REDIS", "redis://localhost:6379/0"
        )

    def validar(self):
        """Verifica que existan todas las variables obligatorias del entorno.

        Raises:
            ErrorConfiguracion: con la lista de variables faltantes.
        """
        faltantes = [nombre for nombre in self.VARIABLES_OBLIGATORIAS if not os.getenv(nombre)]
        if faltantes:
            raise ErrorConfiguracion(
                f"Faltan variables de entorno obligatorias para el entorno "
                f"'{self.NOMBRE}': {', '.join(faltantes)}"
            )


class ConfiguracionDesarrollo(ConfiguracionBase):
    """Entorno local de la desarrolladora: depuración activa."""

    NOMBRE = "desarrollo"
    DEBUG = True
    VARIABLES_OBLIGATORIAS = ("URL_BASE_DATOS",)

    def __init__(self):
        """Usa una clave secreta de desarrollo si no se definió una."""
        super().__init__()
        self.SECRET_KEY = self.SECRET_KEY or "clave-solo-para-desarrollo"


class ConfiguracionPruebas(ConfiguracionBase):
    """Entorno de pruebas automatizadas: base de datos en memoria.

    Nunca usa la base de datos de desarrollo ni la de producción
    (constitución, principio 5).
    """

    NOMBRE = "pruebas"
    TESTING = True

    def __init__(self):
        """Fija valores aislados e independientes del archivo .env."""
        super().__init__()
        self.SECRET_KEY = "clave-de-pruebas"
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.URL_REDIS = "redis://localhost:6379/15"


class ConfiguracionProduccion(ConfiguracionBase):
    """Entorno de producción: todas las variables son obligatorias."""

    NOMBRE = "produccion"
    VARIABLES_OBLIGATORIAS = ("CLAVE_SECRETA", "URL_BASE_DATOS", "URL_REDIS")