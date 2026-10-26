"""Informe PDF de un análisis.

El PDF se guarda en el almacenamiento y no se modifica nunca: un análisis
nuevo genera un informe nuevo (RF44 CA4). La base guarda su clave y la
huella SHA-256 del propio PDF, que permite probar después que el documento
no cambió. Esa huella se sella en Hedera y el PDF lleva un código de
verificación público (funcionalidad 026).

Realiza: RF44, RF45, RF55; RN24, RN25; RNF07.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc


class Informe(db.Model):  # pylint: disable=too-few-public-methods
    """Informe PDF generado al finalizar un análisis."""

    __tablename__ = "informes"
    __table_args__ = (
        db.UniqueConstraint("id_analisis", name="uq_informes_analisis"),
        db.UniqueConstraint("clave", name="uq_informes_clave"),
        db.UniqueConstraint("codigo_verificacion", name="uq_informes_codigo_verificacion"),
    )
    # El sello se publica en Hedera con este tipo (funcionalidad 026).
    TIPO_SELLO = "informe"

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
    # Código que figura en el PDF para verificarlo en la página pública (RF55 CA2).
    codigo_verificacion = db.Column(db.String(16), nullable=True)
    # Sello de la huella del PDF en Hedera: pendiente, enviado, sellado o fallido (RF55 CA1).
    sello_estado = db.Column(db.String(20), nullable=True)
    sello_recibo = db.Column(db.Text, nullable=True)
    sello_referencia = db.Column(db.String(200), nullable=True)
    sello_fecha = db.Column(db.DateTime, nullable=True)
    sello_simulado = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    sello_intentos = db.Column(db.Integer, nullable=False, default=0, server_default="0")

    caso = db.relationship("Caso", back_populates="informes")
    analisis = db.relationship("Analisis", back_populates="informe")
