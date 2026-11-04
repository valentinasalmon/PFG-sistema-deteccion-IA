"""Verificación de identidad del Referente de una aseguradora (funcionalidad 035).

Revision ID: a3c5e7f9b035
Revises: f9a3b5c7d032
Create Date: 2026-11-03 12:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3c5e7f9b035'
down_revision = 'f9a3b5c7d032'
branch_labels = None
depends_on = None


def upgrade():
    """Crea ``verificaciones_identidad`` (solo resultados, sin datos biométricos)."""
    op.create_table(
        'verificaciones_identidad',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('id_organizacion', sa.Integer(),
                  sa.ForeignKey('organizaciones.id', ondelete='SET NULL'), nullable=True),
        sa.Column('id_usuario', sa.Integer(),
                  sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('proveedor', sa.String(length=40), nullable=False),
        sa.Column('referencia_externa', sa.String(length=120), nullable=True),
        sa.Column('huella_token', sa.String(length=64), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('motivo', sa.String(length=300), nullable=True),
        sa.Column('creada_en', sa.DateTime(), nullable=False),
        sa.Column('resuelta_en', sa.DateTime(), nullable=True),
        sa.CheckConstraint("estado IN ('pendiente', 'aprobada', 'rechazada')",
                           name='ck_verificaciones_identidad_estado'),
        sa.UniqueConstraint('huella_token', name='uq_verificaciones_identidad_huella_token'),
    )
    op.create_index('ix_verificaciones_identidad_id_organizacion', 'verificaciones_identidad',
                    ['id_organizacion'])


def downgrade():
    """Quita ``verificaciones_identidad``."""
    op.drop_index('ix_verificaciones_identidad_id_organizacion',
                  table_name='verificaciones_identidad')
    op.drop_table('verificaciones_identidad')
