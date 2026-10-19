"""Clases de configuración, una por entorno (patrón Strategy).

Los valores se leen de variables de entorno con nombres en español. Los
atributos de la clase usan los nombres que exigen Flask y sus extensiones
(por ejemplo ``SECRET_KEY`` o ``SQLALCHEMY_DATABASE_URI``), ya que son
impuestos por esas bibliotecas.

Variables de entorno:
    ENTORNO              desarrollo | pruebas | produccion
    CLAVE_SECRETA        Clave para firmar sesiones y tokens.
    URL_BASE_DATOS       Cadena de conexión a PostgreSQL.
    URL_REDIS            Cadena de conexión a Redis.
    URL_FRONTEND         Dirección de la interfaz web (enlaces de los correos).
    SERVIDOR_CORREO      Servidor SMTP (Mailpit en desarrollo, SES en producción).
    PUERTO_CORREO        Puerto SMTP.
    USUARIO_CORREO       Usuario SMTP (vacío en desarrollo).
    CONTRASENIA_CORREO   Contraseña SMTP (vacía en desarrollo).
    USAR_TLS_CORREO      "si" para cifrar la conexión SMTP con STARTTLS.
    REMITENTE_CORREO     Dirección que figura como remitente.
    ADMINISTRADORES      Correos separados por comas que reciben el rol de
                         Administrador al iniciar sesión (funcionalidad 021).

Realiza: RNF01, RNF02, RNF03 (CA3), RNF22.
"""
import os
from datetime import timedelta

from cachelib import SimpleCache


class ErrorConfiguracion(Exception):
    """La configuración es inválida o está incompleta."""


class ConfiguracionBase:  # pylint: disable=too-many-instance-attributes
    """Valores comunes a todos los entornos.

    Cada subclase redefine solo lo que cambia. ``VARIABLES_OBLIGATORIAS``
    enumera las variables de entorno sin las cuales la aplicación no debe
    arrancar en ese entorno.
    """

    NOMBRE = "base"
    VERSION_APLICACION = "0.2.0"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Verifica cada conexión antes de usarla: si la base se reinició, descarta
    # las conexiones viejas en lugar de fallar en la primera consulta (RNF16).
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- Sesiones del lado del servidor (ADR-0003, RNF01) ---
    # La sesión vive en Redis: cerrar sesión la elimina y la cookie deja de servir.
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = True
    SESSION_KEY_PREFIX = "sesion:"
    # Inactividad máxima: cada solicitud renueva el plazo (RNF01 CA4).
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_REFRESH_EACH_REQUEST = True
    # Duración máxima de una sesión, aunque haya actividad (RNF01 CA4).
    DURACION_MAXIMA_SESION = timedelta(hours=8)
    SESSION_COOKIE_NAME = "sesion"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_DURATION = timedelta(0)

    # --- Protección CSRF (RNF02 CA3) ---
    WTF_CSRF_ENABLED = True
    WTF_CSRF_HEADERS = ["X-CSRFToken"]
    WTF_CSRF_TIME_LIMIT = None  # el token vive lo que vive la sesión

    # --- Contraseñas y bloqueo (RNF01) ---
    BCRYPT_COSTO = 12
    INTENTOS_ANTES_DE_BLOQUEO = 5
    DURACION_BLOQUEO = timedelta(minutes=15)

    # --- Vigencia de los enlaces enviados por correo ---
    VIGENCIA_TOKEN_VERIFICACION = timedelta(hours=24)
    VIGENCIA_TOKEN_RECUPERACION = timedelta(hours=1)
    VIGENCIA_TOKEN_CAMBIO_CORREO = timedelta(hours=24)
    VIGENCIA_COPIA_DATOS = timedelta(minutes=15)  # RF09 CA2

    # --- Organizaciones (funcionalidad 004) ---
    # Límites de cada plan (CP-02, valores propuestos). Son datos configurables
    # para poder ajustarlos sin cambiar el código (RF19 CA3); la 014 los pasará
    # a la base de datos cuando el Administrador pueda cambiar el plan.
    PLANES = {
        "basico": {"nombre": "Organización Básico", "miembros": 5},
        "profesional": {"nombre": "Organización Profesional", "miembros": 25},
    }
    PLAN_INICIAL_ORGANIZACION = "basico"
    VIGENCIA_INVITACION = timedelta(days=7)  # RN10

    # --- Términos de Uso y Política de Privacidad vigentes (RNF08 CA1) ---
    VERSION_TERMINOS = "1.0"

    # --- Correo ---
    PROVEEDOR_CORREO = "smtp"

    VARIABLES_OBLIGATORIAS = ()

    def __init__(self):
        """Lee los valores desde las variables de entorno."""
        # pylint: disable=invalid-name
        self.SECRET_KEY = os.getenv("CLAVE_SECRETA")
        self.SQLALCHEMY_DATABASE_URI = os.getenv("URL_BASE_DATOS")
        self.URL_REDIS = os.getenv("URL_REDIS", "redis://localhost:6379/0")
        self.URL_FRONTEND = os.getenv("URL_FRONTEND", "http://localhost:5173")
        self.SERVIDOR_CORREO = os.getenv("SERVIDOR_CORREO", "localhost")
        self.PUERTO_CORREO = int(os.getenv("PUERTO_CORREO", "1025"))
        self.USUARIO_CORREO = os.getenv("USUARIO_CORREO", "")
        self.CONTRASENIA_CORREO = os.getenv("CONTRASENIA_CORREO", "")
        self.USAR_TLS_CORREO = os.getenv("USAR_TLS_CORREO", "no").lower() == "si"
        # Quien administra el servidor designa a los administradores; la
        # interfaz nunca ofrece ese rol (funcionalidad 021).
        self.ADMINISTRADORES = frozenset(
            correo.strip().lower()
            for correo in os.getenv("ADMINISTRADORES", "").split(",")
            if correo.strip()
        )
        self.REMITENTE_CORREO = os.getenv(
            "REMITENTE_CORREO", "Plataforma de análisis de imágenes <no-responder@localhost>"
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
    """Entorno de pruebas automatizadas: todo en memoria.

    Nunca usa la base de datos de desarrollo ni la de producción
    (constitución, principio 5). Las sesiones viven en memoria, los correos
    se guardan en una lista en lugar de enviarse y bcrypt usa el costo
    mínimo para que las pruebas sean rápidas.
    """

    NOMBRE = "pruebas"
    TESTING = True
    SESSION_TYPE = "cachelib"
    WTF_CSRF_ENABLED = False
    BCRYPT_COSTO = 4
    PROVEEDOR_CORREO = "memoria"

    def __init__(self):
        """Fija valores aislados e independientes del archivo .env."""
        super().__init__()
        # pylint: disable=invalid-name
        self.SECRET_KEY = "clave-de-pruebas"
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.URL_REDIS = "redis://localhost:6379/15"
        self.URL_FRONTEND = "http://frontend.prueba"
        self.ADMINISTRADORES = frozenset()
        self.SESSION_CACHELIB = SimpleCache()


class ConfiguracionProduccion(ConfiguracionBase):
    """Entorno de producción: todas las variables son obligatorias."""

    NOMBRE = "produccion"
    SESSION_COOKIE_SECURE = True  # la cookie solo viaja por HTTPS (RNF02 CA2)
    VARIABLES_OBLIGATORIAS = (
        "CLAVE_SECRETA",
        "URL_BASE_DATOS",
        "URL_REDIS",
        "URL_FRONTEND",
        "SERVIDOR_CORREO",
        "REMITENTE_CORREO",
    )
