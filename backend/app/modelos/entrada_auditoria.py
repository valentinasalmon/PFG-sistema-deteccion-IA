"""Entrada del registro de auditoría.

Cada entrada describe una acción relevante: quién la hizo, cuándo, desde qué
dirección IP, sobre qué recurso y con qué resultado. El registro es de solo
inserción: el modelo impide modificar o eliminar entradas desde la
aplicación.

Realiza: RNF06 (CA2, CA3, CA5); RN34.
"""
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSONB

from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

RESULTADO_EXITOSO = "exitoso"
RESULTADO_FALLIDO = "fallido"
RESULTADO_RECHAZADO = "rechazado"
RESULTADOS = (RESULTADO_EXITOSO, RESULTADO_FALLIDO, RESULTADO_RECHAZADO)


class RegistroInmutable(Exception):
    """Se intentó modificar o eliminar una entrada de auditoría (RNF06 CA3)."""


class EntradaAuditoria(db.Model):  # pylint: disable=too-few-public-methods
    """Una acción registrada en la auditoría.

    ``id_usuario`` queda vacío si no había sesión ni cuenta identificable, y
    pasa a vacío si la cuenta se elimina (``ON DELETE SET NULL``): la entrada
    se conserva con el usuario anonimizado (RNF06 CA5).
    """

    __tablename__ = "auditoria"
    __table_args__ = (
        db.CheckConstraint(f"resultado IN {RESULTADOS}", name="ck_auditoria_resultado"),
        db.Index("ix_auditoria_id_usuario_fecha", "id_usuario", "fecha"),
    )

    # En SQLite (pruebas) solo INTEGER es autoincremental.
    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=ahora_utc, index=True)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    ip = db.Column(db.String(45), nullable=True)
    accion = db.Column(db.String(60), nullable=False, index=True)
    tipo_recurso = db.Column(db.String(40), nullable=True)
    id_recurso = db.Column(db.String(64), nullable=True)
    resultado = db.Column(db.String(10), nullable=False)
    detalle = db.Column(db.JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)


@event.listens_for(EntradaAuditoria, "before_update")
def _impedir_modificacion(_mapper, _conexion, _entrada):
    raise RegistroInmutable("Las entradas de auditoría no pueden modificarse.")


@event.listens_for(EntradaAuditoria, "before_delete")
def _impedir_eliminacion(_mapper, _conexion, _entrada):
    raise RegistroInmutable("Las entradas de auditoría no pueden eliminarse.")
