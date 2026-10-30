"""Carga de fotos con un enlace, sin iniciar sesión (funcionalidades 024 y 028).

Desde la computadora, quien puede cargar imágenes en un caso genera un
enlace, que se muestra como código QR. El celular lo abre y sube fotos de su
galería o de la cámara, sin iniciar sesión. El enlace:

- vence a los ``VIGENCIA`` minutos y se puede cancelar;
- solo permite cargar imágenes en ese caso, nunca verlas, bajarlas ni borrarlas;
- carga a nombre de quien lo generó, con sus permisos vigentes y con las
  mismas validaciones, huella y sello de tiempo que la carga normal.

El enlace por QR (celular) no limita la cantidad de fotos: el único límite es
el de imágenes por caso del plan (RN15), igual que en la carga desde la
computadora. El enlace para la persona afectada, que es público y dura días,
admite además como máximo ``MAXIMO_CARGAS`` fotos, como resguardo.

El token es aleatorio (192 bits) y en la base solo se guarda su huella SHA-256.

Desde la funcionalidad 028 hay además un enlace para la persona afectada
(CP-32, decidido por la autora el 2026-10-28): quien lleva el caso se lo
manda por WhatsApp o por correo y ella sube sus propias fotos. Ese enlace:

- vence a los ``DIAS_PERSONA_AFECTADA`` días (se puede elegir entre 1 y
  ``DIAS_MAXIMOS``) y se puede anular en cualquier momento;
- no muestra ningún dato del caso: solo quién pide las fotos;
- exige aceptar una declaración (las fotos son de la persona o tiene permiso
  para compartirlas) antes de la primera foto, y queda registrada;
- marca cada foto con su origen, que queda en la cadena de custodia.

Realiza: RF53 (CA2); RN19, RN20, RN23; RNF06; CP-32.
"""
import hashlib
import secrets
from datetime import timedelta

from app.modelos.enlace_carga import TIPO_CELULAR, TIPO_PERSONA_AFECTADA, EnlaceCarga
from app.modelos.imagen import ORIGEN_CELULAR, ORIGEN_PERSONA_AFECTADA
from app.servicios import auditoria
from app.servicios.errores import ConflictoDatos, ErrorValidacion, NoEncontrado
from app.utilidades.tiempo import ahora_utc

VIGENCIA = timedelta(minutes=15)
MAXIMO_CARGAS = 30
MENSAJE_INVALIDO = (
    "El enlace venció o ya no es válido. Pedí uno nuevo desde la computadora."
)
MENSAJE_INVALIDO_PERSONA_AFECTADA = (
    "Este enlace venció o fue anulado. Pedile uno nuevo a quien te lo mandó."
)

