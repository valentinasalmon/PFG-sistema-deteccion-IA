"""Verificación de identidad del Referente de una aseguradora (funcionalidad 035).

Antes de que el Administrador apruebe una aseguradora, su Referente confirma
su identidad con un proveedor externo (Identik, CP-35; hoy simulado):

1. desde la pantalla de la organización inicia la verificación y recibe el
   enlace a la página del proveedor;
2. el proveedor informa el resultado (aprobada o rechazada);
3. el Administrador ve el estado junto a la aseguradora y, mientras la
   verificación esté activa, no puede aprobarla sin la identidad aprobada.

La plataforma guarda solo el resultado, nunca imágenes ni datos biométricos.

Realiza: RN41; RF12 (aprobación de aseguradoras); RNF06 (auditoría); RNF08.
"""
import hashlib
import secrets

from app.modelos.organizacion import ROL_REFERENTE, TIPO_ASEGURADORA
from app.modelos.verificacion_identidad import (
    IDENTIDAD_APROBADA,
    IDENTIDAD_PENDIENTE,
    IDENTIDAD_RECHAZADA,
    VerificacionIdentidad,
)
from app.servicios import auditoria
from app.servicios.errores import AccesoDenegado, ErrorValidacion, NoEncontrado
from app.utilidades.tiempo import ahora_utc

MENSAJE_ENLACE_INVALIDO = "El enlace de verificación no existe o ya no es válido."
RESULTADOS = (IDENTIDAD_APROBADA, IDENTIDAD_RECHAZADA)


def huella_de(token):
    """Huella SHA-256 del token del enlace: lo único que se guarda de él."""
    return hashlib.sha256(token.encode()).hexdigest()


def verificacion_a_dict(verificacion):
    """Estado de una verificación para la interfaz, sin datos del proveedor ni biométricos."""
    if verificacion is None:
        return {"estado": "sin_verificar", "creada_en": None, "resuelta_en": None, "motivo": None}
    return {
        "estado": verificacion.estado,
        "creada_en": verificacion.creada_en.isoformat(timespec="seconds"),
        "resuelta_en": (
            verificacion.resuelta_en.isoformat(timespec="seconds")
            if verificacion.resuelta_en else None
        ),
        "motivo": verificacion.motivo,
    }


