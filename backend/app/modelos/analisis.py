"""Análisis de imágenes: el pedido, las imágenes incluidas y los resultados por capa.

``Analisis`` registra el pedido y su progreso; ``AnalisisImagen`` conserva el
nombre y la huella de cada imagen aunque después se elimine; ``ResultadoCapa``
guarda el nivel de indicio, la conclusión y el detalle de cada capa, y
``Anomalia``, cada hallazgo. No existe un resultado que combine capas (RN27).

Realiza: RF38, RF39, RF43, RF46; RN25 a RN27, RN29. Se basa en los modelos
``ResultadoAnalisis`` y ``AnomaliaDetectada`` del repositorio anterior (TIF),
sin ``ConclusionFinal`` (ADR-0006).
"""
from app.extensiones import db
from app.utilidades.tiempo import ahora_utc

ESTADO_EN_COLA = "en_cola"
ESTADO_EN_PROCESO = "en_proceso"
ESTADO_FINALIZADO = "finalizado"
ESTADO_FALLIDO = "fallido"
ESTADOS_ANALISIS = (ESTADO_EN_COLA, ESTADO_EN_PROCESO, ESTADO_FINALIZADO, ESTADO_FALLIDO)
ESTADOS_EN_CURSO = (ESTADO_EN_COLA, ESTADO_EN_PROCESO)

INTEGRIDAD_VERIFICADA = "verificada"
INTEGRIDAD_ALTERADA = "alterada"
INTEGRIDADES = (INTEGRIDAD_VERIFICADA, INTEGRIDAD_ALTERADA)

RESULTADO_COMPLETADO = "completado"
RESULTADO_NO_DISPONIBLE = "no_disponible"
ESTADOS_RESULTADO = (RESULTADO_COMPLETADO, RESULTADO_NO_DISPONIBLE)

SEVERIDADES = ("directo", "fuerte", "moderado", "debil", "neutro")


class Analisis(db.Model):  # pylint: disable=too-few-public-methods
    """Pedido de análisis de imágenes de un caso, con su estado y progreso (RF46)."""

    __tablename__ = "analisis"
    __table_args__ = (
        db.CheckConstraint(f"estado IN {ESTADOS_ANALISIS}", name="ck_analisis_estado"),
        db.Index("ix_analisis_caso", "id_caso"),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_caso = db.Column(db.Integer, db.ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    id_solicitante = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    estado = db.Column(db.String(20), nullable=False, default=ESTADO_EN_COLA)
    # Estado del caso antes del análisis, para volver a él si falla (RF46 CA2).
    estado_anterior_caso = db.Column(db.String(20), nullable=False)
    imagen_actual = db.Column(db.Integer, nullable=False, default=0)
    capa_actual = db.Column(db.String(40), nullable=True)
    motivo_falla = db.Column(db.String(300), nullable=True)
    versiones = db.Column(db.JSON, nullable=False, default=dict)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    iniciado_en = db.Column(db.DateTime, nullable=True)
    finalizado_en = db.Column(db.DateTime, nullable=True)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)

    caso = db.relationship("Caso", back_populates="analisis")
    solicitante = db.relationship("Usuario")
    imagenes = db.relationship(
        "AnalisisImagen", back_populates="analisis", cascade="all, delete-orphan",
        order_by="AnalisisImagen.orden",
    )
    informe = db.relationship(
        "Informe", back_populates="analisis", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def en_curso(self):
        """True mientras el análisis está en cola o en proceso."""
        return self.estado in ESTADOS_EN_CURSO


class AnalisisImagen(db.Model):  # pylint: disable=too-few-public-methods
    """Imagen incluida en un análisis, con su verificación de integridad (RF38 CA4)."""

    __tablename__ = "analisis_imagenes"
    __table_args__ = (
        db.CheckConstraint(
            f"integridad IS NULL OR integridad IN {INTEGRIDADES}",
            name="ck_analisis_imagenes_integridad",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_analisis = db.Column(
        db.Integer, db.ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    id_imagen = db.Column(
        db.Integer, db.ForeignKey("imagenes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    orden = db.Column(db.Integer, nullable=False)
    # Se copian para conservarlos aunque la imagen se elimine después.
    nombre = db.Column(db.String(255), nullable=False)
    huella = db.Column(db.String(64), nullable=False)
    integridad = db.Column(db.String(20), nullable=True)

    analisis = db.relationship("Analisis", back_populates="imagenes")
    imagen = db.relationship("Imagen")
    resultados = db.relationship(
        "ResultadoCapa", back_populates="analisis_imagen", cascade="all, delete-orphan",
        order_by="ResultadoCapa.id",
    )


class ResultadoCapa(db.Model):  # pylint: disable=too-few-public-methods
    """Resultado de una capa sobre una imagen: nivel, conclusión y detalle (RF43)."""

    __tablename__ = "resultados_capa"
    __table_args__ = (
        db.CheckConstraint(f"estado IN {ESTADOS_RESULTADO}", name="ck_resultados_capa_estado"),
        db.CheckConstraint(
            "nivel IS NULL OR (nivel >= 0 AND nivel <= 100)", name="ck_resultados_capa_nivel"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_analisis_imagen = db.Column(
        db.Integer, db.ForeignKey("analisis_imagenes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    capa = db.Column(db.String(40), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    nivel = db.Column(db.Integer, nullable=True)
    conclusion = db.Column(db.Text, nullable=True)
    motivo = db.Column(db.String(300), nullable=True)
    detalle = db.Column(db.JSON, nullable=False, default=dict)
    version = db.Column(db.String(100), nullable=False)
    # Imagen que acompaña al resultado en el almacenamiento (mapa ELA, 011).
    clave_imagen = db.Column(db.String(200), nullable=True)

    analisis_imagen = db.relationship("AnalisisImagen", back_populates="resultados")
    anomalias = db.relationship(
        "Anomalia", back_populates="resultado", cascade="all, delete-orphan",
        order_by="Anomalia.id",
    )


class Anomalia(db.Model):  # pylint: disable=too-few-public-methods
    """Hallazgo de una capa, con su severidad."""

    __tablename__ = "anomalias"
    __table_args__ = (
        db.CheckConstraint(f"severidad IN {SEVERIDADES}", name="ck_anomalias_severidad"),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_resultado = db.Column(
        db.Integer, db.ForeignKey("resultados_capa.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    campo = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Text, nullable=True)
    descripcion = db.Column(db.Text, nullable=False)
    severidad = db.Column(db.String(20), nullable=False)

    resultado = db.relationship("ResultadoCapa", back_populates="anomalias")
