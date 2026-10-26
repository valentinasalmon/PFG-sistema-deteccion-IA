"""Aceptar imágenes HEIC (funcionalidad 024).

Las fotos del iPhone se guardan por defecto en HEIC: se agrega ese valor a la
restricción del formato de las imágenes.

Revision ID: f6b2a1d4c024
Revises: e5a1f0c3b016
Create Date: 2026-10-25 23:30:00
"""
from alembic import op

revision = 'f6b2a1d4c024'
down_revision = 'e5a1f0c3b016'
branch_labels = None
depends_on = None


def upgrade():
    """Amplía ``ck_imagenes_formato`` con ``heic``."""
    with op.batch_alter_table('imagenes') as tabla:
        tabla.drop_constraint('ck_imagenes_formato', type_='check')
        tabla.create_check_constraint('ck_imagenes_formato', "formato IN ('jpeg', 'png', 'heic')")


def downgrade():
    """Vuelve a aceptar solo JPEG y PNG (falla si ya hay imágenes HEIC)."""
    with op.batch_alter_table('imagenes') as tabla:
        tabla.drop_constraint('ck_imagenes_formato', type_='check')
        tabla.create_check_constraint('ck_imagenes_formato', "formato IN ('jpeg', 'png')")
