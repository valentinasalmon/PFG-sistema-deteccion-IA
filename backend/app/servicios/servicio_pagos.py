"""Cobro del plan de las organizaciones por transferencia (funcionalidad 032).

El plan de un estudio jurídico o de una aseguradora se paga al registrarlos
(o al crear el estudio desde Mi perfil, o al cambiar de plan). Cada pago es
un ``Cobro``: una transferencia que se espera a un CVU con una referencia,
como cobra Cresium. Al acreditarse:

- un alta deja el estudio activo y la aseguradora pendiente de aprobación;
- un cambio de plan aplica el plan nuevo.

Si el Administrador rechaza una aseguradora pagada, su cobro se devuelve.
Mientras no esté la API de Cresium, la acreditación se simula (CP-34) y queda
en la auditoría como simulada.

El enlace de la página de pago lleva un token aleatorio; en la base solo se
guarda su huella SHA-256.

Realiza: RF10, RF20 (CA2); RN15, RN38; CP-01, CP-34.
"""
import hashlib
import secrets

from app.modelos.cobro import (
    COBRO_ACREDITADO,
    COBRO_DEVUELTO,
    COBRO_PENDIENTE,
    MOTIVO_ALTA,
    MOTIVO_CAMBIO_PLAN,
    Cobro,
)
from app.modelos.organizacion import (
    ORGANIZACION_ACTIVA,
    ORGANIZACION_PAGO_PENDIENTE,
    ORGANIZACION_PENDIENTE,
)
from app.servicios import auditoria
from app.servicios.errores import AccesoDenegado, ErrorValidacion, NoEncontrado
from app.utilidades.tiempo import ahora_utc

MENSAJE_COBRO_INVALIDO = "El enlace de pago no existe o ya no es válido."
LETRAS_REFERENCIA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0, O, 1 ni I: se leen mal


def huella_de(token):
    """Huella SHA-256 del token: es lo único que se guarda."""
    return hashlib.sha256(token.encode()).hexdigest()


