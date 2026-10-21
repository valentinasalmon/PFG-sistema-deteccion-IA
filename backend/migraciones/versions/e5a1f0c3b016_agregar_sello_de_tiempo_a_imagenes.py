"""agregar sello de tiempo a imagenes (funcionalidad 016)

Revision ID: e5a1f0c3b016
Revises: b3e1c0a7d911
Create Date: 2026-10-22 12:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'e5a1f0c3b016'
down_revision = 'b3e1c0a7d911'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('imagenes') as tabla:
        tabla.add_column(sa.Column('sello_estado', sa.String(length=20), nullable=True))
        tabla.add_column(sa.Column('sello_recibo', sa.Text(), nullable=True))
        tabla.add_column(sa.Column('sello_referencia', sa.String(length=200), nullable=True))
        tabla.add_column(sa.Column('sello_fecha', sa.DateTime(), nullable=True))
        tabla.add_column(sa.Column(
            'sello_simulado', sa.Boolean(), nullable=False, server_default=sa.false()))
        tabla.add_column(sa.Column(
            'sello_intentos', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    with op.batch_alter_table('imagenes') as tabla:
        for columna in ('sello_intentos', 'sello_simulado', 'sello_fecha', 'sello_referencia',
                        'sello_recibo', 'sello_estado'):
            tabla.drop_column(columna)
