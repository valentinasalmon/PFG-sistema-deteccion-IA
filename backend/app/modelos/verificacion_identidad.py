"""Verificación de identidad del Referente de una aseguradora (funcionalidad 035).

Antes de que el Administrador apruebe una aseguradora, su Referente confirma
su identidad con un proveedor externo (Identik, CP-35; hoy simulado). La
plataforma guarda **solo el resultado**: estado, motivo, fechas y la
referencia del proveedor. No hay columnas para imágenes del documento ni
datos biométricos, que son datos sensibles (Ley 25.326) y quedan del lado del
proveedor.

El enlace a la página de verificación lleva un token aleatorio; en la base
solo se guarda su huella SHA-256, como en el pago y en la carga desde el
celular.

Realiza: RN41; RF12; RNF08.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

IDENTIDAD_PENDIENTE = "pendiente"
IDENTIDAD_APROBADA = "aprobada"
IDENTIDAD_RECHAZADA = "rechazada"
ESTADOS_IDENTIDAD = (IDENTIDAD_PENDIENTE, IDENTIDAD_APROBADA, IDENTIDAD_RECHAZADA)


class VerificacionIdentidad(db.Model):  # pylint: disable=too-few-public-methods
    """Un intento de verificar la identidad del Referente de una aseguradora.

    Puede haber varios por organización (por ejemplo, uno rechazado y otro
    aprobado después); vale el más reciente. Los vínculos quedan vacíos si la
    organización o la cuenta se eliminan, para conservar la traza.
    """

    __tablename__ = "verificaciones_identidad"
    __table_args__ = (
        db.CheckConstraint(
            f"estado IN {ESTADOS_IDENTIDAD}", name="ck_verificaciones_identidad_estado"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_organizacion = db.Column(
        db.Integer, db.ForeignKey("organizaciones.id", ondelete="SET NULL"), nullable=True,
        index=True,
    )
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
    )
    proveedor = db.Column(db.String(40), nullable=False)
    referencia_externa = db.Column(db.String(120), nullable=True)
    huella_token = db.Column(db.String(64), nullable=False, unique=True)
    estado = db.Column(db.String(20), nullable=False, default=IDENTIDAD_PENDIENTE)
    motivo = db.Column(db.String(300), nullable=True)
    creada_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    resuelta_en = db.Column(db.DateTime, nullable=True)

    organizacion = db.relationship("Organizacion")
    usuario = db.relationship("Usuario")

    @property
    def aprobada(self):
        """True si la identidad quedó verificada."""
        return self.estado == IDENTIDAD_APROBADA
