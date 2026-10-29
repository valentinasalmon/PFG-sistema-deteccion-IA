"""Imágenes de los casos: carga, consulta, enlaces y eliminación.

La huella SHA-256 se calcula al recibir el archivo, antes de cualquier
procesamiento, y el original se guarda tal cual (RN23). Los permisos son los
del caso: el Responsable y los Colaboradores cargan y eliminan; el Lector
solo consulta; sin permiso, el caso no existe (RN20, RNF05).

Los archivos se escriben en el almacenamiento antes de confirmar la base y
se borran después de confirmarla: si la base falla, se borran los archivos
recién escritos; si falla el borrado de un archivo, queda en el log.

Realiza: RF34 a RF36; RN15 (imágenes por caso), RN19 a RN24; RNF06, RNF07.
"""
import hashlib
import logging
from uuid import uuid4

from app.integraciones.almacenamiento import ArchivoNoDisponible, disposicion_de_descarga
from app.modelos.caso import ESTADO_ANALIZADO, ESTADO_BORRADOR, NIVEL_COLABORACION, NIVEL_LECTURA
from app.modelos.imagen import ORIGEN_COMPUTADORA, TIPOS_MIME, Imagen
from app.servicios import auditoria
from app.servicios.errores import ConflictoDatos, ErrorValidacion, NoEncontrado
from app.utilidades import imagenes as lector
from app.utilidades.tiempo import ahora_utc

registro_log = logging.getLogger(__name__)

ESTADOS_CON_CARGA = (ESTADO_BORRADOR, ESTADO_ANALIZADO)  # RN19
MEGABYTE = 1024 * 1024


class ArchivosDeCasos:
    """Borra del almacenamiento los archivos de los casos que se eliminan (RN21).

    Quien elimina casos llama a ``preparar`` antes de quitarlos (para saber
    qué archivos tenían y registrar sus huellas) y a ``borrar_pendientes``
    después de confirmar la base.
    """

    def __init__(self, repositorio, almacenamiento, informes=None, analisis=None):
        """
        Args:
            repositorio: ``RepositorioImagenes``.
            informes: ``RepositorioInformes``, para borrar también los PDF (008).
            analisis: ``RepositorioAnalisis``, para borrar los mapas ELA (011).
        """
        self.repositorio = repositorio
        self.almacenamiento = almacenamiento
        self.informes = informes
        self.analisis = analisis
        self.pendientes = []

    def preparar(self, casos):
        """Anota los archivos de los casos (imágenes, PDF y mapas) y devuelve sus huellas."""
        ids = [caso.id for caso in casos]
        imagenes = self.repositorio.de_casos(ids)
        informes = self.informes.de_casos(ids) if self.informes else []
        for imagen in imagenes:
            self.pendientes.extend((imagen.clave, imagen.clave_miniatura))
        self.pendientes.extend(informe.clave for informe in informes)
        if self.analisis:
            self.pendientes.extend(self.analisis.claves_de_imagenes_de_casos(ids))
        return [imagen.huella for imagen in imagenes] + [informe.huella for informe in informes]

    def borrar_pendientes(self):
        """Borra los archivos anotados; una falla queda en el log y no se propaga."""
        pendientes, self.pendientes = self.pendientes, []
        for clave in pendientes:
            borrar_sin_fallar(self.almacenamiento, clave)


def borrar_sin_fallar(almacenamiento, clave):
    """Borra un archivo; si falla, lo deja en el log para borrarlo a mano."""
    try:
        almacenamiento.eliminar(clave)
    except Exception:  # pylint: disable=broad-exception-caught
        registro_log.exception("No se pudo borrar el archivo %s del almacenamiento", clave)


