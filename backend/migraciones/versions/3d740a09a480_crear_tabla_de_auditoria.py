"""Crear la tabla de auditoría.

Funcionalidad 003 (auditoría). Realiza: RNF06 (CA2, CA3, CA5); RN34.
La clave foránea a ``usuarios`` usa ``ON DELETE SET NULL``: al eliminarse
una cuenta, sus entradas se conservan con el usuario anonimizado.

Revision ID: 3d740a09a480
Revises: a58c14fe9514
Create Date: 2026-10-16 01:01:31.298717

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identificadores de la revisión, usados por Alembic.
revision = '3d740a09a480'
down_revision = 'a58c14fe9514'
branch_labels = None
depends_on = None


def upgrade():
    """Crea la tabla ``auditoria`` y sus índices por acción, fecha y usuario."""
    op.create_table('auditoria',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('accion', sa.String(length=60), nullable=False),
    sa.Column('tipo_recurso', sa.String(length=40), nullable=True),
    sa.Column('id_recurso', sa.String(length=64), nullable=True),
    sa.Column('resultado', sa.String(length=10), nullable=False),
    sa.Column('detalle', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.CheckConstraint("resultado IN ('exitoso', 'fallido', 'rechazado')", name='ck_auditoria_resultado'),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('auditoria', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_auditoria_accion'), ['accion'], unique=False)
        batch_op.create_index(batch_op.f('ix_auditoria_fecha'), ['fecha'], unique=False)
        batch_op.create_index('ix_auditoria_id_usuario_fecha', ['id_usuario', 'fecha'], unique=False)


def downgrade():
    """Elimina la tabla ``auditoria``."""
    with op.batch_alter_table('auditoria', schema=None) as batch_op:
        batch_op.drop_index('ix_auditoria_id_usuario_fecha')
        batch_op.drop_index(batch_op.f('ix_auditoria_fecha'))
        batch_op.drop_index(batch_op.f('ix_auditoria_accion'))

    op.drop_table('auditoria')
