"""Crear la tabla de imágenes de los casos.

Funcionalidad 006 (carga de imágenes). Realiza: RF34 a RF36; RN23 (huella
SHA-256), RF34 CA4 (una imagen no se repite en un caso). Los archivos viven
en el almacenamiento (S3 o carpeta local); la tabla guarda sus datos técnicos.

Revision ID: 6df33b3b5d51
Revises: 057c1b5b72d9
Create Date: 2026-10-19 14:48:52.215548

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = '6df33b3b5d51'
down_revision = '057c1b5b72d9'
branch_labels = None
depends_on = None


def upgrade():
    """Crea la tabla ``imagenes`` con sus restricciones e índices."""
    op.create_table('imagenes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_caso', sa.Integer(), nullable=False),
    sa.Column('clave', sa.String(length=100), nullable=False),
    sa.Column('clave_miniatura', sa.String(length=100), nullable=False),
    sa.Column('nombre_original', sa.String(length=255), nullable=False),
    sa.Column('formato', sa.String(length=10), nullable=False),
    sa.Column('tamanio', sa.BigInteger(), nullable=False),
    sa.Column('ancho', sa.Integer(), nullable=False),
    sa.Column('alto', sa.Integer(), nullable=False),
    sa.Column('huella', sa.String(length=64), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('cargada_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("formato IN ('jpeg', 'png')", name='ck_imagenes_formato'),
    sa.ForeignKeyConstraint(['id_caso'], ['casos.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clave', name='uq_imagenes_clave'),
    sa.UniqueConstraint('clave_miniatura', name='uq_imagenes_clave_miniatura'),
    sa.UniqueConstraint('id_caso', 'huella', name='uq_imagenes_caso_huella')
    )
    with op.batch_alter_table('imagenes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_imagenes_huella'), ['huella'], unique=False)
        batch_op.create_index(batch_op.f('ix_imagenes_id_caso'), ['id_caso'], unique=False)


def downgrade():
    """Elimina la tabla ``imagenes`` (los archivos del almacenamiento no se tocan)."""
    with op.batch_alter_table('imagenes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_imagenes_id_caso'))
        batch_op.drop_index(batch_op.f('ix_imagenes_huella'))

    op.drop_table('imagenes')
