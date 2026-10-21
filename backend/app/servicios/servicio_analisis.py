"""Análisis de imágenes: pedido, procesamiento por capas, progreso e interrupciones.

El pedido se confirma en la base y recién después se encola, así el
trabajador nunca lee un análisis que todavía no existe. El procesamiento
recalcula la huella de cada imagen antes de analizarla (RF38 CA4), ejecuta
cada capa por separado (si una falla, queda "No disponible" y las demás
siguen: RN26) y confirma después de cada paso para que la pantalla muestre
el progreso (RF46). Este servicio no conoce Flask ni la cola concreta.

Al terminar genera el informe PDF (funcionalidad 008).

Realiza: RF38, RF39 (orquestación), RF43, RF44 (CA3), RF46; RN19, RN25 a
RN27, RN29; RNF07 (CA2).
"""
import hashlib
import logging
from uuid import uuid4

from app.analisis.base import CapaNoDisponible, ContextoImagen
from app.modelos.analisis import (
    ESTADO_EN_PROCESO,
    ESTADO_EN_COLA,
    ESTADO_FALLIDO,
    ESTADO_FINALIZADO,
    INTEGRIDAD_ALTERADA,
    INTEGRIDAD_VERIFICADA,
    RESULTADO_COMPLETADO,
    RESULTADO_NO_DISPONIBLE,
    Analisis,
    AnalisisImagen,
    Anomalia,
    ResultadoCapa,
)
from app.modelos.caso import (
    ESTADO_ANALIZADO,
    ESTADO_BORRADOR,
    ESTADO_EN_ANALISIS,
    NIVEL_COLABORACION,
    NIVEL_LECTURA,
)
from app.servicios import auditoria
from app.servicios.errores import ConflictoDatos, ErrorValidacion, NoEncontrado
from app.utilidades.tiempo import ahora_utc

registro_log = logging.getLogger(__name__)

ESTADOS_QUE_ADMITEN_ANALISIS = (ESTADO_BORRADOR, ESTADO_ANALIZADO)  # RF38 CA1, RN19
MOTIVO_INTERRUMPIDO = (
    "El procesamiento se interrumpió antes de terminar (por ejemplo, por un reinicio del "
    "servidor)."
)
MOTIVO_INESPERADO = "Ocurrió un error inesperado durante el procesamiento."