class ServicioPagos:
    """Crea, consulta, acredita y devuelve los cobros del plan."""

    def __init__(self, repositorio, proveedor, configuracion, registro):
        """
        Args:
            repositorio: ``RepositorioCobros``.
            proveedor: proveedor de pagos (hoy, ``ProveedorPagosSimulado``).
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.proveedor = proveedor
        self.configuracion = configuracion
        self.registro = registro

    def exigir_plan(self, codigo):
        """Rechaza un plan que no existe (Básico o Profesional).

        Raises:
            ErrorValidacion: con el error junto al campo ``plan``.
        """
        if codigo not in self.configuracion["PLANES"]:
            mensaje = "Elegí el plan Básico o el Profesional."
            raise ErrorValidacion(mensaje, {"plan": mensaje})

    def _referencia_nueva(self):
        while True:
            referencia = "EVD-" + "".join(secrets.choice(LETRAS_REFERENCIA) for _ in range(6))
            if not self.repositorio.existe_referencia(referencia):
                return referencia

    def crear_cobro(  # pylint: disable=too-many-arguments
        self, plan, *, organizacion=None, nombre=None, tipo=None, motivo=MOTIVO_ALTA,
        usuario=None,
    ):
        """Crea un cobro pendiente y devuelve ``(cobro, token)``. No confirma.

        Sin ``organizacion`` crea un cobro que no se aplica a nada: lo usa el
        registro con un correo ya existente, para responder igual que con un
        correo nuevo (RF01 CA3). Los cobros pendientes anteriores de la
        organización dejan de servir: solo vale el último enlace.
        """
        self.exigir_plan(plan)
        if organizacion is not None:
            for anterior in self.repositorio.pendientes_de(organizacion.id):
                anterior.huella_token = huella_de(secrets.token_urlsafe(24))
        token = secrets.token_urlsafe(24)
        referencia = self._referencia_nueva()
        cobro = self.repositorio.preparar(Cobro(
            organizacion=organizacion,
            nombre_organizacion=organizacion.nombre if organizacion else nombre,
            tipo_organizacion=organizacion.tipo if organizacion else tipo,
            plan=plan, motivo=motivo, referencia=referencia, huella_token=huella_de(token),
            estado=COBRO_PENDIENTE, proveedor=self.proveedor.nombre,
            **self.proveedor.datos_de_cobro(referencia),
        ))
        if organizacion is not None:
            self.registro.registrar(
                auditoria.ORGANIZACION_COBRO, auditoria.EXITOSO, usuario=usuario,
                recurso=(auditoria.TIPO_ORGANIZACION, organizacion.id),
                detalle={"operacion": "crear", "referencia": referencia, "plan": plan,
                         "motivo": motivo, "proveedor": self.proveedor.nombre},
            )
        return cobro, token

    def crear_cobro_sin_organizacion(self, plan, nombre, tipo):
        """Cobro que no se aplica a nada, para el registro con un correo ya existente.

        La respuesta y la pantalla de pago son iguales a las de un registro
        nuevo, así no se revela que el correo existe (RF01 CA3). Confirma.

        Returns:
            El token del enlace de pago.
        """
        _, token = self.crear_cobro(plan, nombre=nombre, tipo=tipo)
        self.repositorio.confirmar()
        return token

    def _por_token(self, token):
        cobro = self.repositorio.por_huella(huella_de(token or ""))
        if cobro is None:
            raise NoEncontrado(MENSAJE_COBRO_INVALIDO, codigo="cobro_invalido")
        return cobro

    def a_dict(self, cobro):
        """Datos que muestra la pantalla de pago (sin datos de la cuenta de quien paga)."""
        plan = self.configuracion["PLANES"][cobro.plan]
        return {
            "referencia": cobro.referencia,
            "estado": cobro.estado,
            "motivo": cobro.motivo,
            "plan": {"codigo": cobro.plan, "nombre": plan["nombre"], "precio": plan["precio"]},
            "organizacion": {
                "id": cobro.id_organizacion, "nombre": cobro.nombre_organizacion,
                "tipo": cobro.tipo_organizacion,
            },
            "proveedor": self.proveedor.nombre_visible,
            "titular": self.proveedor.titular,
            "cvu": cobro.cvu,
            "alias": cobro.alias,
            "permite_simular": self.proveedor.permite_simular,
            "acreditado_en": (
                cobro.acreditado_en.isoformat(timespec="seconds") if cobro.acreditado_en else None
            ),
        }

    def consultar(self, token):
        """El cobro del enlace, para la pantalla de pago."""
        return self.a_dict(self._por_token(token))

    def _aplicar(self, cobro):
        """Efecto del pago sobre la organización: activarla o cambiar su plan."""
        organizacion = cobro.organizacion
        if organizacion is None:
            return
        if cobro.motivo == MOTIVO_CAMBIO_PLAN:
            organizacion.plan = cobro.plan
        elif organizacion.estado == ORGANIZACION_PAGO_PENDIENTE:
            organizacion.plan = cobro.plan
            organizacion.estado = (
                ORGANIZACION_PENDIENTE if organizacion.es_aseguradora else ORGANIZACION_ACTIVA
            )

    def simular_acreditacion(self, token):
        """Acredita el cobro como si hubiera llegado el aviso de Cresium (simulado).

        Es idempotente: un cobro ya acreditado no cambia.

        Raises:
            NoEncontrado: si el enlace no es válido.
            AccesoDenegado: si el proveedor no permite simular (cobro real).
        """
        cobro = self._por_token(token)
        if not self.proveedor.permite_simular:
            raise AccesoDenegado("Este cobro se acredita solo al recibir la transferencia.")
        if cobro.estado == COBRO_PENDIENTE:
            cobro.estado = COBRO_ACREDITADO
            cobro.acreditado_en = ahora_utc()
            self._aplicar(cobro)
            if cobro.id_organizacion is not None:
                self.registro.registrar(
                    auditoria.ORGANIZACION_COBRO, auditoria.EXITOSO,
                    recurso=(auditoria.TIPO_ORGANIZACION, cobro.id_organizacion),
                    detalle={"operacion": "acreditar", "referencia": cobro.referencia,
                             "plan": cobro.plan, "motivo": cobro.motivo, "simulado": True},
                )
            self.repositorio.confirmar()
        return self.a_dict(cobro)

    def devolver_cobros(self, organizacion, usuario):
        """Devuelve (simulado) lo cobrado a una organización; no confirma.

        Se usa al rechazar una aseguradora pagada (CA6).
        """
        for cobro in self.repositorio.acreditados_de(organizacion.id):
            cobro.estado = COBRO_DEVUELTO
            cobro.devuelto_en = ahora_utc()
            self.registro.registrar(
                auditoria.ORGANIZACION_COBRO, auditoria.EXITOSO, usuario=usuario,
                recurso=(auditoria.TIPO_ORGANIZACION, organizacion.id),
                detalle={"operacion": "devolver", "referencia": cobro.referencia,
                         "simulado": True},
            )