class ServicioImagenes:
    """Operaciones sobre las imágenes de un caso."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, casos, almacenamiento, configuracion, registro, sellos=None,
    ):
        """
        Args:
            repositorio: ``RepositorioImagenes``.
            casos: ``ServicioCasos``, que resuelve los permisos sobre el caso.
            almacenamiento: implementación de ``app.integraciones.almacenamiento``.
            registro: ``ServicioAuditoria``.
            sellos: ``ServicioSellos`` (funcionalidad 016); opcional.
        """
        self.sellos = sellos
        self.repositorio = repositorio
        self.casos = casos
        self.almacenamiento = almacenamiento
        self.configuracion = configuracion
        self.registro = registro

    # --- Auxiliares ---

    def _auditar(self, accion, resultado, usuario, caso, detalle, confirmar=False):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        return self.registro.registrar_en_caso(
            accion, resultado, usuario, caso, detalle, confirmar
        )

    def _rechazar(self, error, accion, usuario, caso, detalle):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        self._auditar(accion, auditoria.RECHAZADO, usuario, caso, detalle, confirmar=True)
        raise error

    def _para_modificar(self, id_caso, usuario, accion):
        """El caso, si el usuario es Responsable o Colaborador y el caso admite cambios (RN19)."""
        caso, _ = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_COLABORACION, accion)
        if caso.estado not in ESTADOS_CON_CARGA:
            self._rechazar(
                ConflictoDatos(
                    "El caso no admite cambios en sus imágenes en este estado. "
                    "Si está cerrado o archivado, su Responsable tiene que reabrirlo.",
                    codigo="caso_solo_lectura",
                ),
                accion, usuario, caso, {"motivo": "estado", "estado": caso.estado},
            )
        return caso

    def caso_para_cargar(self, id_caso, usuario, accion):
        """El caso, si el usuario puede cargarle imágenes ahora (RN19, RN20)."""
        return self._para_modificar(id_caso, usuario, accion)

    @staticmethod
    def puede_modificar(caso, permiso):
        """True si el permiso y el estado del caso permiten cargar y eliminar (RN19, RN20)."""
        return permiso != NIVEL_LECTURA and caso.estado in ESTADOS_CON_CARGA

    def limite_de_imagenes(self, caso):
        """Máximo de imágenes por caso según el plan del espacio (RN15, CP-02)."""
        if caso.es_personal:
            return self.configuracion["PLAN_PERSONAL"]["imagenes_por_caso"]
        return self.configuracion["PLANES"][caso.organizacion.plan]["imagenes_por_caso"]

    def _imagen_de(self, caso, id_imagen):
        imagen = self.repositorio.obtener(id_imagen)
        if imagen is None or imagen.id_caso != caso.id:
            raise NoEncontrado("La imagen no existe o no tenés acceso a ella.")
        return imagen

    # --- Cargar (RF34) ---

    def _validar_archivo(self, caso, usuario, nombre, contenido):
        """Tamaño, formato real, integridad, duplicado y límite del plan.

        Returns:
            ``(huella, formato, ancho, alto)``.
        """
        maximo = self.configuracion["TAMANIO_MAXIMO_IMAGEN"]
        # La huella se calcula primero, antes de cualquier procesamiento (RN23).
        huella = hashlib.sha256(contenido).hexdigest()
        detalle = {"nombre": nombre, "sha256": huella, "tamanio": len(contenido)}

        def rechazar(error, motivo):
            """Registra el rechazo y devuelve el error para lanzarlo."""
            self._auditar(
                auditoria.IMAGEN_CARGA, auditoria.RECHAZADO, usuario, caso,
                {**detalle, "motivo": motivo}, True,
            )
            return error

        if not contenido:
            raise rechazar(_error_archivo("El archivo está vacío."), "vacio")
        if len(contenido) > maximo:
            raise rechazar(_error_archivo(
                f"El archivo supera el tamaño máximo de {maximo // MEGABYTE} MB."
            ), "tamanio")
        formato = lector.detectar_formato(contenido)
        if formato is None:
            raise rechazar(_error_archivo(
                "El formato real del archivo no es válido: solo se aceptan imágenes "
                "JPEG, PNG o HEIC."
            ), "formato")
        try:
            dimensiones = lector.leer_dimensiones(contenido, formato)
        except lector.ImagenInvalida as error:
            raise rechazar(
                _error_archivo("La imagen está dañada o incompleta."), "danada"
            ) from error
        existente = self.repositorio.por_huella(caso.id, huella)
        if existente is not None:
            raise rechazar(ConflictoDatos(
                f"Esta imagen ya está cargada en el caso como «{existente.nombre_original}».",
                codigo="imagen_duplicada",
            ), "duplicada")
        limite = self.limite_de_imagenes(caso)
        if self.repositorio.cantidad_de_caso(caso.id) >= limite:
            raise rechazar(ConflictoDatos(
                f"El caso alcanzó el límite de {limite} imágenes de su plan.",
                codigo="limite_imagenes",
            ), "limite_plan")
        return huella, formato, *dimensiones

    def cargar(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, id_caso, usuario, nombre, contenido, origen=None
    ):
        """Valida y guarda una imagen en el caso (RF34 CA1 a CA4).

        ``origen`` indica por dónde llegó, si no fue la pantalla del caso (por
        ejemplo, ``"celular"`` con un enlace de carga, RF53); queda en la auditoría.

        Cada archivo se carga con su propia solicitud: así se valida en forma
        independiente y la pantalla informa el resultado de cada uno (CA5).

        Returns:
            La ``Imagen`` creada.
        """
        caso = self._para_modificar(id_caso, usuario, auditoria.IMAGEN_CARGA)
        nombre = (nombre or "imagen").strip()[:255] or "imagen"
        huella, formato, *dimensiones = self._validar_archivo(caso, usuario, nombre, contenido)
        try:
            miniatura = lector.generar_miniatura(contenido, self.configuracion["LADO_MINIATURA"])
        except lector.ImagenInvalida:
            self._rechazar(
                _error_archivo("La imagen está dañada o incompleta."), auditoria.IMAGEN_CARGA,
                usuario, caso, {"nombre": nombre, "sha256": huella, "motivo": "danada"},
            )

        # Claves aleatorias, sin datos personales ni del caso (RNF09 CA2).
        imagen = Imagen(
            id_caso=caso.id, clave=f"imagenes/{uuid4().hex}",
            clave_miniatura=f"miniaturas/{uuid4().hex}.jpg", nombre_original=nombre,
            formato=formato, tamanio=len(contenido), ancho=dimensiones[0],
            alto=dimensiones[1], huella=huella, id_usuario=usuario.id,
            origen=origen or ORIGEN_COMPUTADORA,
            sello_estado="pendiente" if self.sellos and self.sellos.activo else None,
        )
        self.almacenamiento.guardar(imagen.clave, contenido, imagen.tipo_mime)
        try:
            self.almacenamiento.guardar(imagen.clave_miniatura, miniatura, "image/jpeg")
            self.repositorio.preparar(imagen)
            caso.actualizado_en = ahora_utc()
            self._auditar(
                auditoria.IMAGEN_CARGA, auditoria.EXITOSO, usuario, caso,
                {"id_imagen": imagen.id, "nombre": nombre, "sha256": huella,
                 "tamanio": imagen.tamanio, "formato": formato,
                 **({"origen": origen} if origen else {})},
            )
            self.repositorio.confirmar()
        except Exception:
            borrar_sin_fallar(self.almacenamiento, imagen.clave)
            borrar_sin_fallar(self.almacenamiento, imagen.clave_miniatura)
            raise
        if self.sellos is not None:
            # Primer intento en el momento; si Hedera no responde, lo retoma la tarea (RF37 CA3).
            self.sellos.intentar(imagen)
        return imagen

    # --- Consultar (RF35) ---

    def listar(self, id_caso, usuario):
        """Devuelve ``(caso, permiso, imágenes)`` si el usuario tiene algún permiso."""
        caso, permiso = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_LECTURA)
        return caso, permiso, self.repositorio.de_caso(caso.id)

    def analizadas(self, imagenes):
        """Ids de las imágenes que ya se analizaron, para elegir por defecto las demás."""
        return self.repositorio.analizadas([imagen.id for imagen in imagenes])

    def enlace_miniatura(self, imagen):
        """Enlace firmado de corta duración a la vista previa (RF35 CA2)."""
        return self.almacenamiento.enlace(imagen.clave_miniatura, self._segundos_de_enlace())

    def enlace_original(self, id_caso, id_imagen, usuario):
        """Enlace firmado de corta duración para descargar el original; queda en la auditoría."""
        caso, _ = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_LECTURA)
        imagen = self._imagen_de(caso, id_imagen)
        self._auditar(
            auditoria.IMAGEN_DESCARGA, auditoria.EXITOSO, usuario, caso,
            {"id_imagen": imagen.id, "sha256": imagen.huella}, confirmar=True,
        )
        return self.almacenamiento.enlace(
            imagen.clave, self._segundos_de_enlace(), nombre_descarga=imagen.nombre_original
        )

    def _segundos_de_enlace(self):
        return int(self.configuracion["VIGENCIA_ENLACE_ARCHIVO"].total_seconds())

    def abrir_enlace_local(self, token):
        """Archivo de un enlace del almacenamiento local (desarrollo y pruebas).

        Returns:
            ``(contenido, tipo_mime, disposicion)``; ``disposicion`` es la
            cabecera de descarga del original, o None para una vista previa.

        Raises:
            NoEncontrado: si el enlace venció, fue alterado o el archivo no existe.
        """
        try:
            contenido, nombre = self.almacenamiento.abrir_enlace(token)
        except (ArchivoNoDisponible, AttributeError) as error:
            raise NoEncontrado("El enlace venció o no es válido.") from error
        formato = lector.detectar_formato(contenido)
        tipo_mime = TIPOS_MIME[formato] if formato else "application/octet-stream"
        return contenido, tipo_mime, disposicion_de_descarga(nombre) if nombre else None

    # --- Eliminar (RF36) ---

    def eliminar(self, id_caso, id_imagen, usuario):
        """Elimina la imagen y sus archivos, con todas sus versiones (RF36 CA1).

        Raises:
            ConflictoDatos: si la imagen está en un informe (RN24, RF36 CA2).
        """
        accion = auditoria.IMAGEN_ELIMINACION
        caso = self._para_modificar(id_caso, usuario, accion)
        imagen = self._imagen_de(caso, id_imagen)
        if imagen.en_informe:
            self._rechazar(
                ConflictoDatos(
                    "La imagen forma parte de un informe generado y no puede eliminarse.",
                    codigo="imagen_en_informe",
                ),
                accion, usuario, caso, {"id_imagen": imagen.id, "motivo": "en_informe"},
            )
        claves = (imagen.clave, imagen.clave_miniatura)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"id_imagen": imagen.id, "nombre": imagen.nombre_original, "sha256": imagen.huella},
        )
        caso.actualizado_en = ahora_utc()
        self.repositorio.quitar(imagen)
        self.repositorio.confirmar()
        for clave in claves:
            borrar_sin_fallar(self.almacenamiento, clave)


def _error_archivo(mensaje):
    return ErrorValidacion(mensaje, {"archivo": mensaje})