class ServicioAnalisis:
    """Pide, procesa y consulta los análisis de un caso."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, casos, imagenes, ejecucion, correos, configuracion, registro,
    ):
        """
        Args:
            repositorio: ``RepositorioAnalisis``.
            casos: ``ServicioCasos``, que resuelve los permisos sobre el caso.
            imagenes: ``RepositorioImagenes``.
            ejecucion: diccionario con ``capas`` (lista de ``CapaAnalisis``),
                ``almacenamiento`` (de donde se leen los originales), ``cola``
                (implementación de ``app.integraciones.cola``), ``trabajo``
                (ruta de importación de la función que procesa un análisis) e
                ``informes`` (``ServicioInformes``, que genera el PDF).
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.casos = casos
        self.imagenes = imagenes
        self.ejecucion = ejecucion
        self.correos = correos
        self.configuracion = configuracion
        self.registro = registro

    def _auditar(self, accion, resultado, usuario, caso, detalle, confirmar=False):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        return self.registro.registrar_en_caso(
            accion, resultado, usuario, caso, detalle, confirmar
        )

    def _rechazar(self, error, usuario, caso, motivo):
        self._auditar(
            auditoria.ANALISIS_SOLICITUD, auditoria.RECHAZADO, usuario, caso,
            {"motivo": motivo}, confirmar=True,
        )
        raise error

    # --- Pedido (RF38) ---

    def solicitar(self, id_caso, usuario, ids_imagenes):
        """Crea el análisis, pasa el caso a En análisis y lo encola (RF38 CA1 a CA3).

        Returns:
            El ``Analisis`` creado (en cola, o fallido si no se pudo encolar).
        """
        caso, _ = self.casos.caso_con_permiso(
            id_caso, usuario, NIVEL_COLABORACION, auditoria.ANALISIS_SOLICITUD
        )
        self.verificar_interrumpidos(caso)
        if self.repositorio.en_curso_de_caso(caso.id) or caso.estado == ESTADO_EN_ANALISIS:
            self._rechazar(ConflictoDatos(
                "El caso ya tiene un análisis en curso: vas a poder pedir otro cuando termine.",
                codigo="analisis_en_curso",
            ), usuario, caso, "en_curso")
        if caso.estado not in ESTADOS_QUE_ADMITEN_ANALISIS:
            self._rechazar(ConflictoDatos(
                "El caso no admite análisis en este estado. Si está cerrado o archivado, su "
                "Responsable tiene que reabrirlo.",
                codigo="caso_sin_analisis",
            ), usuario, caso, "estado")
        elegidas = self._imagenes_elegidas(caso, usuario, ids_imagenes)

        analisis = Analisis(
            id_caso=caso.id, id_solicitante=usuario.id, estado=ESTADO_EN_COLA,
            estado_anterior_caso=caso.estado,
            versiones={capa.nombre: capa.version() for capa in self.ejecucion["capas"]},
        )
        for orden, imagen in enumerate(elegidas, start=1):
            analisis.imagenes.append(AnalisisImagen(
                id_imagen=imagen.id, orden=orden, nombre=imagen.nombre_original,
                huella=imagen.huella,
            ))
        self.repositorio.preparar(analisis)
        caso.estado = ESTADO_EN_ANALISIS
        caso.actualizado_en = ahora_utc()
        self._auditar(
            auditoria.ANALISIS_SOLICITUD, auditoria.EXITOSO, usuario, caso,
            {"id_analisis": analisis.id, "imagenes": len(elegidas)},
        )
        self.repositorio.confirmar()
        try:
            self.ejecucion["cola"].encolar(self.ejecucion["trabajo"], analisis.id)
        except Exception:  # pylint: disable=broad-exception-caught
            registro_log.exception("No se pudo encolar el análisis %s", analisis.id)
            self._fallar(analisis.id, "No se pudo poner el análisis en la cola de trabajo.")
        return self.repositorio.obtener(analisis.id)

    def _imagenes_elegidas(self, caso, usuario, ids_imagenes):
        """Las imágenes pedidas, todas del caso y sin repetir (RF38 CA2)."""
        ids = list(dict.fromkeys(ids_imagenes or []))
        if not ids:
            mensaje = "Elegí al menos una imagen para analizar."
            self._rechazar(
                ErrorValidacion(mensaje, {"imagenes": mensaje}), usuario, caso, "sin_imagenes"
            )
        del_caso = {imagen.id: imagen for imagen in self.imagenes.de_caso(caso.id)}
        if any(id_imagen not in del_caso for id_imagen in ids):
            mensaje = "Alguna de las imágenes elegidas no pertenece a este caso."
            self._rechazar(
                ErrorValidacion(mensaje, {"imagenes": mensaje}), usuario, caso, "imagen_ajena"
            )
        return [del_caso[id_imagen] for id_imagen in ids]

    # --- Procesamiento (lo ejecuta la cola) ---

    def procesar(self, id_analisis):
        """Ejecuta las capas sobre cada imagen del análisis y registra el resultado.

        Si el análisis no existe o ya no está en cola (por ejemplo, porque se
        marcó como interrumpido), no hace nada.
        """
        analisis = self.repositorio.obtener(id_analisis)
        if analisis is None or analisis.estado != ESTADO_EN_COLA:
            return
        try:
            analisis.estado = ESTADO_EN_PROCESO
            analisis.iniciado_en = ahora_utc()
            self._avanzar(analisis)
            for posicion, incluida in enumerate(analisis.imagenes, start=1):
                analisis.imagen_actual = posicion
                analisis.capa_actual = None
                self._avanzar(analisis)
                self._procesar_imagen(analisis, incluida)
            self._finalizar(analisis)
        except Exception:  # pylint: disable=broad-exception-caught
            registro_log.exception("Falló el análisis %s", id_analisis)
            self.repositorio.descartar()
            self._fallar(id_analisis, MOTIVO_INESPERADO)

    def _avanzar(self, analisis):
        """Confirma el progreso; la marca de tiempo sirve para detectar interrupciones."""
        analisis.actualizado_en = ahora_utc()
        self.repositorio.confirmar()

    def _procesar_imagen(self, analisis, incluida):
        """Verifica la integridad de una imagen y le aplica cada capa."""
        imagen = incluida.imagen
        contenido = self.ejecucion["almacenamiento"].leer(imagen.clave) if imagen else b""
        if hashlib.sha256(contenido).hexdigest() != incluida.huella:
            incluida.integridad = INTEGRIDAD_ALTERADA
            self._auditar(
                auditoria.ANALISIS_INTEGRIDAD, auditoria.FALLIDO, analisis.solicitante,
                analisis.caso,
                {"id_analisis": analisis.id, "nombre": incluida.nombre, "sha256": incluida.huella},
            )
            self._avanzar(analisis)
            return
        incluida.integridad = INTEGRIDAD_VERIFICADA
        contexto = ContextoImagen(imagen.formato, imagen.ancho, imagen.alto, imagen.cargada_en)
        for capa in self.ejecucion["capas"]:
            analisis.capa_actual = capa.titulo
            self._avanzar(analisis)
            incluida.resultados.append(self._ejecutar_capa(capa, contenido, contexto))
            self._avanzar(analisis)

    def _ejecutar_capa(self, capa, contenido, contexto):
        """Resultado de una capa; si falla, "No disponible" con el motivo (RN26, RF43 CA3)."""
        version = capa.version()
        try:
            resultado = capa.analizar(contenido, contexto)
        except CapaNoDisponible as error:
            return ResultadoCapa(
                capa=capa.nombre, estado=RESULTADO_NO_DISPONIBLE, motivo=str(error),
                version=version,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            registro_log.exception("Falló la capa %s", capa.nombre)
            return ResultadoCapa(
                capa=capa.nombre, estado=RESULTADO_NO_DISPONIBLE,
                motivo="La capa falló de forma inesperada al procesar esta imagen.",
                version=version,
            )
        return ResultadoCapa(
            capa=capa.nombre, estado=RESULTADO_COMPLETADO, nivel=resultado.nivel,
            conclusion=resultado.conclusion, detalle=resultado.detalle, version=version,
            clave_imagen=self._guardar_imagen(resultado.imagen),
            anomalias=[
                Anomalia(
                    campo=a.campo[:100], valor=a.valor, descripcion=a.descripcion,
                    severidad=a.severidad,
                )
                for a in resultado.anomalias
            ],
        )

    def _guardar_imagen(self, imagen):
        """Guarda la imagen de un resultado (mapa ELA); si falla, el resultado sigue sin ella."""
        if not imagen:
            return None
        clave = f"analisis/{uuid4().hex}.png"
        try:
            self.ejecucion["almacenamiento"].guardar(clave, imagen, "image/png")
        except Exception:  # pylint: disable=broad-exception-caught
            registro_log.exception("No se pudo guardar la imagen del resultado %s", clave)
            return None
        return clave

    def _generar_informe(self, analisis):
        """Genera el informe PDF (008); si falla, el análisis igual finaliza (CA6 de la 008).

        Returns:
            True si el informe quedó generado.
        """
        analisis.capa_actual = "Informe PDF"
        self._avanzar(analisis)
        try:
            self.ejecucion["informes"].generar(analisis)
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            registro_log.exception("No se pudo generar el informe del análisis %s", analisis.id)
            self.repositorio.descartar()
            return False

    def _finalizar(self, analisis):
        """Informe, análisis Finalizado, caso Analizado, auditoría y correo (CA7)."""
        con_informe = self._generar_informe(analisis)
        analisis = self.repositorio.obtener(analisis.id)
        caso = analisis.caso
        analisis.estado = ESTADO_FINALIZADO
        analisis.capa_actual = None
        analisis.finalizado_en = ahora_utc()
        caso.estado = ESTADO_ANALIZADO
        caso.actualizado_en = ahora_utc()
        alteradas = sum(1 for i in analisis.imagenes if i.integridad == INTEGRIDAD_ALTERADA)
        self._auditar(
            auditoria.ANALISIS_FINALIZACION, auditoria.EXITOSO, analisis.solicitante, caso,
            {"id_analisis": analisis.id, "imagenes": len(analisis.imagenes),
             "integridad_alterada": alteradas, "informe": con_informe},
        )
        self._avanzar(analisis)
        for usuario in _destinatarios_del_aviso(analisis, caso):
            self.correos.enviar_aviso_analisis_finalizado(
                usuario, caso, len(analisis.imagenes), con_informe
            )

    def _fallar(self, id_analisis, motivo):
        """Análisis Fallido, el caso vuelve a su estado anterior y se avisa (RF46 CA2)."""
        analisis = self.repositorio.obtener(id_analisis)
        caso = analisis.caso
        analisis.estado = ESTADO_FALLIDO
        analisis.motivo_falla = motivo
        analisis.capa_actual = None
        analisis.finalizado_en = ahora_utc()
        if caso.estado == ESTADO_EN_ANALISIS:
            caso.estado = analisis.estado_anterior_caso
            caso.actualizado_en = ahora_utc()
        self._auditar(
            auditoria.ANALISIS_FALLA, auditoria.FALLIDO, analisis.solicitante, caso,
            {"id_analisis": analisis.id, "motivo": motivo},
        )
        self._avanzar(analisis)
        for usuario in _destinatarios_del_aviso(analisis, caso):
            self.correos.enviar_aviso_analisis_fallido(usuario, caso, motivo)

    def verificar_interrumpidos(self, caso):
        """Marca como Fallido el análisis en curso que dejó de avanzar (RF46 CA2)."""
        analisis = self.repositorio.en_curso_de_caso(caso.id)
        if analisis is None:
            return
        if ahora_utc() - analisis.actualizado_en > self.configuracion["TIEMPO_MAXIMO_SIN_AVANCE"]:
            self._fallar(analisis.id, MOTIVO_INTERRUMPIDO)

    # --- Consultas (RF43, RF46) ---

    def listar(self, id_caso, usuario):
        """Historial de análisis del caso, del más reciente al más antiguo (RN25)."""
        caso, _ = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_LECTURA)
        self.verificar_interrumpidos(caso)
        return self.repositorio.de_caso(caso.id)

    def enlaces_de_imagenes(self, analisis):
        """Enlaces firmados de las imágenes de los resultados, por id de resultado (RNF03 CA2)."""
        segundos = int(self.configuracion["VIGENCIA_ENLACE_ARCHIVO"].total_seconds())
        return {
            resultado.id: self.ejecucion["almacenamiento"].enlace(resultado.clave_imagen, segundos)
            for incluida in analisis.imagenes
            for resultado in incluida.resultados
            if resultado.clave_imagen
        }

    def detalle(self, id_caso, id_analisis, usuario):
        """Estado, progreso y resultados de un análisis del caso."""
        caso, _ = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_LECTURA)
        self.verificar_interrumpidos(caso)
        analisis = self.repositorio.obtener(id_analisis)
        if analisis is None or analisis.id_caso != caso.id:
            raise NoEncontrado("El análisis no existe o no tenés acceso a él.")
        return analisis


def _destinatarios_del_aviso(analisis, caso):
    """Quien pidió el análisis y el Responsable del caso, sin repetir (RF47)."""
    destinatarios = []
    for usuario in (analisis.solicitante, caso.responsable):
        if usuario is not None and usuario not in destinatarios:
            destinatarios.append(usuario)
    return destinatarios
