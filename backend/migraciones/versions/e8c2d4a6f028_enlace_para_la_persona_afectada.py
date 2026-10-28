"""Enlace para la persona afectada y origen de cada imagen (funcionalidad 028).

Revision ID: e8c2d4a6f028
Revises: d1a7b3c5e027
Create Date: 2026-10-28 18:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'e8c2d4a6f028'
down_revision = 'd1a7b3c5e027'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega el tipo de enlace, su destinatario y la declaración, y el origen de la imagen."""
    with op.batch_alter_table('enlaces_carga') as tabla:
        tabla.add_column(sa.Column(
            'tipo', sa.String(length=20), nullable=False, server_default='celular'
        ))
        tabla.add_column(sa.Column('destinatario', sa.String(length=100), nullable=True))
        tabla.add_column(sa.Column('declaracion_aceptada_en', sa.DateTime(), nullable=True))
        tabla.create_check_constraint(
            'ck_enlaces_carga_tipo', "tipo IN ('celular', 'persona_afectada')"
        )
    with op.batch_alter_table('imagenes') as tabla:
        tabla.add_column(sa.Column('origen', sa.String(length=20), nullable=True))


def downgrade():
    """Quita las columnas nuevas."""
    with op.batch_alter_table('imagenes') as tabla:
        tabla.drop_column('origen')
    with op.batch_alter_table('enlaces_carga') as tabla:
        tabla.drop_constraint('ck_enlaces_carga_tipo', type_='check')
        tabla.drop_column('declaracion_aceptada_en')
        tabla.drop_column('destinatario')
        tabla.drop_column('tipo')