class ServicioIdentidad:
    """Inicia, consulta y resuelve las verificaciones de identidad."""

    def __init__(self, repositorio, organizaciones, proveedor, registro):
        """
        Args:
            repositorio: ``RepositorioVerificaciones``.
            organizaciones: ``RepositorioOrganizaciones``.
            proveedor: implementación de ``app.integraciones.identidad``, o None
                si la verificación está desactivada.
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.organizaciones = organizaciones
        self.proveedor = proveedor
        self.registro = registro

    @property
    def activa(self):
        """True si hay un proveedor configurado: la verificación se exige para aprobar."""
        return self.proveedor is not None

    def _auditar(self, organizacion_id, usuario, detalle):
        self.registro.registrar(
            auditoria.ORGANIZACION_IDENTIDAD, auditoria.EXITOSO, usuario=usuario,
            recurso=(auditoria.TIPO_ORGANIZACION, organizacion_id), detalle=detalle,
        )

    def _organizacion_del_miembro(self, id_organizacion, usuario):
        """La organización y la membresía del usuario; NoEncontrado si no pertenece."""
        organizacion = self.organizaciones.obtener(id_organizacion)
        membresia = (
            self.organizaciones.membresia(id_organizacion, usuario.id) if organizacion else None
        )
        if membresia is None:
            raise NoEncontrado("La organización no existe o no tenés acceso a ella.")
        return organizacion, membresia

    def estado(self, id_organizacion, usuario):
        """Estado de la verificación para un miembro de la organización (CA1, CA4)."""
        organizacion, _ = self._organizacion_del_miembro(id_organizacion, usuario)
        return {
            "activa": self.activa,
            "corresponde": organizacion.tipo == TIPO_ASEGURADORA and organizacion.pendiente,
            **verificacion_a_dict(self.repositorio.ultima_de(organizacion.id)),
        }

    def iniciar(self, id_organizacion, usuario):
        """Inicia una verificación del Referente de una aseguradora pendiente (CA1, CA2, CA7).

        Returns:
            ``(verificacion, url)``: la verificación pendiente y el enlace al proveedor.
        """
        organizacion, membresia = self._organizacion_del_miembro(id_organizacion, usuario)
        if not self.activa:
            raise ErrorValidacion("La verificación de identidad no está activa en la plataforma.")
        if membresia.rol != ROL_REFERENTE:
            raise AccesoDenegado("Solo el Referente de la aseguradora verifica su identidad.")
        if organizacion.tipo != TIPO_ASEGURADORA or not organizacion.pendiente:
            raise ErrorValidacion(
                "La verificación de identidad es para aseguradoras pendientes de aprobación."
            )
        anterior = self.repositorio.ultima_de(organizacion.id)
        if anterior is not None and anterior.aprobada:
            raise ErrorValidacion("Tu identidad ya está verificada.")
        token = secrets.token_urlsafe(32)
        datos = self.proveedor.iniciar(token, usuario)
        verificacion = self.repositorio.preparar(VerificacionIdentidad(
            id_organizacion=organizacion.id, id_usuario=usuario.id,
            proveedor=self.proveedor.nombre, referencia_externa=datos["referencia"],
            huella_token=huella_de(token), estado=IDENTIDAD_PENDIENTE,
        ))
        self._auditar(organizacion.id, usuario, {
            "operacion": "inicio", "proveedor": self.proveedor.nombre,
            "referencia": datos["referencia"],
        })
        self.repositorio.confirmar()
        return verificacion, datos["url"]

    def _por_token(self, token):
        verificacion = self.repositorio.por_huella(huella_de(token or ""))
        if verificacion is None or verificacion.organizacion is None:
            raise NoEncontrado(MENSAJE_ENLACE_INVALIDO, codigo="verificacion_invalida")
        return verificacion

    def consultar(self, token):
        """Lo que muestra la página pública de verificación: aseguradora y estado (CA6)."""
        verificacion = self._por_token(token)
        return {
            "aseguradora": verificacion.organizacion.nombre,
            "simulada": bool(self.proveedor and self.proveedor.permite_simular),
            **verificacion_a_dict(verificacion),
        }

    def registrar_resultado(self, verificacion, resultado, motivo=None):
        """Aplica el resultado que informó el proveedor (CA3). Es idempotente.

        Lo usan la simulación y, cuando esté conectado Identik, su aviso.
        """
        if resultado not in RESULTADOS:
            raise ErrorValidacion("El resultado de la verificación no es válido.")
        if verificacion.estado != IDENTIDAD_PENDIENTE:
            return verificacion
        verificacion.estado = resultado
        verificacion.motivo = (motivo or "")[:300] or None
        verificacion.resuelta_en = ahora_utc()
        self._auditar(verificacion.id_organizacion, verificacion.usuario, {
            "operacion": "resultado", "resultado": resultado,
            "proveedor": verificacion.proveedor, "referencia": verificacion.referencia_externa,
        })
        self.repositorio.confirmar()
        return verificacion

    def simular(self, token, resultado):
        """Resultado elegido en la página de la verificación simulada (CA6)."""
        if not (self.proveedor and self.proveedor.permite_simular):
            raise AccesoDenegado("Esta verificación la resuelve el proveedor, no se simula.")
        motivo = None if resultado == IDENTIDAD_APROBADA else "Rechazada en la simulación."
        return verificacion_a_dict(
            self.registrar_resultado(self._por_token(token), resultado, motivo)
        )

    def estados_de(self, ids_organizaciones):
        """Estado de la verificación de cada aseguradora, para el Administrador (CA4)."""
        ultimas = self.repositorio.ultimas_de(list(ids_organizaciones))
        return {id_: verificacion_a_dict(ultimas.get(id_)) for id_ in ids_organizaciones}

    def exigir_aprobada(self, organizacion):
        """Antes de aprobar una aseguradora: su Referente tiene que estar verificado (RN41, CA5)."""
        if not self.activa:
            return
        ultima = self.repositorio.ultima_de(organizacion.id)
        if ultima is None or not ultima.aprobada:
            raise ErrorValidacion(
                "La identidad del Referente todavía no está verificada. "
                "Esperá a que complete la verificación antes de aprobar la aseguradora.",
                codigo="identidad_sin_verificar",
            )
