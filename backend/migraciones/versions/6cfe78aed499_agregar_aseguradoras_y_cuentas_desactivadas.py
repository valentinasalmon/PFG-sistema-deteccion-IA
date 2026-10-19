"""Agregar el estado y el CUIT de las organizaciones y las cuentas desactivadas.

Funcionalidad 021 (organizaciones de aseguradoras). Realiza: RN37 (un CUIT
por organización), RN38 (aseguradoras pendientes de aprobación) y RN39
(cuentas desactivadas). Las organizaciones y cuentas existentes quedan
activas.

Revision ID: 6cfe78aed499
Revises: cf00ca279723
Create Date: 2026-10-16 01:49:34.594464

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = '6cfe78aed499'
down_revision = 'cf00ca279723'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega ``cuit``, ``estado`` y ``aprobada_en`` a organizaciones y ``activo`` a usuarios."""
    with op.batch_alter_table('organizaciones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cuit', sa.String(length=11), nullable=True))
        batch_op.add_column(sa.Column('estado', sa.String(length=20), server_default='activa', nullable=False))
        batch_op.add_column(sa.Column('aprobada_en', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint('uq_organizaciones_cuit', ['cuit'])
        batch_op.create_check_constraint(
            'ck_organizaciones_estado', "estado IN ('pendiente', 'activa')"
        )

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activo', sa.Boolean(), server_default=sa.text('true'), nullable=False))


def downgrade():
    """Quita las columnas y restricciones agregadas."""
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('activo')

    with op.batch_alter_table('organizaciones', schema=None) as batch_op:
        batch_op.drop_constraint('ck_organizaciones_estado', type_='check')
        batch_op.drop_constraint('uq_organizaciones_cuit', type_='unique')
        batch_op.drop_column('aprobada_en')
        batch_op.drop_column('estado')
        batch_op.drop_column('cuit')
