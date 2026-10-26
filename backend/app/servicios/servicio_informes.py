"""Informes PDF de los análisis: generación, historial y descarga.

El informe se genera al finalizar el análisis y se guarda en el
almacenamiento con una clave aleatoria; la base guarda la huella SHA-256 del
PDF. Nunca se modifica: un análisis nuevo genera un informe nuevo
(RF44 CA4). Las imágenes incluidas quedan marcadas y ya no se pueden
eliminar (RN24).

Cada informe lleva un código de verificación y un QR hacia una página
pública, y la huella de su PDF se sella en Hedera: cualquiera puede
comprobar que un PDF no fue modificado (funcionalidad 026).

Realiza: RF44, RF45, RF55; RN24, RN25, RN27, RN29; RNF07 (CA3).
"""
import hashlib
import logging
import secrets
from uuid import uuid4

from app.informes import informe_analisis
from app.modelos.analisis import ESTADO_FINALIZADO, INTEGRIDAD_VERIFICADA
from app.modelos.caso import NIVEL_COLABORACION, NIVEL_LECTURA
from app.modelos.informe import Informe
from app.servicios import auditoria
from app.servicios.errores import ConflictoDatos, NoEncontrado
from app.utilidades.qr import qr_svg
from app.utilidades.tiempo import ahora_utc

# Sin letras ni números que se confundan al leerlos (0/O, 1/I/L).
ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LARGO_CODIGO = 12


def nuevo_codigo():
    """Código de verificación aleatorio de 12 caracteres (unos 59 bits)."""
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(LARGO_CODIGO))


def normalizar_codigo(codigo):
    """El código sin guiones ni espacios y en mayúsculas, como se guarda."""
    return "".join(c for c in (codigo or "").upper() if c.isalnum())


def codigo_legible(codigo):
    """El código en grupos de cuatro, como se imprime en el PDF: ``ABCD-EFGH-JKMN``."""
    return "-".join(codigo[i:i + 4] for i in range(0, len(codigo), 4))


registro_log = logging.getLogger(__name__)


