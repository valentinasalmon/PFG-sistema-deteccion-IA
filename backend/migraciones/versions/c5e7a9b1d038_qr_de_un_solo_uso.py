"""QR del celular de un solo uso (funcionalidad 038).

El enlace del QR queda atado al primer dispositivo que lo abre (se guarda
solo la huella de su clave) y se cierra cuando ese dispositivo toca
«Terminar».

Revision ID: c5e7a9b1d038
Revises: b4d6f8a0c038
Create Date: 2026-11-06 19:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'c5e7a9b1d038'
down_revision = 'b4d6f8a0c038'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega ``huella_dispositivo`` y ``terminado_en`` a ``enlaces_carga``."""
    with op.batch_alter_table('enlaces_carga') as tabla:
        tabla.add_column(sa.Column('huella_dispositivo', sa.String(64), nullable=True))
        tabla.add_column(sa.Column('terminado_en', sa.DateTime(), nullable=True))


def downgrade():
    """Quita las dos columnas."""
    with op.batch_alter_table('enlaces_carga') as tabla:
        tabla.drop_column('terminado_en')
        tabla.drop_column('huella_dispositivo')
