"""Organizaciones, invitaciones y membresías.

Concentra las reglas de la funcionalidad 004: quién puede hacer cada
operación, exactamente un Referente por organización, límite de miembros del
plan, vigencia de las invitaciones, abandono y eliminación. Cada operación,
exitosa o rechazada, queda en la auditoría en la misma transacción.

Permisos: quien no es miembro recibe ``NoEncontrado`` (no se revela si la
organización existe); un Miembro que intenta algo reservado al Referente
recibe ``AccesoDenegado``.

Realiza: RF10 a RF18 (sin las reglas de casos, que agrega la 005); RN06,
RN07, RN08, RN10, RN11, RN15; RNF06.
"""
from app.modelos.organizacion import (
    INVITACION_ACEPTADA,
    INVITACION_CANCELADA,
    INVITACION_PENDIENTE,
    INVITACION_RECHAZADA,
    ROL_MIEMBRO,
    ROL_REFERENTE,
    Invitacion,
    Membresia,
    Organizacion,
)
from app.servicios import auditoria
from app.servicios.errores import (
    AccesoDenegado,
    ConflictoDatos,
    ErrorValidacion,
    NoEncontrado,
    TokenInvalido,
)
from app.servicios.tokens import PROPOSITO_INVITACION
from app.utilidades.tiempo import ahora_utc

MENSAJE_NO_ENCONTRADA = "La organización no existe o no tenés acceso a ella."
MENSAJE_SOLO_REFERENTE = "Solo el Referente de la organización puede hacer esto."
CAMPOS_EDITABLES = ("nombre", "tipo", "correo_contacto", "telefono")


