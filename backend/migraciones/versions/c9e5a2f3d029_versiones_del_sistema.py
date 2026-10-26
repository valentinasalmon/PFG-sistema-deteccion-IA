"""Crear la tabla de versiones desplegadas (funcionalidad 029).

Revision ID: c9e5a2f3d029
Revises: b8d4f1e2c026
Create Date: 2026-10-27 10:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'c9e5a2f3d029'
down_revision = 'b8d4f1e2c026'
branch_labels = None
depends_on = None


def upgrade():
    """Crea ``versiones_sistema``."""
    op.create_table(
        'versiones_sistema',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('commit', sa.String(length=40), nullable=False),
        sa.Column('huella', sa.String(length=64), nullable=False),
        sa.Column('desplegada_en', sa.DateTime(), nullable=False),
        sa.Column('sello_estado', sa.String(length=20), nullable=True),
        sa.Column('sello_recibo', sa.Text(), nullable=True),
        sa.Column('sello_referencia', sa.String(length=200), nullable=True),
        sa.Column('sello_fecha', sa.DateTime(), nullable=True),
        sa.Column('sello_simulado', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('sello_intentos', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('commit', name='uq_versiones_sistema_commit'),
    )


def downgrade():
    """Elimina ``versiones_sistema``."""
    op.drop_table('versiones_sistema')
