"""Registro de auditoría de las acciones relevantes del sistema.

Los demás servicios llaman a ``ServicioAuditoria.registrar`` por cada acción.
La entrada se suma a la transacción en curso, así se confirma junto con la
acción que registra y, si no puede guardarse, la acción tampoco se aplica
(RNF06 CA8). El servicio no conoce Flask: la dirección IP llega en el
``origen`` que arma la ruta.

Realiza: RNF06 (CA1, CA2, CA4, CA7, CA8) y las acciones de cuenta y sesión
de la funcionalidad 003.
"""
from app.modelos.entrada_auditoria import (
    RESULTADO_EXITOSO,
    RESULTADO_FALLIDO,
    RESULTADO_RECHAZADO,
    EntradaAuditoria,
)
from app.modelos.usuario import Usuario
from app.utilidades.tiempo import ahora_utc

# Resultados, reexportados para que los servicios no dependan del modelo.
EXITOSO = RESULTADO_EXITOSO
FALLIDO = RESULTADO_FALLIDO
RECHAZADO = RESULTADO_RECHAZADO

# --- Acciones de cuenta y sesión (funcionalidad 003) ---
CUENTA_REGISTRO = "cuenta.registro"
CUENTA_VERIFICACION = "cuenta.verificacion"
CUENTA_REENVIO_VERIFICACION = "cuenta.reenvio_verificacion"
CUENTA_BLOQUEO = "cuenta.bloqueo"
SESION_INICIO = "sesion.inicio"
SESION_CIERRE = "sesion.cierre"
CONTRASENIA_RECUPERACION = "contrasenia.recuperacion"
CONTRASENIA_RESTABLECIMIENTO = "contrasenia.restablecimiento"
CONTRASENIA_CAMBIO = "contrasenia.cambio"
PERFIL_EDICION = "perfil.edicion"
CORREO_SOLICITUD_CAMBIO = "correo.solicitud_cambio"
CORREO_CAMBIO = "correo.cambio"

# --- Acciones de organizaciones (funcionalidad 004) ---
ORGANIZACION_CREACION = "organizacion.creacion"
ORGANIZACION_EDICION = "organizacion.edicion"
ORGANIZACION_ELIMINACION = "organizacion.eliminacion"
ORGANIZACION_CAMBIO_REFERENTE = "organizacion.cambio_referente"
INVITACION_ENVIO = "invitacion.envio"
INVITACION_REENVIO = "invitacion.reenvio"
INVITACION_CANCELACION = "invitacion.cancelacion"
INVITACION_ACEPTACION = "invitacion.aceptacion"
INVITACION_RECHAZO = "invitacion.rechazo"
MEMBRESIA_EDICION = "membresia.edicion"
MEMBRESIA_DESVINCULACION = "membresia.desvinculacion"
MEMBRESIA_ABANDONO = "membresia.abandono"

# --- Acciones de aseguradoras (funcionalidad 021) ---
ORGANIZACION_APROBACION = "organizacion.aprobacion"
ORGANIZACION_RECHAZO = "organizacion.rechazo"
CUENTA_DESACTIVACION = "cuenta.desactivacion"
CUENTA_REACTIVACION = "cuenta.reactivacion"
CUENTA_PROMOCION_ADMINISTRADOR = "cuenta.promocion_administrador"

TIPO_USUARIO = "usuario"
TIPO_ORGANIZACION = "organizacion"
TIPO_INVITACION = "invitacion"

# Fragmentos de claves que nunca se guardan en el detalle (RNF06 CA4).
FRAGMENTOS_SENSIBLES = (
    "contrasenia", "password", "hash", "huella", "token", "cookie", "csrf",
    "id_sesion", "identificador_sesion",
)


def limpiar_detalle(detalle):
    """Devuelve una copia del detalle sin claves sensibles, en cualquier nivel.

    Es una red de seguridad: los servicios no deberían enviar esos datos,
    pero si alguno lo hiciera por error, no llegan a la auditoría (CA2).
    """
    if isinstance(detalle, dict):
        return {
            clave: limpiar_detalle(valor)
            for clave, valor in detalle.items()
            if not any(fragmento in str(clave).lower() for fragmento in FRAGMENTOS_SENSIBLES)
        }
    if isinstance(detalle, (list, tuple)):
        return [limpiar_detalle(valor) for valor in detalle]
    return detalle


def _recurso(recurso):
    """Convierte el recurso en ``(tipo, id)``; acepta un ``Usuario`` o una tupla."""
    if recurso is None:
        return None, None
    if isinstance(recurso, Usuario):
        return TIPO_USUARIO, str(recurso.id)
    tipo, identificador = recurso
    return tipo, None if identificador is None else str(identificador)


class ServicioAuditoria:
    """Agrega entradas al registro de auditoría."""

    def __init__(self, repositorio, origen=None):
        """
        Args:
            repositorio: ``RepositorioAuditoria``.
            origen: datos de la solicitud, por ahora ``{"ip": "..."}``.
        """
        self.repositorio = repositorio
        self.origen = origen or {}

    def registrar(  # pylint: disable=too-many-arguments
        self, accion, resultado, *, usuario=None, recurso=None, detalle=None, confirmar=False
    ):
        """Registra una acción.

        Args:
            accion: una de las constantes de acción de este módulo.
            resultado: ``EXITOSO``, ``FALLIDO`` o ``RECHAZADO``.
            usuario: quien actuó, o None si no había sesión ni cuenta identificable.
            recurso: el ``Usuario`` afectado o una tupla ``(tipo, id)``.
            detalle: diccionario con los cambios o el motivo; se quitan las claves sensibles.
            confirmar: True para confirmar la transacción ya mismo, cuando la
                acción no tiene otros cambios que confirmar (por ejemplo, un
                intento rechazado que termina con un error).

        Returns:
            La ``EntradaAuditoria`` agregada.
        """
        tipo_recurso, id_recurso = _recurso(recurso)
        entrada = EntradaAuditoria(
            fecha=ahora_utc(),
            id_usuario=usuario.id if usuario is not None else None,
            ip=self.origen.get("ip"),
            accion=accion,
            tipo_recurso=tipo_recurso,
            id_recurso=id_recurso,
            resultado=resultado,
            detalle=limpiar_detalle(detalle or {}),
        )
        self.repositorio.agregar(entrada)
        if confirmar:
            self.repositorio.confirmar()
        return entrada
