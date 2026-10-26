"""Carga de fotos desde el celular con un enlace de un solo uso (funcionalidad 024).

Desde la computadora, quien puede cargar imágenes en un caso genera un
enlace, que se muestra como código QR. El celular lo abre y sube fotos de su
galería o de la cámara, sin iniciar sesión. El enlace:

- vence a los ``VIGENCIA`` minutos y se puede cancelar;
- solo permite cargar imágenes en ese caso, nunca verlas, bajarlas ni borrarlas;
- carga a nombre de quien lo generó, con sus permisos vigentes y con las
  mismas validaciones, huella y sello de tiempo que la carga normal;
- admite como máximo ``MAXIMO_CARGAS`` fotos.

El token es aleatorio (192 bits) y en la base solo se guarda su huella SHA-256.

Realiza: RF53 (CA2); RN19, RN20, RN23; RNF06.
"""
import hashlib
import secrets
from datetime import timedelta

from app.modelos.enlace_carga import EnlaceCarga
from app.servicios import auditoria
from app.servicios.errores import ConflictoDatos, NoEncontrado
from app.utilidades.tiempo import ahora_utc

VIGENCIA = timedelta(minutes=15)
MAXIMO_CARGAS = 30
ORIGEN_CELULAR = "celular"
MENSAJE_INVALIDO = (
    "El enlace venció o ya no es válido. Pedí uno nuevo desde la computadora."
)


def huella_de(token):
    """Huella SHA-256 del token: es lo único que se guarda."""
    return hashlib.sha256(token.encode()).hexdigest()


class ServicioEnlacesCarga:
    """Crea, cancela y usa los enlaces de carga desde el celular."""

    def __init__(self, repositorio, imagenes, registro):
        """
        Args:
            repositorio: ``RepositorioEnlacesCarga``.
            imagenes: ``ServicioImagenes``, que valida y guarda cada foto.
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.imagenes = imagenes
        self.registro = registro

    def _cancelar_anteriores(self, id_caso, usuario, ahora):
        for anterior in self.repositorio.sin_cancelar(id_caso, usuario.id):
            anterior.revocado_en = ahora

    def crear(self, id_caso, usuario):
        """Genera un enlace nuevo y cancela los anteriores del mismo usuario en el caso.

        Returns:
            ``(enlace, token)``: el token solo existe en este momento.
        """
        caso = self.imagenes.caso_para_cargar(id_caso, usuario, auditoria.IMAGEN_ENLACE_CARGA)
        ahora = ahora_utc()
        self._cancelar_anteriores(caso.id, usuario, ahora)
        token = secrets.token_urlsafe(24)
        enlace = self.repositorio.preparar(EnlaceCarga(
            huella_token=huella_de(token), id_caso=caso.id, id_usuario=usuario.id,
            creado_en=ahora, vence_en=ahora + VIGENCIA,
        ))
        self.registro.registrar_en_caso(
            auditoria.IMAGEN_ENLACE_CARGA, auditoria.EXITOSO, usuario, caso,
            {"operacion": "crear", "id_enlace": enlace.id, "vence": enlace.vence_en.isoformat()},
        )
        self.repositorio.confirmar()
        return enlace, token

    def cancelar(self, id_caso, usuario):
        """Cancela los enlaces vigentes del usuario para el caso."""
        caso = self.imagenes.caso_para_cargar(id_caso, usuario, auditoria.IMAGEN_ENLACE_CARGA)
        self._cancelar_anteriores(caso.id, usuario, ahora_utc())
        self.registro.registrar_en_caso(
            auditoria.IMAGEN_ENLACE_CARGA, auditoria.EXITOSO, usuario, caso,
            {"operacion": "cancelar"},
        )
        self.repositorio.confirmar()

    def _vigente(self, token):
        enlace = self.repositorio.por_huella(huella_de(token or ""))
        if enlace is None or not enlace.vigente(ahora_utc()):
            raise NoEncontrado(MENSAJE_INVALIDO, codigo="enlace_invalido")
        return enlace

    def consultar(self, token):
        """Datos que muestra la página del celular: caso, vencimiento y fotos restantes."""
        enlace = self._vigente(token)
        return {
            "numero": enlace.caso.numero,
            "vence_en": enlace.vence_en.isoformat(timespec="seconds"),
            "restantes": MAXIMO_CARGAS - enlace.cargas,
        }

    def cargar(self, token, nombre, contenido):
        """Carga una foto con el enlace, a nombre de quien lo generó (RF53 CA2).

        Raises:
            NoEncontrado: si el enlace no existe, venció o se canceló.
            ConflictoDatos: si ya se cargó el máximo de fotos con este enlace.
        """
        enlace = self._vigente(token)
        if enlace.cargas >= MAXIMO_CARGAS:
            raise ConflictoDatos(
                f"Ya se cargaron {MAXIMO_CARGAS} fotos con este enlace. "
                "Generá uno nuevo desde la computadora.",
                codigo="enlace_agotado",
            )
        imagen = self.imagenes.cargar(
            enlace.id_caso, enlace.usuario, nombre, contenido, origen=ORIGEN_CELULAR
        )
        enlace.cargas += 1
        self.repositorio.confirmar()
        return imagen
