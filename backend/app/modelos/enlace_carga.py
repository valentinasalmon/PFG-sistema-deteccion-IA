"""Enlaces de carga desde el celular (funcionalidad 024, etapa 2).

Desde la computadora se genera un enlace de un solo uso, que se muestra como
código QR. Con él, el celular sube fotos a ese caso sin iniciar sesión. Se
guarda solo la huella SHA-256 del token: con la base de datos no alcanza
para reconstruir el enlace.

Realiza: RF53 (CA2).
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc


class EnlaceCarga(db.Model):  # pylint: disable=too-few-public-methods
    """Permiso temporal para subir fotos a un caso desde otro dispositivo."""

    __tablename__ = "enlaces_carga"

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

    caso = db.relationship("Caso", back_populates="enlaces_carga")
    usuario = db.relationship("Usuario")

    def vigente(self, ahora):
        """True si no venció ni fue cancelado."""
        return self.revocado_en is None and self.vence_en > ahora
