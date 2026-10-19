"""Casos y accesos compartidos.

Un caso pertenece al espacio personal de su Responsable o al de una
organización (RN12). Los casos de una organización pueden compartirse con
miembros puntuales o con toda la organización, con permiso de Lectura o de
Colaboración (RN13, RN20).

Realiza: RF23 a RF33; RN12, RN13, RN16 a RN20, RN30.
"""
import unicodedata

from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

TIPO_AUTOMOVILISTICO = "automovilistico"
TIPO_LABORAL = "laboral"
TIPOS_CASO = (TIPO_AUTOMOVILISTICO, TIPO_LABORAL)

ESTADO_BORRADOR = "borrador"
ESTADO_EN_ANALISIS = "en_analisis"
ESTADO_ANALIZADO = "analizado"
ESTADO_CERRADO = "cerrado"
ESTADO_ARCHIVADO = "archivado"
ESTADOS_CASO = (
    ESTADO_BORRADOR, ESTADO_EN_ANALISIS, ESTADO_ANALIZADO, ESTADO_CERRADO, ESTADO_ARCHIVADO,
)

NIVEL_LECTURA = "lectura"
NIVEL_COLABORACION = "colaboracion"
NIVELES_ACCESO = (NIVEL_LECTURA, NIVEL_COLABORACION)


def normalizar_texto(texto):
    """Minúsculas y sin tildes, para buscar sin distinguir unas de otras (RF26 CA3)."""
    if not texto:
        return None
    sin_tildes = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").lower()


class Caso(db.Model):  # pylint: disable=too-few-public-methods
    """Caso de un siniestro o de un reclamo laboral.

    ``id_organizacion`` vacío significa espacio personal. ``numero`` sigue el
    formato ``CASO-AAAA-NNNNNN`` con una secuencia global (RN16).
    ``transferencia_a`` guarda la transferencia de un caso personal que
    espera la aceptación del destinatario (RF33 CA2).
    """

    __tablename__ = "casos"
    __table_args__ = (
        db.CheckConstraint(f"tipo IN {TIPOS_CASO}", name="ck_casos_tipo"),
        db.CheckConstraint(f"estado IN {ESTADOS_CASO}", name="ck_casos_estado"),
        db.Index("ix_casos_responsable", "id_responsable"),
        db.Index("ix_casos_organizacion", "id_organizacion"),
        db.Index("ix_casos_actualizado", "actualizado_en"),
    )

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False, unique=True)
    id_organizacion = db.Column(
        db.Integer, db.ForeignKey("organizaciones.id", ondelete="CASCADE"), nullable=True
    )
    id_responsable = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    fecha_hecho = db.Column(db.Date, nullable=False)
    lugar = db.Column(db.String(200), nullable=False)
    expediente = db.Column(db.String(100), nullable=True)
    expediente_normalizado = db.Column(db.String(100), nullable=True, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default=ESTADO_BORRADOR)
    retencion_desde = db.Column(db.DateTime, nullable=True)
    transferencia_a = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    transferencia_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)

    organizacion = db.relationship("Organizacion")
    responsable = db.relationship("Usuario", foreign_keys=[id_responsable])
    destinatario_transferencia = db.relationship("Usuario", foreign_keys=[transferencia_a])
    accesos = db.relationship("AccesoCaso", back_populates="caso", cascade="all, delete-orphan")

    @property
    def es_personal(self):
        """True si el caso es del espacio personal de su Responsable."""
        return self.id_organizacion is None

    @property
    def tiene_informes(self):
        """True si el caso tiene informes generados.

        Los informes llegan con la funcionalidad 008; hasta entonces ningún
        caso los tiene y reabrir siempre vuelve a Borrador (RF29 CA1).
        """
        return False


class AccesoCaso(db.Model):  # pylint: disable=too-few-public-methods
    """Permiso de Lectura o Colaboración sobre un caso de organización.

    Es para un miembro (``id_usuario``) o para toda la organización
    (``toda_organizacion``); solo vale mientras el usuario sea miembro de la
    organización del caso (RF30 CA2).
    """

    __tablename__ = "accesos_caso"
    __table_args__ = (
        db.CheckConstraint(f"nivel IN {NIVELES_ACCESO}", name="ck_accesos_caso_nivel"),
        db.UniqueConstraint("id_caso", "id_usuario", name="uq_accesos_caso_usuario"),
        db.Index(
            "ux_accesos_caso_organizacion", "id_caso", unique=True,
            postgresql_where=db.text("toda_organizacion"),
            sqlite_where=db.text("toda_organizacion"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_caso = db.Column(db.Integer, db.ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True, index=True
    )
    toda_organizacion = db.Column(db.Boolean, nullable=False, default=False)
    nivel = db.Column(db.String(20), nullable=False)
    otorgado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)

    caso = db.relationship("Caso", back_populates="accesos")
    usuario = db.relationship("Usuario")
