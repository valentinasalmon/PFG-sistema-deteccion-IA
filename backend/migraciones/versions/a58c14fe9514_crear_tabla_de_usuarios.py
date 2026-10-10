"""Crear la tabla de usuarios.

Funcionalidad 002 (cuentas y sesión). Realiza: RF01, RF02, RF03, RF05, RF07;
RN01 (restricción del perfil), RN03 (correo único).

Revision ID: a58c14fe9514
Revises:
Create Date: 2026-10-09 23:41:09.898182

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = 'a58c14fe9514'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Crea la tabla ``usuarios`` y el índice único del correo."""
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('apellido', sa.String(length=100), nullable=False),
    sa.Column('correo', sa.String(length=254), nullable=False),
    sa.Column('hash_contrasenia', sa.String(length=60), nullable=False),
    sa.Column('perfil', sa.String(length=20), nullable=False),
    sa.Column('colegio', sa.String(length=150), nullable=True),
    sa.Column('empresa', sa.String(length=150), nullable=True),
    sa.Column('rol', sa.String(length=20), nullable=False),
    sa.Column('version_terminos', sa.String(length=20), nullable=False),
    sa.Column('aceptacion_terminos_en', sa.DateTime(), nullable=False),
    sa.Column('correo_verificado_en', sa.DateTime(), nullable=True),
    sa.Column('intentos_fallidos', sa.Integer(), nullable=False),
    sa.Column('bloqueado_hasta', sa.DateTime(), nullable=True),
    sa.Column('version_sesion', sa.Integer(), nullable=False),
    sa.Column('creado_en', sa.DateTime(), nullable=False),
    sa.Column('actualizado_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("perfil IN ('abogado', 'aseguradora')", name='ck_usuarios_perfil'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_usuarios_correo'), ['correo'], unique=True)


def downgrade():
    """Elimina la tabla ``usuarios``."""
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_usuarios_correo'))

    op.drop_table('usuarios')
