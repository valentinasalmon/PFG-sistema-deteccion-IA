"""Crear las tablas de análisis, imágenes analizadas, resultados por capa y anomalías.

Funcionalidad 007 (motor de análisis y capa de metadatos). Realiza: RF38,
RF39, RF43, RF46; RN25 a RN27, RN29. No hay tabla de conclusión combinada
(RN27, ADR-0006).

Revision ID: 161ae29f2074
Revises: 6df33b3b5d51
Create Date: 2026-10-19 16:51:54.108656

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de la revisión, usados por Alembic.
revision = '161ae29f2074'
down_revision = '6df33b3b5d51'
branch_labels = None
depends_on = None


def upgrade():
    """Crea las cuatro tablas del análisis con sus restricciones e índices."""
    op.create_table('analisis',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_caso', sa.Integer(), nullable=False),
    sa.Column('id_solicitante', sa.Integer(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('estado_anterior_caso', sa.String(length=20), nullable=False),
    sa.Column('imagen_actual', sa.Integer(), nullable=False),
    sa.Column('capa_actual', sa.String(length=40), nullable=True),
    sa.Column('motivo_falla', sa.String(length=300), nullable=True),
    sa.Column('versiones', sa.JSON(), nullable=False),
    sa.Column('creado_en', sa.DateTime(), nullable=False),
    sa.Column('iniciado_en', sa.DateTime(), nullable=True),
    sa.Column('finalizado_en', sa.DateTime(), nullable=True),
    sa.Column('actualizado_en', sa.DateTime(), nullable=False),
    sa.CheckConstraint("estado IN ('en_cola', 'en_proceso', 'finalizado', 'fallido')", name='ck_analisis_estado'),
    sa.ForeignKeyConstraint(['id_caso'], ['casos.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_solicitante'], ['usuarios.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('analisis', schema=None) as batch_op:
        batch_op.create_index('ix_analisis_caso', ['id_caso'], unique=False)

    op.create_table('analisis_imagenes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_analisis', sa.Integer(), nullable=False),
    sa.Column('id_imagen', sa.Integer(), nullable=True),
    sa.Column('orden', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('huella', sa.String(length=64), nullable=False),
    sa.Column('integridad', sa.String(length=20), nullable=True),
    sa.CheckConstraint("integridad IS NULL OR integridad IN ('verificada', 'alterada')", name='ck_analisis_imagenes_integridad'),
    sa.ForeignKeyConstraint(['id_analisis'], ['analisis.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_imagen'], ['imagenes.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('analisis_imagenes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_analisis_imagenes_id_analisis'), ['id_analisis'], unique=False)
        batch_op.create_index(batch_op.f('ix_analisis_imagenes_id_imagen'), ['id_imagen'], unique=False)

    op.create_table('resultados_capa',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_analisis_imagen', sa.Integer(), nullable=False),
    sa.Column('capa', sa.String(length=40), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('nivel', sa.Integer(), nullable=True),
    sa.Column('conclusion', sa.Text(), nullable=True),
    sa.Column('motivo', sa.String(length=300), nullable=True),
    sa.Column('detalle', sa.JSON(), nullable=False),
    sa.Column('version', sa.String(length=100), nullable=False),
    sa.CheckConstraint("estado IN ('completado', 'no_disponible')", name='ck_resultados_capa_estado'),
    sa.CheckConstraint('nivel IS NULL OR (nivel >= 0 AND nivel <= 100)', name='ck_resultados_capa_nivel'),
    sa.ForeignKeyConstraint(['id_analisis_imagen'], ['analisis_imagenes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('resultados_capa', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_resultados_capa_id_analisis_imagen'), ['id_analisis_imagen'], unique=False)

    op.create_table('anomalias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_resultado', sa.Integer(), nullable=False),
    sa.Column('campo', sa.String(length=100), nullable=False),
    sa.Column('valor', sa.Text(), nullable=True),
    sa.Column('descripcion', sa.Text(), nullable=False),
    sa.Column('severidad', sa.String(length=20), nullable=False),
    sa.CheckConstraint("severidad IN ('directo', 'fuerte', 'moderado', 'debil', 'neutro')", name='ck_anomalias_severidad'),
    sa.ForeignKeyConstraint(['id_resultado'], ['resultados_capa.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('anomalias', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_anomalias_id_resultado'), ['id_resultado'], unique=False)


def downgrade():
    """Elimina las tablas del análisis en el orden inverso."""
    with op.batch_alter_table('anomalias', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_anomalias_id_resultado'))

    op.drop_table('anomalias')
    with op.batch_alter_table('resultados_capa', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_resultados_capa_id_analisis_imagen'))

    op.drop_table('resultados_capa')
    with op.batch_alter_table('analisis_imagenes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_analisis_imagenes_id_imagen'))
        batch_op.drop_index(batch_op.f('ix_analisis_imagenes_id_analisis'))

    op.drop_table('analisis_imagenes')
    with op.batch_alter_table('analisis', schema=None) as batch_op:
        batch_op.drop_index('ix_analisis_caso')

    op.drop_table('analisis')
