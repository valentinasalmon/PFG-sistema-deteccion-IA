"""Crear la tabla de informes y marcar las imágenes incluidas en un informe.

Funcionalidad 008 (informe PDF e historial). Realiza: RF44, RF45; RN24
(una imagen de un informe no se elimina), RNF07 (huella del PDF).

Revision ID: 7d203719a8cb
Revises: 161ae29f2074
Create Date: 2026-10-19 17:20:15.452106

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = '7d203719a8cb'
down_revision = '161ae29f2074'
branch_labels = None
depends_on = None


def upgrade():
    """Crea la tabla ``informes`` y la columna ``imagenes.en_informe``."""
    op.create_table('informes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_caso', sa.Integer(), nullable=False),
    sa.Column('id_analisis', sa.Integer(), nullable=False),
    sa.Column('clave', sa.String(length=100), nullable=False),
    sa.Column('huella', sa.String(length=64), nullable=False),
    sa.Column('tamanio', sa.Integer(), nullable=False),
    sa.Column('generado_en', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['id_analisis'], ['analisis.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_caso'], ['casos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clave', name='uq_informes_clave'),
    sa.UniqueConstraint('id_analisis', name='uq_informes_analisis')
    )
    with op.batch_alter_table('informes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_informes_id_caso'), ['id_caso'], unique=False)

    with op.batch_alter_table('imagenes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('en_informe', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade():
    """Quita la columna y la tabla (los PDF del almacenamiento no se tocan)."""
    with op.batch_alter_table('imagenes', schema=None) as batch_op:
        batch_op.drop_column('en_informe')

    with op.batch_alter_table('informes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_informes_id_caso'))

    op.drop_table('informes')
