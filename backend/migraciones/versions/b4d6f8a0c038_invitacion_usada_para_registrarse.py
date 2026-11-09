"""Invitación usada para registrarse (funcionalidad 038).

Quien crea su cuenta desde el enlace de una invitación queda dentro de esa
organización al verificar el correo, también en un estudio jurídico. Se marca
la invitación usada para no sumar a la persona a otras organizaciones que la
hayan invitado sin que lo elija.

Revision ID: b4d6f8a0c038
Revises: a3c5e7f9b035
Create Date: 2026-11-06 18:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'b4d6f8a0c038'
down_revision = 'a3c5e7f9b035'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega ``invitaciones.usada_para_registrarse`` (falso por defecto)."""
    with op.batch_alter_table('invitaciones') as tabla:
        tabla.add_column(sa.Column(
            'usada_para_registrarse', sa.Boolean(), nullable=False, server_default=sa.false()
        ))


def downgrade():
    """Quita la marca."""
    with op.batch_alter_table('invitaciones') as tabla:
        tabla.drop_column('usada_para_registrarse')
