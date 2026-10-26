"""Versiones desplegadas de la plataforma ("host tokenizado", funcionalidad 029).

Cada despliegue en producción registra su commit y la huella SHA-256 del
artefacto desplegado, y esa huella se sella en Hedera. Cada análisis guarda
con qué commit se hizo: así se puede probar con qué código se analizó cada caso.

Realiza: RF56; RNF07.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc


class VersionSistema(db.Model):  # pylint: disable=too-few-public-methods
    """Una versión desplegada, con la huella de su artefacto y su sello en Hedera."""

    __tablename__ = "versiones_sistema"
    __table_args__ = (db.UniqueConstraint("commit", name="uq_versiones_sistema_commit"),)
    # El sello se publica en Hedera con este tipo.
    TIPO_SELLO = "version"

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    commit = db.Column(db.String(40), nullable=False)
    huella = db.Column(db.String(64), nullable=False)
    desplegada_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    sello_estado = db.Column(db.String(20), nullable=True)
    sello_recibo = db.Column(db.Text, nullable=True)
    sello_referencia = db.Column(db.String(200), nullable=True)
    sello_fecha = db.Column(db.DateTime, nullable=True)
    sello_simulado = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    sello_intentos = db.Column(db.Integer, nullable=False, default=0, server_default="0")
