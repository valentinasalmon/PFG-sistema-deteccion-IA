"""Sello de tiempo de las imágenes en Blockchain Federal Argentina (funcionalidad 016).

Cada imagen cargada queda ``pendiente``. El servicio pide el sello (solo la
huella SHA-256), la imagen pasa a ``enviado`` con el recibo de BFA y, cuando
BFA la incluye en un bloque, a ``sellado`` con la referencia y la fecha. Si BFA
no responde se reintenta en cada pasada de la tarea programada; después de
``MAXIMO_INTENTOS`` queda ``fallido``. Nada de esto impide cargar ni analizar.

En el modo ``navegador`` el servidor no llama a BFA: el navegador pide el
sello y la confirmación, y este servicio valida y guarda los recibos con
``registrar_desde_navegador``.

Realiza: RF37 (CA1 a CA3); RNF20 (CA1).
"""
import logging

from app.integraciones.sello_tiempo import (
    SelloNoDisponible,
    fecha_bfa,
    leer_recibo_definitivo,
    leer_recibo_temporal,
)
from app.servicios import auditoria
from app.servicios.errores import ConflictoDatos, ErrorValidacion

SELLO_PENDIENTE = "pendiente"
SELLO_ENVIADO = "enviado"
SELLO_SELLADO = "sellado"
SELLO_FALLIDO = "fallido"
# La tarea corre cada 15 minutos: 96 intentos son unas 24 horas de reintentos.
MAXIMO_INTENTOS = 96

registro_log = logging.getLogger(__name__)


class ServicioSellos:
    """Pide, confirma y reintenta los sellos de tiempo."""

    def __init__(self, repositorio, sellador, registro):
        """
        Args:
            repositorio: ``RepositorioImagenes``.
            sellador: implementación de ``app.integraciones.sello_tiempo``, o
                None si el sellado está desactivado.
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.sellador = sellador
        self.registro = registro

    @property
    def activo(self):
        """True si hay un sellador configurado."""
        return self.sellador is not None

    @property
    def en_navegador(self):
        """True si el sello lo pide el navegador y no el servidor."""
        return self.activo and not getattr(self.sellador, "en_servidor", True)

    def intentar(self, imagen):
        """Avanza el sello de una imagen un paso; nunca lanza (RF37 CA3)."""
        if (not self.activo or self.en_navegador
                or imagen.sello_estado in (SELLO_SELLADO, SELLO_FALLIDO)):
            return imagen.sello_estado
        try:
            if imagen.sello_estado in (None, SELLO_PENDIENTE):
                imagen.sello_recibo = self.sellador.sellar(imagen.huella)
                imagen.sello_estado = SELLO_ENVIADO
                imagen.sello_simulado = self.sellador.simulado
            confirmacion = self.sellador.verificar(imagen.huella, imagen.sello_recibo)
            if confirmacion is not None:
                imagen.sello_estado = SELLO_SELLADO
                imagen.sello_referencia = confirmacion.referencia
                imagen.sello_fecha = confirmacion.fecha
                if confirmacion.recibo:
                    imagen.sello_recibo = confirmacion.recibo
                self._auditar_sello(imagen, "servidor")
        except SelloNoDisponible as falla:
            imagen.sello_intentos = (imagen.sello_intentos or 0) + 1
            if imagen.sello_estado is None:
                imagen.sello_estado = SELLO_PENDIENTE
            if imagen.sello_intentos >= MAXIMO_INTENTOS:
                imagen.sello_estado = SELLO_FALLIDO
            registro_log.warning("Sello de la imagen %s no disponible: %s", imagen.id, falla)
        self.repositorio.confirmar()
        return imagen.sello_estado

    def procesar(self):
        """Tarea programada: avanza todos los sellos pendientes o enviados.

        Returns:
            Diccionario con la cantidad de ``sellados`` y de ``en_curso``.
        """
        sellados = en_curso = 0
        if not self.activo or self.en_navegador:
            return {"sellados": 0, "en_curso": 0}
        for imagen in self.repositorio.con_sello_en_curso((SELLO_PENDIENTE, SELLO_ENVIADO)):
            estado = self.intentar(imagen)
            if estado == SELLO_SELLADO:
                sellados += 1
            elif estado in (SELLO_PENDIENTE, SELLO_ENVIADO):
                en_curso += 1
        return {"sellados": sellados, "en_curso": en_curso}

    def registrar_desde_navegador(self, imagen, recibo=None, recibo_definitivo=None, fecha=None):
        """Guarda lo que obtuvo el navegador de BFA, después de validarlo.

        Args:
            imagen: ``Imagen`` a la que pertenece el sello.
            recibo: recibo temporal que devolvió ``stamp``; pasa la imagen a
                ``enviado``.
            recibo_definitivo: recibo que devolvió ``verify``; se comprueba
                que contiene la huella de la imagen y de él sale el bloque.
            fecha: ``attestation_time`` informado por BFA.

        Raises:
            ConflictoDatos: si el sello no se gestiona desde el navegador.
            ErrorValidacion: si el recibo no es de BFA o no es de esta imagen.
        """
        if not self.en_navegador:
            raise ConflictoDatos(
                "El sello de tiempo lo gestiona el servidor.", codigo="sello_servidor"
            )
        if imagen.sello_estado == SELLO_SELLADO:
            return imagen
        try:
            if recibo_definitivo:
                bloque = leer_recibo_definitivo(recibo_definitivo, imagen.huella)
                imagen.sello_estado = SELLO_SELLADO
                imagen.sello_recibo = recibo_definitivo
                imagen.sello_referencia = f"BFA bloque {bloque}"
                imagen.sello_fecha = fecha_bfa(fecha)
                imagen.sello_simulado = False
                self._auditar_sello(imagen, "navegador")
            elif recibo:
                imagen.sello_recibo = leer_recibo_temporal(recibo)
                imagen.sello_estado = SELLO_ENVIADO
                imagen.sello_simulado = False
            else:
                raise ValueError("Falta el recibo de BFA.")
        except ValueError as falla:
            raise ErrorValidacion(str(falla), {"recibo": str(falla)}) from falla
        self.repositorio.confirmar()
        return imagen

    def _auditar_sello(self, imagen, origen):
        self.registro.registrar(
            auditoria.IMAGEN_SELLO, auditoria.EXITOSO,
            recurso=(auditoria.TIPO_CASO, imagen.id_caso),
            detalle={"sha256": imagen.huella, "referencia": imagen.sello_referencia,
                     "simulado": imagen.sello_simulado, "origen": origen},
        )
