"""Cobros del plan de una organización (funcionalidad 032).

Cada cobro es una transferencia que se espera a un CVU, identificada por una
referencia legible (``EVD-XXXXXX``), tal como cobra Cresium. Se crea al
registrar un estudio o una aseguradora, al crear un estudio desde Mi perfil y
al cambiar de plan. Mientras no esté la API de Cresium, la acreditación se
simula (CP-34).

El enlace de la página de pago lleva un token aleatorio: en la base solo se
guarda su huella SHA-256, como en los enlaces de carga.

Realiza: RF10, RF20; CP-01, CP-34.
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

COBRO_PENDIENTE = "pendiente"
COBRO_ACREDITADO = "acreditado"
COBRO_DEVUELTO = "devuelto"
ESTADOS_COBRO = (COBRO_PENDIENTE, COBRO_ACREDITADO, COBRO_DEVUELTO)

MOTIVO_ALTA = "alta"
MOTIVO_CAMBIO_PLAN = "cambio_plan"
MOTIVOS_COBRO = (MOTIVO_ALTA, MOTIVO_CAMBIO_PLAN)


class Cobro(db.Model):  # pylint: disable=too-few-public-methods
    """Pago esperado del plan de una organización.

    ``id_organizacion`` queda vacío si la organización se elimina (por
    ejemplo, una aseguradora rechazada) y también en el cobro de un registro
    con un correo ya existente, que existe para no revelar ese hecho (RF01 CA3).
    """

    __tablename__ = "cobros"
    __table_args__ = (
        db.CheckConstraint(f"estado IN {ESTADOS_COBRO}", name="ck_cobros_estado"),
        db.CheckConstraint(f"motivo IN {MOTIVOS_COBRO}", name="ck_cobros_motivo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_organizacion = db.Column(
        db.Integer, db.ForeignKey("organizaciones.id", ondelete="SET NULL"), nullable=True,
        index=True,
    )
    # Nombre de la organización al crear el cobro: se muestra aunque no exista.
    nombre_organizacion = db.Column(db.String(150), nullable=False)
    tipo_organizacion = db.Column(db.String(20), nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    motivo = db.Column(db.String(20), nullable=False, default=MOTIVO_ALTA)
    referencia = db.Column(db.String(20), nullable=False, unique=True)
    huella_token = db.Column(db.String(64), nullable=False, unique=True)
    estado = db.Column(db.String(20), nullable=False, default=COBRO_PENDIENTE)
    proveedor = db.Column(db.String(40), nullable=False)
    cvu = db.Column(db.String(22), nullable=False)
    alias = db.Column(db.String(40), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    acreditado_en = db.Column(db.DateTime, nullable=True)
    devuelto_en = db.Column(db.DateTime, nullable=True)

    organizacion = db.relationship("Organizacion")
