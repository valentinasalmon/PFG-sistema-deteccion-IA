"""Sello de tiempo de las imágenes en Hedera (funcionalidades 016 y 023).

Cada imagen cargada queda ``pendiente``. El servicio pide el sello (solo la
huella SHA-256), la imagen pasa a ``enviado`` con el recibo de Hedera y,
cuando el mensaje aparece en el *mirror node*, a ``sellado`` con la
referencia y la fecha de consenso. Si Hedera no responde se reintenta en
cada pasada de la tarea programada; después de ``MAXIMO_INTENTOS`` queda
``fallido``. Nada de esto impide cargar ni analizar.

Realiza: RF37 (CA1 a CA3); RNF20 (CA1).
"""
import logging

from app.integraciones.sello_tiempo import SelloNoDisponible
from app.servicios import auditoria

SELLO_PENDIENTE = "pendiente"
SELLO_ENVIADO = "enviado"
SELLO_SELLADO = "sellado"
SELLO_FALLIDO = "fallido"
# La tarea corre cada 15 minutos: 96 intentos son unas 24 horas de reintentos.
MAXIMO_INTENTOS = 96

registro_log = logging.getLogger(__name__)


class ServicioSellos:
    """Pide, confirma y reintenta los sellos de tiempo."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, sellador, registro, repositorio_informes=None,
        repositorio_versiones=None,
    ):
        """
        Args:
            repositorio: ``RepositorioImagenes``.
            repositorio_informes: ``RepositorioInformes``, para sellar también la
                huella de los informes PDF (funcionalidad 026).
            repositorio_versiones: ``RepositorioVersiones``, para sellar la huella de
                cada versión desplegada (funcionalidad 029).
            sellador: implementación de ``app.integraciones.sello_tiempo``, o
                None si el sellado está desactivado.
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.sellador = sellador
        self.registro = registro
        self.repositorio_informes = repositorio_informes
        self.repositorio_versiones = repositorio_versiones

    @property
    def activo(self):
        """True si hay un sellador configurado."""
        return self.sellador is not None

    def intentar(self, imagen):
        """Avanza un paso el sello de una imagen o de un informe; nunca lanza (RF37 CA3).

        Funciona con cualquier objeto con ``huella``, ``id_caso`` y las columnas
        ``sello_*``; ``TIPO_SELLO`` indica qué se publica (``"informe"`` en la 026).
        """
        if not self.activo or imagen.sello_estado in (SELLO_SELLADO, SELLO_FALLIDO):
            return imagen.sello_estado
        try:
            if imagen.sello_estado in (None, SELLO_PENDIENTE):
                tipo = getattr(imagen, "TIPO_SELLO", "imagen")
                imagen.sello_recibo = (
                    self.sellador.sellar(imagen.huella) if tipo == "imagen"
                    else self.sellador.sellar(imagen.huella, tipo=tipo)
                )
                imagen.sello_estado = SELLO_ENVIADO
                imagen.sello_simulado = self.sellador.simulado
            confirmacion = self.sellador.verificar(imagen.huella, imagen.sello_recibo)
            if confirmacion is not None:
                imagen.sello_estado = SELLO_SELLADO
                imagen.sello_referencia = confirmacion.referencia
                imagen.sello_fecha = confirmacion.fecha
                if confirmacion.recibo:
                    imagen.sello_recibo = confirmacion.recibo
                self.registro.registrar(
                    auditoria.IMAGEN_SELLO, auditoria.EXITOSO,
                    recurso=(
                        (auditoria.TIPO_CASO, imagen.id_caso) if hasattr(imagen, "id_caso")
                        else (auditoria.TIPO_VERSION, imagen.id)
                    ),
                    detalle={"sha256": imagen.huella, "referencia": confirmacion.referencia,
                             "simulado": imagen.sello_simulado,
                             "tipo": getattr(imagen, "TIPO_SELLO", "imagen")},
                )
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
        if not self.activo:
            return {"sellados": 0, "en_curso": 0}
        en_curso_estados = (SELLO_PENDIENTE, SELLO_ENVIADO)
        pendientes = list(self.repositorio.con_sello_en_curso(en_curso_estados))
        for extra in (self.repositorio_informes, self.repositorio_versiones):
            if extra is not None:
                pendientes += extra.con_sello_en_curso(en_curso_estados)
        for imagen in pendientes:
            estado = self.intentar(imagen)
            if estado == SELLO_SELLADO:
                sellados += 1
            elif estado in (SELLO_PENDIENTE, SELLO_ENVIADO):
                en_curso += 1
        return {"sellados": sellados, "en_curso": en_curso}