class ServicioOrganizaciones:  # pylint: disable=too-many-instance-attributes
    """Operaciones sobre organizaciones, sus miembros y sus invitaciones."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, usuarios, correos, tokens, configuracion, registro
    ):
        """
        Args:
            repositorio: ``RepositorioOrganizaciones``.
            usuarios: ``RepositorioUsuarios``, para saber si un correo está registrado.
            registro: ``ServicioAuditoria``.
        """
        self.repositorio = repositorio
        self.usuarios = usuarios
        self.correos = correos
        self.tokens = tokens
        self.configuracion = configuracion
        self.registro = registro

    # --- Utilidades internas ---

    def _auditar(self, accion, resultado, usuario, organizacion, detalle=None, confirmar=False):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        return self.registro.registrar(
            accion, resultado, usuario=usuario,
            recurso=(auditoria.TIPO_ORGANIZACION, organizacion.id),
            detalle=detalle, confirmar=confirmar,
        )

    def _rechazar(self, error, accion, usuario, organizacion, motivo, detalle=None):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Registra la operación rechazada, la confirma y lanza el error."""
        self._auditar(
            accion, auditoria.RECHAZADO, usuario, organizacion,
            {**(detalle or {}), "motivo": motivo}, confirmar=True,
        )
        raise error

    def _acceso(self, id_organizacion, usuario):
        """Devuelve ``(organizacion, membresia)`` o lanza ``NoEncontrado``."""
        organizacion = self.repositorio.obtener(id_organizacion)
        membresia = (
            self.repositorio.membresia(id_organizacion, usuario.id) if organizacion else None
        )
        if membresia is None:
            raise NoEncontrado(MENSAJE_NO_ENCONTRADA)
        return organizacion, membresia

    def _como_referente(self, id_organizacion, usuario, accion):
        """Devuelve la organización si el usuario es su Referente; si no, registra y rechaza."""
        organizacion, membresia = self._acceso(id_organizacion, usuario)
        if not membresia.es_referente:
            self._rechazar(
                AccesoDenegado(MENSAJE_SOLO_REFERENTE), accion, usuario, organizacion,
                "no_es_referente",
            )
        return organizacion

    def _membresia_de(self, organizacion, id_usuario):
        membresia = self.repositorio.membresia(organizacion.id, id_usuario)
        if membresia is None:
            raise NoEncontrado("Esa persona no es miembro de la organización.")
        return membresia

    def limite_de_miembros(self, organizacion):
        """Cantidad máxima de miembros del plan de la organización (RN15)."""
        return self.configuracion["PLANES"][organizacion.plan]["miembros"]

    def nombre_del_plan(self, organizacion):
        """Nombre visible del plan de la organización."""
        return self.configuracion["PLANES"][organizacion.plan]["nombre"]

    # --- Organizaciones (RF10, RF11, RF18) ---

    def listar(self, usuario):
        """Membresías del usuario, con su organización (RN06)."""
        return self.repositorio.membresias_de_usuario(usuario.id)

    def crear(self, usuario, datos):
        """Crea la organización con el plan inicial y el creador como Referente (RF10).

        Args:
            datos: diccionario con ``nombre``, ``tipo`` y, opcionales,
                ``correo_contacto`` y ``telefono``.
        """
        organizacion = Organizacion(
            nombre=datos["nombre"], tipo=datos["tipo"],
            correo_contacto=datos.get("correo_contacto") or None,
            telefono=datos.get("telefono") or None,
            plan=self.configuracion["PLAN_INICIAL_ORGANIZACION"],
        )
        organizacion.membresias.append(Membresia(id_usuario=usuario.id, rol=ROL_REFERENTE))
        self.repositorio.preparar(organizacion)
        self._auditar(
            auditoria.ORGANIZACION_CREACION, auditoria.EXITOSO, usuario, organizacion,
            {"nombre": organizacion.nombre, "tipo": organizacion.tipo, "plan": organizacion.plan},
        )
        self.repositorio.confirmar()
        return organizacion

    def obtener(self, id_organizacion, usuario):
        """Devuelve ``(organizacion, membresia)`` si el usuario es miembro."""
        return self._acceso(id_organizacion, usuario)

    def editar(self, id_organizacion, usuario, cambios):
        """Modifica los datos de la organización (RF11). Solo el Referente."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.ORGANIZACION_EDICION
        )
        modificados = {}
        for campo in CAMPOS_EDITABLES:
            if campo not in cambios:
                continue
            nuevo = cambios[campo] or None
            if campo in ("nombre", "tipo") and nuevo is None:
                continue
            anterior = getattr(organizacion, campo)
            if nuevo != anterior:
                modificados[campo] = {"anterior": anterior, "nuevo": nuevo}
                setattr(organizacion, campo, nuevo)
        if modificados:
            self._auditar(
                auditoria.ORGANIZACION_EDICION, auditoria.EXITOSO, usuario, organizacion,
                {"cambios": modificados},
            )
            self.repositorio.confirmar()
        return organizacion

    def _eliminar(self, organizacion, usuario, avisar):
        """Elimina la organización con sus membresías e invitaciones (RN09 sin casos)."""
        nombre = organizacion.nombre
        a_avisar = [m.usuario for m in organizacion.membresias if m.id_usuario != usuario.id]
        self._auditar(
            auditoria.ORGANIZACION_ELIMINACION, auditoria.EXITOSO, usuario, organizacion,
            {"nombre": nombre, "miembros": len(organizacion.membresias)},
        )
        self.repositorio.quitar(organizacion)
        self.repositorio.confirmar()
        if avisar:
            for miembro in a_avisar:
                self.correos.enviar_aviso_eliminacion_organizacion(miembro, nombre)

    def eliminar(self, id_organizacion, usuario, confirmacion):
        """Elimina la organización si se escribe su nombre exacto (RF18). Solo el Referente."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.ORGANIZACION_ELIMINACION
        )
        if (confirmacion or "").strip() != organizacion.nombre:
            mensaje = "Escribí el nombre exacto de la organización para confirmar."
            self._rechazar(
                ErrorValidacion(mensaje, {"confirmacion": mensaje}),
                auditoria.ORGANIZACION_ELIMINACION, usuario, organizacion,
                "confirmacion_incorrecta",
            )
        self._eliminar(organizacion, usuario, avisar=True)

    # --- Miembros (RF14, RF15, RF16, RF17) ---

    def miembros(self, id_organizacion, usuario):
        """Membresías de la organización (RF16). Cualquier miembro."""
        self._acceso(id_organizacion, usuario)
        return self.repositorio.miembros(id_organizacion)

    def editar_membresia(self, id_organizacion, usuario, id_usuario, cargo):
        """Cambia el cargo de un miembro sin tocar sus datos personales (RF15 CA1, RN11)."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.MEMBRESIA_EDICION
        )
        membresia = self._membresia_de(organizacion, id_usuario)
        nuevo = cargo or None
        if nuevo != membresia.cargo:
            self._auditar(
                auditoria.MEMBRESIA_EDICION, auditoria.EXITOSO, usuario, organizacion,
                {"id_usuario": id_usuario, "cargo": {"anterior": membresia.cargo, "nuevo": nuevo}},
            )
            membresia.cargo = nuevo
            self.repositorio.confirmar()
        return membresia

    def desvincular(self, id_organizacion, usuario, id_usuario):
        """Quita a un miembro de la organización y le avisa (RF14). Solo el Referente."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.MEMBRESIA_DESVINCULACION
        )
        if id_usuario == usuario.id:
            self._rechazar(
                ConflictoDatos(
                    "No podés desvincularte a vos mismo. Designá otro Referente y "
                    "después abandoná la organización.",
                    codigo="referente_no_puede_desvincularse",
                ),
                auditoria.MEMBRESIA_DESVINCULACION, usuario, organizacion, "es_el_referente",
            )
        membresia = self._membresia_de(organizacion, id_usuario)
        desvinculado = membresia.usuario
        self._auditar(
            auditoria.MEMBRESIA_DESVINCULACION, auditoria.EXITOSO, usuario, organizacion,
            {"id_usuario": id_usuario, "correo": desvinculado.correo},
        )
        self.repositorio.quitar(membresia)
        self.repositorio.confirmar()
        self.correos.enviar_aviso_desvinculacion(desvinculado, organizacion)

    def designar_referente(self, id_organizacion, usuario, id_usuario):
        """Transfiere el rol de Referente a otro miembro (RF15 CA2, RN07)."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.ORGANIZACION_CAMBIO_REFERENTE
        )
        if id_usuario == usuario.id:
            mensaje = "Ya sos el Referente de la organización."
            raise ErrorValidacion(mensaje, {"id_usuario": mensaje})
        nueva = self._membresia_de(organizacion, id_usuario)
        actual = self.repositorio.membresia(organizacion.id, usuario.id)
        # Primero se baja el rol actual: el índice único admite un solo Referente.
        actual.rol = ROL_MIEMBRO
        self.repositorio.preparar(actual)
        nueva.rol = ROL_REFERENTE
        self._auditar(
            auditoria.ORGANIZACION_CAMBIO_REFERENTE, auditoria.EXITOSO, usuario, organizacion,
            {"anterior": usuario.id, "nuevo": id_usuario},
        )
        self.repositorio.confirmar()
        self.correos.enviar_aviso_cambio_referente(nueva.usuario, organizacion, True, nueva.usuario)
        self.correos.enviar_aviso_cambio_referente(usuario, organizacion, False, nueva.usuario)

    def abandonar(self, id_organizacion, usuario, confirmar_eliminacion=False):
        """El usuario deja la organización (RF17, RN08).

        Returns:
            True si la organización se eliminó porque era su único miembro.
        """
        organizacion, membresia = self._acceso(id_organizacion, usuario)
        if membresia.es_referente:
            cantidad = self.repositorio.cantidad_de_miembros(organizacion.id)
            if cantidad > 1:
                self._rechazar(
                    ConflictoDatos(
                        "Sos el Referente: antes de abandonar la organización, designá a otro "
                        "miembro como Referente.",
                        codigo="debe_designar_referente",
                    ),
                    auditoria.MEMBRESIA_ABANDONO, usuario, organizacion, "es_el_referente",
                )
            if not confirmar_eliminacion:
                self._rechazar(
                    ConflictoDatos(
                        "Sos el único miembro: si abandonás la organización, se eliminará.",
                        codigo="organizacion_se_eliminara",
                    ),
                    auditoria.MEMBRESIA_ABANDONO, usuario, organizacion, "falta_confirmacion",
                )
            self._auditar(
                auditoria.MEMBRESIA_ABANDONO, auditoria.EXITOSO, usuario, organizacion,
                {"organizacion_eliminada": True},
            )
            self._eliminar(organizacion, usuario, avisar=False)
            return True

        referente = self.repositorio.referente(organizacion.id).usuario
        self._auditar(auditoria.MEMBRESIA_ABANDONO, auditoria.EXITOSO, usuario, organizacion)
        self.repositorio.quitar(membresia)
        self.repositorio.confirmar()
        self.correos.enviar_aviso_abandono(referente, organizacion, usuario)
        return False

    # --- Invitaciones (RF12, RF13) ---

    def invitaciones(self, id_organizacion, usuario):
        """Invitaciones pendientes de la organización. Solo el Referente."""
        organizacion, membresia = self._acceso(id_organizacion, usuario)
        if not membresia.es_referente:
            raise AccesoDenegado(MENSAJE_SOLO_REFERENTE)
        return self.repositorio.invitaciones_pendientes(organizacion.id)

    def _enviar_invitacion(self, invitacion, invitante):
        token = self.tokens.generar(PROPOSITO_INVITACION, {"id": invitacion.id})
        registrado = self.usuarios.existe_correo(invitacion.correo)
        self.correos.enviar_invitacion(invitacion, invitante, token, registrado)

    def invitar(self, id_organizacion, usuario, correo, cargo=None):
        """Invita a un correo, registrado o no (RF12). Solo el Referente.

        Raises:
            ConflictoDatos: si ya es miembro, si ya tiene una invitación
                vigente o si se alcanzó el límite de miembros del plan.
        """
        accion = auditoria.INVITACION_ENVIO
        organizacion = self._como_referente(id_organizacion, usuario, accion)
        correo = correo.strip().lower()
        ahora = ahora_utc()
        detalle = {"correo": correo}
        if self.repositorio.es_miembro_por_correo(organizacion.id, correo):
            mensaje = "Esa persona ya es miembro de la organización."
            self._rechazar(
                ConflictoDatos(mensaje, {"correo": mensaje}, codigo="ya_es_miembro"),
                accion, usuario, organizacion, "ya_es_miembro", detalle,
            )
        existente = self.repositorio.invitacion_pendiente(organizacion.id, correo)
        if existente is not None and existente.vigente(ahora):
            mensaje = "Ese correo ya tiene una invitación pendiente. Podés reenviarla."
            self._rechazar(
                ConflictoDatos(mensaje, {"correo": mensaje}, codigo="ya_invitado"),
                accion, usuario, organizacion, "ya_invitado", detalle,
            )
        limite = self.limite_de_miembros(organizacion)
        ocupados = self.repositorio.cantidad_de_miembros(organizacion.id) + (
            self.repositorio.cantidad_de_invitaciones_vigentes(organizacion.id, ahora)
        )
        if ocupados >= limite:
            mensaje = (
                f"La organización alcanzó el límite de {limite} miembros de su plan "
                f"({self.nombre_del_plan(organizacion)}), contando las invitaciones "
                "pendientes. Cancelá una invitación o ampliá el plan para invitar a alguien más."
            )
            self._rechazar(
                ConflictoDatos(mensaje, {"correo": mensaje}, codigo="limite_del_plan"),
                accion, usuario, organizacion, "limite_del_plan", {**detalle, "limite": limite},
            )

        # Una invitación pendiente pero vencida se renueva en lugar de duplicarse.
        invitacion = existente or Invitacion(organizacion=organizacion, correo=correo)
        invitacion.cargo = cargo or None
        invitacion.id_invitante = usuario.id
        invitacion.vence_en = ahora + self.configuracion["VIGENCIA_INVITACION"]
        self.repositorio.preparar(invitacion)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, organizacion,
            {**detalle, "id_invitacion": invitacion.id, "cargo": invitacion.cargo,
             "vence_en": invitacion.vence_en.isoformat()},
        )
        self.repositorio.confirmar()
        self._enviar_invitacion(invitacion, usuario)
        return invitacion

    def _invitacion_pendiente_de(self, organizacion, id_invitacion):
        invitacion = self.repositorio.invitacion(id_invitacion)
        if (
            invitacion is None or invitacion.id_organizacion != organizacion.id
            or invitacion.estado != INVITACION_PENDIENTE
        ):
            raise NoEncontrado("La invitación no existe o ya fue respondida.")
        return invitacion

    def reenviar_invitacion(self, id_organizacion, usuario, id_invitacion):
        """Reenvía una invitación pendiente y renueva su vencimiento (RF12 CA4)."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.INVITACION_REENVIO
        )
        invitacion = self._invitacion_pendiente_de(organizacion, id_invitacion)
        invitacion.vence_en = ahora_utc() + self.configuracion["VIGENCIA_INVITACION"]
        self._auditar(
            auditoria.INVITACION_REENVIO, auditoria.EXITOSO, usuario, organizacion,
            {"id_invitacion": invitacion.id, "correo": invitacion.correo,
             "vence_en": invitacion.vence_en.isoformat()},
        )
        self.repositorio.confirmar()
        self._enviar_invitacion(invitacion, usuario)
        return invitacion

    def cancelar_invitacion(self, id_organizacion, usuario, id_invitacion):
        """Cancela una invitación pendiente (RF12 CA4)."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.INVITACION_CANCELACION
        )
        invitacion = self._invitacion_pendiente_de(organizacion, id_invitacion)
        invitacion.estado = INVITACION_CANCELADA
        self._auditar(
            auditoria.INVITACION_CANCELACION, auditoria.EXITOSO, usuario, organizacion,
            {"id_invitacion": invitacion.id, "correo": invitacion.correo},
        )
        self.repositorio.confirmar()

    def consultar_invitacion(self, token):
        """Datos de la invitación del enlace, sin sesión (CU11 paso 2).

        El token solo sirve para consultar; responder exige iniciar sesión
        con el correo invitado.

        Raises:
            TokenInvalido: si el enlace fue alterado o la invitación no existe.
        """
        datos = self.tokens.leer(
            PROPOSITO_INVITACION, token, self.configuracion["VIGENCIA_INVITACION"]
        )
        invitacion = self.repositorio.invitacion(datos["id"])
        if invitacion is None:
            raise TokenInvalido("La invitación ya no existe.", "no_corresponde")
        return invitacion

    def pendientes_de(self, usuario):
        """Invitaciones pendientes y vigentes al correo del usuario (CU11 3a)."""
        return self.repositorio.invitaciones_pendientes_de_correo(usuario.correo, ahora_utc())

    def responder(self, id_invitacion, usuario, aceptar):
        """Acepta o rechaza una invitación (RF13).

        Solo puede responderla quien inició sesión con el correo invitado
        (RN10). Al aceptar, el usuario se incorpora como Miembro con el cargo
        de la invitación. En ambos casos se avisa al Referente.
        """
        accion = auditoria.INVITACION_ACEPTACION if aceptar else auditoria.INVITACION_RECHAZO
        invitacion = self.repositorio.invitacion(id_invitacion)
        if invitacion is None:
            raise NoEncontrado("La invitación no existe.")
        organizacion = invitacion.organizacion
        detalle = {"id_invitacion": invitacion.id}
        if invitacion.correo != usuario.correo:
            self._rechazar(
                AccesoDenegado(
                    "Esta invitación es para otro correo. Iniciá sesión con el correo invitado "
                    "para responderla.",
                    codigo="correo_distinto",
                ),
                accion, usuario, organizacion, "correo_distinto", detalle,
            )
        if not invitacion.vigente(ahora_utc()):
            self._rechazar(
                ConflictoDatos("La invitación ya no está vigente.", codigo="invitacion_no_vigente"),
                accion, usuario, organizacion, "no_vigente",
                {**detalle, "estado": invitacion.estado},
            )

        invitacion.respondida_en = ahora_utc()
        if aceptar:
            invitacion.estado = INVITACION_ACEPTADA
            if self.repositorio.membresia(organizacion.id, usuario.id) is None:
                organizacion.membresias.append(
                    Membresia(id_usuario=usuario.id, rol=ROL_MIEMBRO, cargo=invitacion.cargo)
                )
        else:
            invitacion.estado = INVITACION_RECHAZADA
        self._auditar(accion, auditoria.EXITOSO, usuario, organizacion, detalle)
        self.repositorio.confirmar()
        referente = self.repositorio.referente(organizacion.id)
        self.correos.enviar_respuesta_invitacion(referente.usuario, invitacion, aceptar)
        return organizacion
