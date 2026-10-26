"""Crear la tabla de enlaces de carga desde el celular (funcionalidad 024).

Revision ID: a7c3e9d2b024
Revises: f6b2a1d4c024
Create Date: 2026-10-26 12:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7c3e9d2b024'
down_revision = 'f6b2a1d4c024'
branch_labels = None
depends_on = None


def upgrade():
    """Crea ``enlaces_carga``."""
    op.create_table(
        'enlaces_carga',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('huella_token', sa.String(length=64), nullable=False),
        sa.Column('id_caso', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('vence_en', sa.DateTime(), nullable=False),
        sa.Column('revocado_en', sa.DateTime(), nullable=True),
        sa.Column('cargas', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['id_caso'], ['casos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('huella_token'),
    )
    op.create_index('ix_enlaces_carga_id_caso', 'enlaces_carga', ['id_caso'])


def downgrade():
    """Elimina ``enlaces_carga``."""
    op.drop_index('ix_enlaces_carga_id_caso', table_name='enlaces_carga')
    op.drop_table('enlaces_carga')
