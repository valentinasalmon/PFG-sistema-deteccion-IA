"""Organizaciones, membresías e invitaciones.

Una organización (estudio jurídico o aseguradora) agrupa a varios usuarios.
Cada membresía indica el rol del usuario en ella: exactamente uno es el
Referente, que la administra (RN07). Las invitaciones se envían a un correo,
esté registrado o no, y vencen a los 7 días (RN10).

Realiza: RF10 a RF18; RN06, RN07, RN10, RN11, RN36, RN37.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

TIPO_ESTUDIO_JURIDICO = "estudio_juridico"
TIPO_ASEGURADORA = "aseguradora"
TIPOS_ORGANIZACION = (TIPO_ESTUDIO_JURIDICO, TIPO_ASEGURADORA)

ROL_REFERENTE = "referente"
ROL_MIEMBRO = "miembro"
ROLES_ORGANIZACION = (ROL_REFERENTE, ROL_MIEMBRO)

# Estado de la organización: las aseguradoras esperan la aprobación del Administrador (RN37).
ORGANIZACION_PENDIENTE = "pendiente"
ORGANIZACION_ACTIVA = "activa"
ESTADOS_ORGANIZACION = (ORGANIZACION_PENDIENTE, ORGANIZACION_ACTIVA)

INVITACION_PENDIENTE = "pendiente"
INVITACION_ACEPTADA = "aceptada"
INVITACION_RECHAZADA = "rechazada"
INVITACION_CANCELADA = "cancelada"
ESTADOS_INVITACION = (
    INVITACION_PENDIENTE, INVITACION_ACEPTADA, INVITACION_RECHAZADA, INVITACION_CANCELADA,
)


class Organizacion(db.Model):  # pylint: disable=too-few-public-methods
    """Estudio jurídico o aseguradora con su plan de uso.

    Al eliminarse, se eliminan también sus membresías e invitaciones (en el
    ORM y, como respaldo, con ``ON DELETE CASCADE`` en la base).
    """

    __tablename__ = "organizaciones"
    __table_args__ = (
        db.CheckConstraint(f"tipo IN {TIPOS_ORGANIZACION}", name="ck_organizaciones_tipo"),
        db.CheckConstraint(f"estado IN {ESTADOS_ORGANIZACION}", name="ck_organizaciones_estado"),
        db.UniqueConstraint("cuit", name="uq_organizaciones_cuit"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    correo_contacto = db.Column(db.String(254), nullable=True)
    telefono = db.Column(db.String(30), nullable=True)
    plan = db.Column(db.String(20), nullable=False)
    # CUIT de la aseguradora del catálogo de la SSN: una organización por empresa (RN36).
    cuit = db.Column(db.String(11), nullable=True)
    estado = db.Column(
        db.String(20), nullable=False, default=ORGANIZACION_ACTIVA,
        server_default=ORGANIZACION_ACTIVA,
    )
    aprobada_en = db.Column(db.DateTime, nullable=True)
    creada_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    actualizada_en = db.Column(db.DateTime, nullable=False, default=ahora_utc, onupdate=ahora_utc)

    membresias = db.relationship(
        "Membresia", back_populates="organizacion", cascade="all, delete-orphan"
    )
    invitaciones = db.relationship(
        "Invitacion", back_populates="organizacion", cascade="all, delete-orphan"
    )

    @property
    def es_aseguradora(self):
        """True si la organización es una aseguradora del catálogo de la SSN."""
        return self.tipo == TIPO_ASEGURADORA

    @property
    def pendiente(self):
        """True si espera la aprobación del Administrador (RN37)."""
        return self.estado == ORGANIZACION_PENDIENTE


class Membresia(db.Model):  # pylint: disable=too-few-public-methods
    """Pertenencia de un usuario a una organización, con su rol y cargo.

    El cargo es un dato de la membresía, no del usuario: el Referente puede
    editarlo sin tocar los datos personales del miembro (RN11). El índice
    único parcial garantiza un solo Referente por organización (RN07).
    """

    __tablename__ = "membresias"
    __table_args__ = (
        db.UniqueConstraint("id_organizacion", "id_usuario", name="uq_membresias_usuario"),
        db.CheckConstraint(f"rol IN {ROLES_ORGANIZACION}", name="ck_membresias_rol"),
        db.Index(
            "ux_membresias_un_referente", "id_organizacion", unique=True,
            postgresql_where=db.text("rol = 'referente'"),
            sqlite_where=db.text("rol = 'referente'"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_organizacion = db.Column(
        db.Integer, db.ForeignKey("organizaciones.id", ondelete="CASCADE"), nullable=False
    )
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rol = db.Column(db.String(20), nullable=False)
    cargo = db.Column(db.String(100), nullable=True)
    incorporado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)

    organizacion = db.relationship("Organizacion", back_populates="membresias")
    usuario = db.relationship("Usuario")

    @property
    def es_referente(self):
        """True si el miembro administra la organización."""
        return self.rol == ROL_REFERENTE


class Invitacion(db.Model):  # pylint: disable=too-few-public-methods
    """Invitación a un correo para sumarse a una organización (RF12, RF13).

    Solo puede haber una invitación pendiente por correo en cada organización.
    """

    __tablename__ = "invitaciones"
    __table_args__ = (
        db.CheckConstraint(f"estado IN {ESTADOS_INVITACION}", name="ck_invitaciones_estado"),
        db.Index(
            "ux_invitaciones_pendiente", "id_organizacion", "correo", unique=True,
            postgresql_where=db.text("estado = 'pendiente'"),
            sqlite_where=db.text("estado = 'pendiente'"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_organizacion = db.Column(
        db.Integer, db.ForeignKey("organizaciones.id", ondelete="CASCADE"), nullable=False
    )
    correo = db.Column(db.String(254), nullable=False, index=True)
    cargo = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default=INVITACION_PENDIENTE)
    id_invitante = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    creada_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    vence_en = db.Column(db.DateTime, nullable=False)
    respondida_en = db.Column(db.DateTime, nullable=True)

    organizacion = db.relationship("Organizacion", back_populates="invitaciones")
    invitante = db.relationship("Usuario")

    def vigente(self, momento):
        """True si está pendiente y no venció en ``momento``."""
        return self.estado == INVITACION_PENDIENTE and self.vence_en > momento
