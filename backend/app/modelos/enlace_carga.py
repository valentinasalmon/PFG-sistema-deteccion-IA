"""Enlaces de carga de fotos sin iniciar sesión (funcionalidades 024 y 028).

Hay dos tipos:

- ``celular``: desde la computadora se genera un enlace de un solo uso, que
  se muestra como código QR, para subir fotos desde el propio celular (024).
- ``persona_afectada``: un enlace que se le manda a la persona afectada para
  que suba ella misma sus fotos al caso, previa declaración de que son suyas
  o tiene permiso para compartirlas (028, CP-32).

Se guarda solo la huella SHA-256 del token: con la base de datos no alcanza
para reconstruir el enlace.

Realiza: RF53 (CA2); CP-32.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

TIPO_CELULAR = "celular"
TIPO_PERSONA_AFECTADA = "persona_afectada"
TIPOS_ENLACE = (TIPO_CELULAR, TIPO_PERSONA_AFECTADA)


class EnlaceCarga(db.Model):  # pylint: disable=too-few-public-methods
    """Permiso temporal para subir fotos a un caso desde otro dispositivo."""

    __tablename__ = "enlaces_carga"
    __table_args__ = (
        db.CheckConstraint(f"tipo IN {TIPOS_ENLACE}", name="ck_enlaces_carga_tipo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    huella_token = db.Column(db.String(64), nullable=False, unique=True)
    id_caso = db.Column(
        db.Integer, db.ForeignKey("casos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    vence_en = db.Column(db.DateTime, nullable=False)
    revocado_en = db.Column(db.DateTime, nullable=True)
    cargas = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    tipo = db.Column(
        db.String(20), nullable=False, default=TIPO_CELULAR, server_default=TIPO_CELULAR
    )
    # Cómo identifica quien lo generó a la persona que lo recibe (solo lo ve el equipo del caso).
    destinatario = db.Column(db.String(100), nullable=True)
    # Cuándo la persona afectada aceptó la declaración sobre sus fotos (028, CP-32).
    declaracion_aceptada_en = db.Column(db.DateTime, nullable=True)

    caso = db.relationship("Caso", back_populates="enlaces_carga")
    usuario = db.relationship("Usuario")

    def vigente(self, ahora):
        """True si no venció ni fue cancelado."""
        return self.revocado_en is None and self.vence_en > ahora
