"""Cobros del plan y estado «pago pendiente» de las organizaciones (funcionalidad 032).

Revision ID: f9a3b5c7d032
Revises: e8c2d4a6f028
Create Date: 2026-10-29 18:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'f9a3b5c7d032'
down_revision = 'e8c2d4a6f028'
branch_labels = None
depends_on = None


def upgrade():
    """Crea ``cobros`` y suma el estado ``pago_pendiente``."""
    with op.batch_alter_table('organizaciones') as tabla:
        tabla.drop_constraint('ck_organizaciones_estado', type_='check')
        tabla.create_check_constraint(
            'ck_organizaciones_estado', "estado IN ('pago_pendiente', 'pendiente', 'activa')"
        )
    op.create_table(
        'cobros',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('id_organizacion', sa.Integer(),
                  sa.ForeignKey('organizaciones.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nombre_organizacion', sa.String(length=150), nullable=False),
        sa.Column('tipo_organizacion', sa.String(length=20), nullable=False),
        sa.Column('plan', sa.String(length=20), nullable=False),
        sa.Column('motivo', sa.String(length=20), nullable=False),
        sa.Column('referencia', sa.String(length=20), nullable=False),
        sa.Column('huella_token', sa.String(length=64), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('proveedor', sa.String(length=40), nullable=False),
        sa.Column('cvu', sa.String(length=22), nullable=False),
        sa.Column('alias', sa.String(length=40), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('acreditado_en', sa.DateTime(), nullable=True),
        sa.Column('devuelto_en', sa.DateTime(), nullable=True),
        sa.CheckConstraint("estado IN ('pendiente', 'acreditado', 'devuelto')",
                           name='ck_cobros_estado'),
        sa.CheckConstraint("motivo IN ('alta', 'cambio_plan')", name='ck_cobros_motivo'),
        sa.UniqueConstraint('referencia', name='uq_cobros_referencia'),
        sa.UniqueConstraint('huella_token', name='uq_cobros_huella_token'),
    )
    op.create_index('ix_cobros_id_organizacion', 'cobros', ['id_organizacion'])


def downgrade():
    """Quita ``cobros`` y el estado nuevo (las organizaciones con pago pendiente pasan a activas)."""
    op.drop_index('ix_cobros_id_organizacion', table_name='cobros')
    op.drop_table('cobros')
    op.execute("UPDATE organizaciones SET estado = 'activa' WHERE estado = 'pago_pendiente'")
    with op.batch_alter_table('organizaciones') as tabla:
        tabla.drop_constraint('ck_organizaciones_estado', type_='check')
        tabla.create_check_constraint(
            'ck_organizaciones_estado', "estado IN ('pendiente', 'activa')"
        )
