"""Agregar la imagen (mapa ELA) a los resultados de capa

Funcionalidad 011: la capa ELA devuelve un mapa que se guarda en el
almacenamiento; el resultado conserva su clave.

Revision ID: b3e1c0a7d911
Revises: 7d203719a8cb
Create Date: 2026-10-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3e1c0a7d911'
down_revision = '7d203719a8cb'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega la columna de la clave de la imagen del resultado."""
    with op.batch_alter_table('resultados_capa', schema=None) as batch_op:
        batch_op.add_column(sa.Column('clave_imagen', sa.String(length=200), nullable=True))


def downgrade():
    """Quita la columna de la clave de la imagen del resultado."""
    with op.batch_alter_table('resultados_capa', schema=None) as batch_op:
        batch_op.drop_column('clave_imagen')
