"""Crear las tablas de casos y accesos compartidos.

Funcionalidad 005 (casos y permisos). Realiza: RF23 a RF33; RN12, RN13,
RN16 (número único), RN20.

Revision ID: 057c1b5b72d9
Revises: 6cfe78aed499
Create Date: 2026-10-19 13:37:37.550530

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = '057c1b5b72d9'
down_revision = '6cfe78aed499'
branch_labels = None
depends_on = None


def upgrade():
    """Crea las tablas ``casos`` y ``accesos_caso`` con sus índices."""
    op.create_table('casos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero', sa.String(length=20), nullable=False),
    sa.Column('id_organizacion', sa.Integer(), nullable=True),
    sa.Column('id_responsable', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('fecha_hecho', sa.Date(), nullable=False),
    sa.Column('lugar', sa.String(length=200), nullable=False),
    sa.Column('expediente', sa.String(length=100), nullable=True),
    sa.Column('expediente_normalizado', sa.String(length=100), nullable=True),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('retencion_desde', sa.DateTime(), nullable=True),
    sa.Column('transferencia_a', sa.Integer(), nullable=True),
    sa.Column('transferencia_en', sa.DateTime(), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=False),
    sa.Column('actualizado_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("estado IN ('borrador', 'en_analisis', 'analizado', 'cerrado', 'archivado')", name='ck_casos_estado'),
    sa.CheckConstraint("tipo IN ('automovilistico', 'laboral')", name='ck_casos_tipo'),
    sa.ForeignKeyConstraint(['id_organizacion'], ['organizaciones.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_responsable'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['transferencia_a'], ['usuarios.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero')
    )
    with op.batch_alter_table('casos', schema=None) as batch_op:
        batch_op.create_index('ix_casos_actualizado', ['actualizado_en'], unique=False)
        batch_op.create_index(batch_op.f('ix_casos_expediente_normalizado'), ['expediente_normalizado'], unique=False)
        batch_op.create_index('ix_casos_organizacion', ['id_organizacion'], unique=False)
        batch_op.create_index('ix_casos_responsable', ['id_responsable'], unique=False)

    op.create_table('accesos_caso',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_caso', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('toda_organizacion', sa.Boolean(), nullable=False),
    sa.Column('nivel', sa.String(length=20), nullable=False),
    sa.Column('otorgado_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("nivel IN ('lectura', 'colaboracion')", name='ck_accesos_caso_nivel'),
    sa.ForeignKeyConstraint(['id_caso'], ['casos.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_caso', 'id_usuario', name='uq_accesos_caso_usuario')
    )
    with op.batch_alter_table('accesos_caso', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_accesos_caso_id_usuario'), ['id_usuario'], unique=False)
        batch_op.create_index('ux_accesos_caso_organizacion', ['id_caso'], unique=True, postgresql_where=sa.text('toda_organizacion'), sqlite_where=sa.text('toda_organizacion'))


def downgrade():
    """Elimina las tablas de la funcionalidad 005."""
    with op.batch_alter_table('accesos_caso', schema=None) as batch_op:
        batch_op.drop_index('ux_accesos_caso_organizacion', postgresql_where=sa.text('toda_organizacion'), sqlite_where=sa.text('toda_organizacion'))
        batch_op.drop_index(batch_op.f('ix_accesos_caso_id_usuario'))

    op.drop_table('accesos_caso')
    with op.batch_alter_table('casos', schema=None) as batch_op:
        batch_op.drop_index('ix_casos_responsable')
        batch_op.drop_index('ix_casos_organizacion')
        batch_op.drop_index(batch_op.f('ix_casos_expediente_normalizado'))
        batch_op.drop_index('ix_casos_actualizado')

    op.drop_table('casos')