class ServicioInformes:
    """Genera, lista y entrega los informes de un caso."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, casos, almacenamiento, configuracion, registro, sellos=None
    ):
        """
        Args:
            repositorio: ``RepositorioInformes``.
            casos: ``ServicioCasos``, que resuelve los permisos sobre el caso.
            almacenamiento: donde se guardan los PDF y se leen las miniaturas.
            registro: ``ServicioAuditoria``.
            sellos: ``ServicioSellos``, que sella la huella del PDF (026); opcional.
        """
        self.registro = registro
        self.sellos = sellos
        self.url_frontend = configuracion["URL_FRONTEND"].rstrip("/")
        self.repositorio = repositorio
        self.casos = casos
        self.almacenamiento = almacenamiento
        self.version_plataforma = configuracion["VERSION_APLICACION"]
        self.vigencia_enlace = configuracion["VIGENCIA_ENLACE_ARCHIVO"]

    # --- Generación (RF44) ---

    def _miniaturas(self, analisis):
        """Vistas reducidas de las imágenes verificadas; una que falte no impide el informe."""
        miniaturas = {}
        for incluida in analisis.imagenes:
            if incluida.imagen is None or incluida.integridad != INTEGRIDAD_VERIFICADA:
                continue
            try:
                miniaturas[incluida.id] = self.almacenamiento.leer(incluida.imagen.clave_miniatura)
            except Exception:  # pylint: disable=broad-exception-caught
                registro_log.warning("Falta la miniatura de la imagen %s", incluida.id_imagen)
        return miniaturas

    def _imagenes_de_capas(self, analisis):
        """Imágenes de los resultados (mapas ELA); una que falte no impide el informe."""
        imagenes = {}
        for incluida in analisis.imagenes:
            for resultado in incluida.resultados:
                if not resultado.clave_imagen:
                    continue
                try:
                    imagenes[resultado.id] = self.almacenamiento.leer(resultado.clave_imagen)
                except Exception:  # pylint: disable=broad-exception-caught
                    registro_log.warning("Falta la imagen del resultado %s", resultado.id)
        return imagenes

    def generar(self, analisis):
        """Genera el PDF, lo guarda y suma el ``Informe`` a la transacción, sin confirmarla.

        Raises:
            Exception: cualquier falla al armar o guardar el PDF; quien llama
                decide qué hacer (el análisis igual finaliza, CA6).
        """
        generado_en = ahora_utc()
        codigo = nuevo_codigo()
        datos = informe_analisis.armar_datos(
            analisis, self._miniaturas(analisis), self.version_plataforma,
            self._imagenes_de_capas(analisis),
        )
        url = f"{self.url_frontend}/verificar/{codigo}"
        datos["verificacion"] = {
            "codigo": codigo_legible(codigo), "url": url, "qr": qr_svg(url),
            "pagina": f"{self.url_frontend}/verificar",
        }
        contenido = informe_analisis.generar_pdf(datos, generado_en)
        informe = Informe(
            id_caso=analisis.id_caso, id_analisis=analisis.id,
            clave=f"informes/{uuid4().hex}.pdf",
            huella=hashlib.sha256(contenido).hexdigest(), tamanio=len(contenido),
            generado_en=generado_en, codigo_verificacion=codigo,
            sello_estado="pendiente" if self.sellos and self.sellos.activo else None,
        )
        self.almacenamiento.guardar(informe.clave, contenido, "application/pdf")
        analisis.informe = informe
        self.repositorio.agregar(informe)
        for incluida in analisis.imagenes:
            if incluida.imagen is not None and incluida.integridad == INTEGRIDAD_VERIFICADA:
                incluida.imagen.en_informe = True
        self.registro.registrar_en_caso(
            auditoria.INFORME_GENERACION, auditoria.EXITOSO, analisis.solicitante,
            analisis.caso, {"id_analisis": analisis.id, "sha256": informe.huella},
        )
        return informe

    def regenerar(self, id_caso, id_analisis, usuario):
        """Vuelve a generar el informe de un análisis finalizado que no lo tiene (CA6)."""
        caso, _ = self.casos.caso_con_permiso(
            id_caso, usuario, NIVEL_COLABORACION, auditoria.INFORME_GENERACION
        )
        analisis = next((a for a in caso.analisis if a.id == id_analisis), None)
        if analisis is None:
            raise NoEncontrado("El análisis no existe o no tenés acceso a él.")
        if analisis.estado != ESTADO_FINALIZADO or analisis.informe is not None:
            raise ConflictoDatos(
                "Solo se genera el informe de un análisis finalizado que todavía no lo tiene.",
                codigo="informe_no_regenerable",
            )
        informe = self.generar(analisis)
        caso.actualizado_en = ahora_utc()
        self.repositorio.confirmar()
        self.sellar(informe)
        return informe

    def sellar(self, informe):
        """Primer intento de sellar la huella del PDF; si falla, lo retoma la tarea (RF55 CA1).

        Se llama después de confirmar el informe: el sello nunca impide generarlo.
        """
        if informe is not None and self.sellos is not None and informe.sello_estado:
            self.sellos.intentar(informe)

    # --- Verificación pública (RF55 CA3) ---

    def verificar(self, codigo=None, huella=None):
        """Datos públicos de un informe, buscado por su código o por la huella del PDF.

        Solo devuelve lo necesario para comprobar el documento (fecha, huella y
        sello), nunca datos del caso.

        Raises:
            NoEncontrado: si no hay un informe con ese código o esa huella.
        """
        informe = None
        if codigo:
            informe = self.repositorio.por_codigo(normalizar_codigo(codigo))
        elif huella:
            informe = self.repositorio.por_huella((huella or "").lower())
        if informe is None:
            raise NoEncontrado(
                "No hay ningún informe de evidentIA con ese código o con ese archivo.",
                codigo="informe_no_encontrado",
            )
        return informe

    # --- Historial y descarga (RF45) ---

    def listar(self, id_caso, usuario):
        """Informes del caso, del más reciente al más antiguo (RF45 CA1)."""
        caso, _ = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_LECTURA)
        return self.repositorio.de_caso(caso.id)

    def enlace_de_descarga(self, id_caso, id_informe, usuario):
        """Enlace firmado de 5 minutos al PDF; la descarga queda en la auditoría (RF45 CA2)."""
        caso, _ = self.casos.caso_con_permiso(id_caso, usuario, NIVEL_LECTURA)
        informe = self.repositorio.obtener(id_informe)
        if informe is None or informe.id_caso != caso.id:
            raise NoEncontrado("El informe no existe o no tenés acceso a él.")
        self.registro.registrar_en_caso(
            auditoria.INFORME_DESCARGA, auditoria.EXITOSO, usuario, caso,
            {"id_informe": informe.id, "sha256": informe.huella}, confirmar=True,
        )
        segundos = int(self.vigencia_enlace.total_seconds())
        nombre = f"informe-{caso.numero}-analisis-{informe.id_analisis}.pdf"
        return self.almacenamiento.enlace(informe.clave, segundos, nombre_descarga=nombre)
