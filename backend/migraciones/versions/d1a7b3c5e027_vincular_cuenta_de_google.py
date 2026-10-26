"""Vincular la cuenta de Google a cada usuario (funcionalidad 027).

Revision ID: d1a7b3c5e027
Revises: c9e5a2f3d029
Create Date: 2026-10-28 10:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'd1a7b3c5e027'
down_revision = 'c9e5a2f3d029'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega ``usuarios.google_sub``, único y opcional."""
    with op.batch_alter_table('usuarios') as tabla:
        tabla.add_column(sa.Column('google_sub', sa.String(length=255), nullable=True))
        tabla.create_unique_constraint('uq_usuarios_google_sub', ['google_sub'])


def downgrade():
    """Quita la columna."""
    with op.batch_alter_table('usuarios') as tabla:
        tabla.drop_constraint('uq_usuarios_google_sub', type_='unique')
        tabla.drop_column('google_sub')
