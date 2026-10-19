"""Informe PDF de un análisis.

El PDF se guarda en el almacenamiento y no se modifica nunca: un análisis
nuevo genera un informe nuevo (RF44 CA4). La base guarda su clave y la
huella SHA-256 del propio PDF, que permite probar después que el documento
no cambió.

Realiza: RF44, RF45; RN24, RN25; RNF07.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc


class Informe(db.Model):  # pylint: disable=too-few-public-methods
    """Informe PDF generado al finalizar un análisis."""

    __tablename__ = "informes"
    __table_args__ = (
        db.UniqueConstraint("id_analisis", name="uq_informes_analisis"),
        db.UniqueConstraint("clave", name="uq_informes_clave"),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_caso = db.Column(
        db.Integer, db.ForeignKey("casos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    id_analisis = db.Column(
        db.Integer, db.ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False
    )
    clave = db.Column(db.String(100), nullable=False)
    huella = db.Column(db.String(64), nullable=False)
    tamanio = db.Column(db.Integer, nullable=False)
    generado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)

    caso = db.relationship("Caso", back_populates="informes")
    analisis = db.relationship("Analisis", back_populates="informe")
