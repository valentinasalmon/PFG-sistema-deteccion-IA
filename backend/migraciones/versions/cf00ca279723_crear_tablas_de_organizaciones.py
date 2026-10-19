"""Crear las tablas de organizaciones, membresías e invitaciones.

Funcionalidad 004 (organizaciones e invitaciones). Realiza: RF10 a RF18;
RN07 (índice único parcial: un solo Referente por organización) y RN10
(una sola invitación pendiente por correo en cada organización).

Revision ID: cf00ca279723
Revises: 3d740a09a480
Create Date: 2026-10-16 01:14:48.182762

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = 'cf00ca279723'
down_revision = '3d740a09a480'
branch_labels = None
depends_on = None


def upgrade():
    """Crea las tablas ``organizaciones``, ``membresias`` e ``invitaciones``."""
    op.create_table('organizaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=150), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('correo_contacto', sa.String(length=254), nullable=True),
    sa.Column('telefono', sa.String(length=30), nullable=True),
    sa.Column('plan', sa.String(length=20), nullable=False),
    sa.Column('creada_en', sa.DateTime(), nullable=False),
    sa.Column('actualizada_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("tipo IN ('estudio_juridico', 'aseguradora')", name='ck_organizaciones_tipo'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invitaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_organizacion', sa.Integer(), nullable=False),
    sa.Column('correo', sa.String(length=254), nullable=False),
    sa.Column('cargo', sa.String(length=100), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('id_invitante', sa.Integer(), nullable=True),
    sa.Column('creada_en', sa.DateTime(), nullable=False),
    sa.Column('vence_en', sa.DateTime(), nullable=False),
    sa.Column('respondida_en', sa.DateTime(), nullable=True),
    sa.CheckConstraint("estado IN ('pendiente', 'aceptada', 'rechazada', 'cancelada')", name='ck_invitaciones_estado'),
    sa.ForeignKeyConstraint(['id_invitante'], ['usuarios.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['id_organizacion'], ['organizaciones.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('invitaciones', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_invitaciones_correo'), ['correo'], unique=False)
        batch_op.create_index('ux_invitaciones_pendiente', ['id_organizacion', 'correo'], unique=True, postgresql_where=sa.text("estado = 'pendiente'"), sqlite_where=sa.text("estado = 'pendiente'"))

    op.create_table('membresias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_organizacion', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('rol', sa.String(length=20), nullable=False),
    sa.Column('cargo', sa.String(length=100), nullable=True),
    sa.Column('incorporado_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("rol IN ('referente', 'miembro')", name='ck_membresias_rol'),
    sa.ForeignKeyConstraint(['id_organizacion'], ['organizaciones.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_organizacion', 'id_usuario', name='uq_membresias_usuario')
    )
    with op.batch_alter_table('membresias', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_membresias_id_usuario'), ['id_usuario'], unique=False)
        batch_op.create_index('ux_membresias_un_referente', ['id_organizacion'], unique=True, postgresql_where=sa.text("rol = 'referente'"), sqlite_where=sa.text("rol = 'referente'"))


def downgrade():
    """Elimina las tablas de la funcionalidad 004."""
    with op.batch_alter_table('membresias', schema=None) as batch_op:
        batch_op.drop_index('ux_membresias_un_referente', postgresql_where=sa.text("rol = 'referente'"), sqlite_where=sa.text("rol = 'referente'"))
        batch_op.drop_index(batch_op.f('ix_membresias_id_usuario'))

    op.drop_table('membresias')
    with op.batch_alter_table('invitaciones', schema=None) as batch_op:
        batch_op.drop_index('ux_invitaciones_pendiente', postgresql_where=sa.text("estado = 'pendiente'"), sqlite_where=sa.text("estado = 'pendiente'"))
        batch_op.drop_index(batch_op.f('ix_invitaciones_correo'))

    op.drop_table('invitaciones')
    op.drop_table('organizaciones')
