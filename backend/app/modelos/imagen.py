"""Imágenes cargadas en un caso.

El archivo original se guarda sin modificar en el almacenamiento (S3 en
producción) bajo una clave aleatoria; la base guarda sus datos técnicos y la
huella SHA-256 calculada al recibirlo (RN23). La miniatura es una copia
reducida para la vista previa, aparte del original.

Realiza: RF34 a RF36; RN22 a RN24; RNF07, RNF09 (CA2).
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

FORMATO_JPEG = "jpeg"
FORMATO_PNG = "png"
FORMATOS_IMAGEN = (FORMATO_JPEG, FORMATO_PNG)
TIPOS_MIME = {FORMATO_JPEG: "image/jpeg", FORMATO_PNG: "image/png"}


class Imagen(db.Model):  # pylint: disable=too-few-public-methods
    """Imagen de un caso, con su huella y sus datos técnicos.

    Una misma imagen (misma huella) no puede cargarse dos veces en el mismo
    caso (RF34 CA4).
    """

    __tablename__ = "imagenes"
    __table_args__ = (
        db.CheckConstraint(f"formato IN {FORMATOS_IMAGEN}", name="ck_imagenes_formato"),
        db.UniqueConstraint("id_caso", "huella", name="uq_imagenes_caso_huella"),
        db.UniqueConstraint("clave", name="uq_imagenes_clave"),
        db.UniqueConstraint("clave_miniatura", name="uq_imagenes_clave_miniatura"),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_caso = db.Column(
        db.Integer, db.ForeignKey("casos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clave = db.Column(db.String(100), nullable=False)
    clave_miniatura = db.Column(db.String(100), nullable=False)
    nombre_original = db.Column(db.String(255), nullable=False)
    formato = db.Column(db.String(10), nullable=False)
    tamanio = db.Column(db.BigInteger, nullable=False)
    ancho = db.Column(db.Integer, nullable=False)
    alto = db.Column(db.Integer, nullable=False)
    huella = db.Column(db.String(64), nullable=False, index=True)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    cargada_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    # Una imagen incluida en un informe generado ya no puede eliminarse (RN24).
    # Sello de tiempo en BFA (funcionalidad 016, RF37): pendiente, enviado, sellado o fallido.
    sello_estado = db.Column(db.String(20), nullable=True)
    sello_recibo = db.Column(db.Text, nullable=True)
    sello_referencia = db.Column(db.String(200), nullable=True)
    sello_fecha = db.Column(db.DateTime, nullable=True)
    sello_simulado = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    sello_intentos = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    en_informe = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())

    caso = db.relationship("Caso", back_populates="imagenes")
    usuario = db.relationship("Usuario")

    @property
    def tipo_mime(self):
        """Tipo MIME según el formato real del contenido."""
        return TIPOS_MIME[self.formato]
