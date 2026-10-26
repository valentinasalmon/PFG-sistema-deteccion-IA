"""Modelo de usuario de la plataforma.

Realiza: RF01, RF02, RF03, RF05, RF07, RF52; RN01, RN02, RN03, RN39.
"""
from flask_login import UserMixin

from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

PERFIL_ABOGADO = "abogado"
PERFIL_ASEGURADORA = "aseguradora"
PERFILES = (PERFIL_ABOGADO, PERFIL_ASEGURADORA)

ROL_USUARIO = "usuario"
ROL_ADMINISTRADOR = "administrador"


class Usuario(UserMixin, db.Model):  # pylint: disable=too-few-public-methods
    """Persona registrada en la plataforma.

    El perfil (Abogado o Aseguradora) se fija al registrarse y no cambia (RN01).
    ``version_sesion`` se incrementa cuando hay que invalidar todas las
    sesiones abiertas de la cuenta, por ejemplo al restablecer la contraseña.
    """

    __tablename__ = "usuarios"
    __table_args__ = (
        db.CheckConstraint(f"perfil IN {PERFILES}", name="ck_usuarios_perfil"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(254), nullable=False, unique=True, index=True)
    hash_contrasenia = db.Column(db.String(60), nullable=False)
    perfil = db.Column(db.String(20), nullable=False)
    colegio = db.Column(db.String(150), nullable=True)
    empresa = db.Column(db.String(150), nullable=True)
    rol = db.Column(db.String(20), nullable=False, default=ROL_USUARIO)

    version_terminos = db.Column(db.String(20), nullable=False)
    aceptacion_terminos_en = db.Column(db.DateTime, nullable=False)
    correo_verificado_en = db.Column(db.DateTime, nullable=True)
    # Identificador estable de la cuenta de Google vinculada (``sub``), si la hay (RF52).
    google_sub = db.Column(db.String(255), nullable=True, unique=True)

    intentos_fallidos = db.Column(db.Integer, nullable=False, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    version_sesion = db.Column(db.Integer, nullable=False, default=1)
    # Una cuenta con perfil Aseguradora sin aseguradora queda desactivada (RN39).
    activo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())

    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc, onupdate=ahora_utc)

    @property
    def verificado(self):
        """True si la persona ya confirmó su correo electrónico (RF02)."""
        return self.correo_verificado_en is not None

    def get_id(self):
        """Identificador que Flask-Login guarda en la sesión.

        Incluye la versión de sesión: si cambia, las sesiones anteriores dejan
        de ser válidas (cierre de todas las sesiones, CA14).
        """
        return f"{self.id}:{self.version_sesion}"