DIAS_PERSONA_AFECTADA = 7
DIAS_MAXIMOS = 30
MAXIMO_ENLACES_VIGENTES = 10
# Versión de la declaración que acepta la persona afectada: queda en la auditoría.
VERSION_DECLARACION = "2026-10-28"
DECLARACION = (
    "Declaro que las fotos que voy a subir son mías o que tengo permiso para compartirlas, "
    "y que las comparto para que se usen en este reclamo."
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

    # --- Enlace para la persona afectada (028, CP-32) ---

    def crear_para_persona_afectada(self, id_caso, usuario, dias=None, destinatario=None):
        """Genera un enlace para que la persona afectada suba sus fotos.

        A diferencia del enlace del celular, no cancela los anteriores: un
        caso puede tener varias personas afectadas.

        Returns:
            ``(enlace, token)``: el token solo existe en este momento.

        Raises:
            ErrorValidacion: si la vigencia no está entre 1 y ``DIAS_MAXIMOS`` días.
            ConflictoDatos: si el caso ya tiene ``MAXIMO_ENLACES_VIGENTES`` enlaces vigentes.
        """
        dias = DIAS_PERSONA_AFECTADA if dias is None else dias
        if not isinstance(dias, int) or isinstance(dias, bool) or not 1 <= dias <= DIAS_MAXIMOS:
            raise ErrorValidacion(
                f"El enlace puede durar entre 1 y {DIAS_MAXIMOS} días.",
                {"dias": f"Elegí entre 1 y {DIAS_MAXIMOS} días."},
            )
        destinatario = (destinatario or "").strip()[:100] or None
        caso = self.imagenes.caso_para_cargar(id_caso, usuario, auditoria.IMAGEN_ENLACE_CARGA)
        ahora = ahora_utc()
        if len(self.repositorio.vigentes_para_persona_afectada(caso.id, ahora)) >= (
            MAXIMO_ENLACES_VIGENTES
        ):
            raise ConflictoDatos(
                f"El caso ya tiene {MAXIMO_ENLACES_VIGENTES} enlaces vigentes. "
                "Anulá alguno antes de crear otro.",
                codigo="demasiados_enlaces",
            )
        token = secrets.token_urlsafe(24)
        enlace = self.repositorio.preparar(EnlaceCarga(
            huella_token=huella_de(token), id_caso=caso.id, id_usuario=usuario.id,
            creado_en=ahora, vence_en=ahora + timedelta(days=dias),
            tipo=TIPO_PERSONA_AFECTADA, destinatario=destinatario,
        ))
        self.registro.registrar_en_caso(
            auditoria.IMAGEN_ENLACE_CARGA, auditoria.EXITOSO, usuario, caso,
            {"operacion": "crear", "tipo": TIPO_PERSONA_AFECTADA, "id_enlace": enlace.id,
             "vence": enlace.vence_en.isoformat()},
        )
        self.repositorio.confirmar()
        return enlace, token

    def listar_para_persona_afectada(self, id_caso, usuario):
        """Enlaces vigentes para la persona afectada del caso."""
        caso = self.imagenes.caso_para_cargar(id_caso, usuario, auditoria.IMAGEN_ENLACE_CARGA)
        return self.repositorio.vigentes_para_persona_afectada(caso.id, ahora_utc())

    def anular(self, id_caso, id_enlace, usuario):
        """Anula un enlace para la persona afectada: deja de servir en ese momento.

        Raises:
            NoEncontrado: si el enlace no es de ese caso o ya no está vigente.
        """
        caso = self.imagenes.caso_para_cargar(id_caso, usuario, auditoria.IMAGEN_ENLACE_CARGA)
        enlace = self.repositorio.obtener(id_enlace)
        ahora = ahora_utc()
        if (enlace is None or enlace.id_caso != caso.id or enlace.tipo != TIPO_PERSONA_AFECTADA
                or not enlace.vigente(ahora)):
            raise NoEncontrado("El enlace no existe o ya no está vigente.")
        enlace.revocado_en = ahora
        self.registro.registrar_en_caso(
            auditoria.IMAGEN_ENLACE_CARGA, auditoria.EXITOSO, usuario, caso,
            {"operacion": "anular", "tipo": TIPO_PERSONA_AFECTADA, "id_enlace": enlace.id},
        )
        self.repositorio.confirmar()

    # --- Uso del enlace, sin sesión ---

    def _vigente(self, token):
        enlace = self.repositorio.por_huella(huella_de(token or ""))
        if enlace is None or not enlace.vigente(ahora_utc()):
            mensaje = (
                MENSAJE_INVALIDO_PERSONA_AFECTADA
                if enlace is not None and enlace.tipo == TIPO_PERSONA_AFECTADA
                else MENSAJE_INVALIDO
            )
            raise NoEncontrado(mensaje, codigo="enlace_invalido")
        return enlace

    def consultar(self, token):
        """Datos que muestra la página del enlace.

        Para el celular: caso, vencimiento y fotos restantes. Para la persona
        afectada no hay ningún dato del caso: solo quién pide las fotos y la
        declaración que tiene que aceptar.
        """
        enlace = self._vigente(token)
        datos = {
            "tipo": enlace.tipo,
            "vence_en": enlace.vence_en.isoformat(timespec="seconds"),
            "restantes": self._restantes(enlace),
        }
        if enlace.tipo == TIPO_CELULAR:
            return {**datos, "numero": enlace.caso.numero}
        caso = enlace.caso
        return {
            **datos,
            "solicitante": f"{enlace.usuario.nombre} {enlace.usuario.apellido}",
            "organizacion": None if caso.es_personal else caso.organizacion.nombre,
            "declaracion": DECLARACION,
            "declaracion_aceptada": enlace.declaracion_aceptada_en is not None,
        }

    def _restantes(self, enlace):
        """Fotos que todavía admite el enlace.

        Es el lugar libre del plan; para la persona afectada, además, el tope del enlace.
        """
        lugar = self.imagenes.lugar_disponible(enlace.caso)
        if enlace.tipo == TIPO_PERSONA_AFECTADA:
            return min(lugar, max(0, MAXIMO_CARGAS - enlace.cargas))
        return lugar

    def _registrar_declaracion(self, enlace):
        """La primera vez que la persona afectada acepta la declaración, queda registrada."""
        if enlace.declaracion_aceptada_en is not None:
            return
        enlace.declaracion_aceptada_en = ahora_utc()
        self.registro.registrar_en_caso(
            auditoria.IMAGEN_ENLACE_CARGA, auditoria.EXITOSO, None, enlace.caso,
            {"operacion": "declaracion", "tipo": TIPO_PERSONA_AFECTADA,
             "id_enlace": enlace.id, "version": VERSION_DECLARACION},
        )

    def cargar(self, token, nombre, contenido, declaracion=False):
        """Carga una foto con el enlace, a nombre de quien lo generó (RF53 CA2).

        Con el enlace de la persona afectada, ``declaracion`` tiene que ser
        True: la persona aceptó la declaración en la página (CP-32).

        Raises:
            NoEncontrado: si el enlace no existe, venció o se canceló.
            ErrorValidacion: si falta aceptar la declaración.
            ConflictoDatos: si la persona afectada ya cargó el máximo de fotos con
                este enlace, o si el caso llegó al límite de imágenes del plan (RN15).
        """
        enlace = self._vigente(token)
        es_persona_afectada = enlace.tipo == TIPO_PERSONA_AFECTADA
        if es_persona_afectada and not declaracion:
            raise ErrorValidacion(
                "Para subir fotos tenés que aceptar la declaración.",
                {"declaracion": "Aceptá la declaración para continuar."},
                codigo="declaracion_requerida",
            )
        if es_persona_afectada and enlace.cargas >= MAXIMO_CARGAS:
            raise ConflictoDatos(
                f"Ya se cargaron {MAXIMO_CARGAS} fotos con este enlace. "
                "Pedile uno nuevo a quien te lo mandó.",
                codigo="enlace_agotado",
            )
        if es_persona_afectada:
            self._registrar_declaracion(enlace)
        origen = ORIGEN_PERSONA_AFECTADA if es_persona_afectada else ORIGEN_CELULAR
        imagen = self.imagenes.cargar(
            enlace.id_caso, enlace.usuario, nombre, contenido, origen=origen
        )
        enlace.cargas += 1
        self.repositorio.confirmar()
        return imagen
