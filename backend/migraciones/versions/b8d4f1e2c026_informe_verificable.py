"""Informe verificable: código público y sello de la huella del PDF (funcionalidad 026).

Revision ID: b8d4f1e2c026
Revises: a7c3e9d2b024
Create Date: 2026-10-26 18:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'b8d4f1e2c026'
down_revision = 'a7c3e9d2b024'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega el código de verificación y las columnas del sello a ``informes``."""
    with op.batch_alter_table('informes') as tabla:
        tabla.add_column(sa.Column('codigo_verificacion', sa.String(length=16), nullable=True))
        tabla.add_column(sa.Column('sello_estado', sa.String(length=20), nullable=True))
        tabla.add_column(sa.Column('sello_recibo', sa.Text(), nullable=True))
        tabla.add_column(sa.Column('sello_referencia', sa.String(length=200), nullable=True))
        tabla.add_column(sa.Column('sello_fecha', sa.DateTime(), nullable=True))
        tabla.add_column(sa.Column(
            'sello_simulado', sa.Boolean(), server_default=sa.false(), nullable=False
        ))
        tabla.add_column(sa.Column(
            'sello_intentos', sa.Integer(), server_default='0', nullable=False
        ))
        tabla.create_unique_constraint('uq_informes_codigo_verificacion', ['codigo_verificacion'])


def downgrade():
    """Quita el código de verificación y el sello de ``informes``."""
    with op.batch_alter_table('informes') as tabla:
        tabla.drop_constraint('uq_informes_codigo_verificacion', type_='unique')
        for columna in ('sello_intentos', 'sello_simulado', 'sello_fecha', 'sello_referencia',
                        'sello_recibo', 'sello_estado', 'codigo_verificacion'):
            tabla.drop_column(columna)
