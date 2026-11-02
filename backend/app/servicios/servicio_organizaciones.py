"""Organizaciones, invitaciones y membresías.

Concentra las reglas de la funcionalidad 004: quién puede hacer cada
operación, exactamente un Referente por organización, límite de miembros del
plan, vigencia de las invitaciones, abandono y eliminación. Cada operación,
exitosa o rechazada, queda en la auditoría en la misma transacción.

Permisos: quien no es miembro recibe ``NoEncontrado`` (no se revela si la
organización existe); un Miembro que intenta algo reservado al Referente
recibe ``AccesoDenegado``.

Desde la funcionalidad 021, las aseguradoras se crean al registrarlas desde
el catálogo de la SSN, quedan pendientes hasta que el Administrador las
aprueba, y las cuentas con perfil Aseguradora que se quedan sin aseguradora
se desactivan.

Desde la funcionalidad 032, toda organización nueva elige su plan y espera el
pago (estado «pago pendiente»): el estudio queda activo al acreditarse y la
aseguradora pasa a esperar la aprobación. Mientras no esté activa no se puede
invitar ni crear casos en ella.

Realiza: RF10 a RF18 (sin las reglas de casos, que agrega la 005); RN06,
RN07, RN08, RN10, RN11, RN15, RN36 a RN40; RNF06.
"""
from app.modelos.organizacion import (
    INVITACION_ACEPTADA,
    ORGANIZACION_ACTIVA,
    ORGANIZACION_PAGO_PENDIENTE,
    TIPO_ASEGURADORA,
    TIPO_ESTUDIO_JURIDICO,
    INVITACION_CANCELADA,
    INVITACION_PENDIENTE,
    INVITACION_RECHAZADA,
    ROL_MIEMBRO,
    ROL_REFERENTE,
    Invitacion,
    Membresia,
    Organizacion,
)
from app.modelos.usuario import PERFIL_ABOGADO, PERFIL_ASEGURADORA, ROL_ADMINISTRADOR
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
MENSAJE_SOLO_ADMINISTRADOR = "Solo el Administrador de la plataforma puede hacer esto."
CAMPOS_EDITABLES = ("nombre", "correo_contacto", "telefono")


# Concentra todas las reglas de la organización (raíz del agregado): separarlas
# repartiría la misma transacción y los mismos permisos entre varias clases.
# pylint: disable-next=too-many-instance-attributes,too-many-public-methods
class ServicioOrganizaciones:
    """Operaciones sobre organizaciones, sus miembros y sus invitaciones."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, usuarios, correos, tokens, configuracion, registro, casos=None,
        archivos=None, pagos=None,
    ):
        """
        Args:
            repositorio: ``RepositorioOrganizaciones``.
            usuarios: ``RepositorioUsuarios``, para saber si un correo está registrado.
            registro: ``ServicioAuditoria``.
            casos: ``RepositorioCasos``, para aplicar a los casos de la
                organización las reglas de salida y eliminación (funcionalidad 005).
            archivos: ``ArchivosDeCasos``, que borra las imágenes de los casos
                que se eliminan con la organización (RN21, funcionalidad 006).
            pagos: ``ServicioPagos``, que cobra el plan (funcionalidad 032).
        """
        self.pagos = pagos
        self.casos = casos
        self.archivos = archivos
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

    def crear(self, usuario, datos, confirmar=True):
        """Crea un estudio jurídico con el creador como Referente y su cobro (RF10, 032).

        El estudio queda con «pago pendiente» hasta que se acredita el pago del
        plan elegido.

        Args:
            datos: diccionario con ``nombre``, ``tipo``, ``plan`` (Básico si
                falta) y, opcionales, ``correo_contacto`` y ``telefono``.
            confirmar: False cuando se crea dentro del registro de la cuenta,
                que confirma todo junto.

        Returns:
            ``(organizacion, token)``: el token del enlace de pago solo existe acá.
        """
        if usuario.perfil != PERFIL_ABOGADO:
            raise AccesoDenegado(
                "Las aseguradoras se registran desde el registro de la plataforma; "
                "sus empleados se suman por invitación."
            )
        if datos["tipo"] != TIPO_ESTUDIO_JURIDICO:
            mensaje = "Solo podés crear organizaciones del tipo Estudio Jurídico."
            raise ErrorValidacion(mensaje, {"tipo": mensaje})
        plan = datos.get("plan") or self.configuracion["PLAN_INICIAL_ORGANIZACION"]
        self.pagos.exigir_plan(plan)
        organizacion = Organizacion(
            nombre=datos["nombre"], tipo=datos["tipo"],
            correo_contacto=datos.get("correo_contacto") or None,
            telefono=datos.get("telefono") or None,
            plan=plan, estado=ORGANIZACION_PAGO_PENDIENTE,
        )
        organizacion.membresias.append(Membresia(id_usuario=usuario.id, rol=ROL_REFERENTE))
        self.repositorio.preparar(organizacion)
        self._auditar(
            auditoria.ORGANIZACION_CREACION, auditoria.EXITOSO, usuario, organizacion,
            {"nombre": organizacion.nombre, "tipo": organizacion.tipo, "plan": organizacion.plan,
             "estado": organizacion.estado},
        )
        _, token = self.pagos.crear_cobro(plan, organizacion=organizacion, usuario=usuario)
        if confirmar:
            self.repositorio.confirmar()
        return organizacion, token

    def retomar_pago(self, id_organizacion, usuario):
        """Genera un enlace de pago nuevo para una organización con el pago pendiente.

        Solo el Referente. Sirve si se cerró la pantalla de pago (CA7 de la 032).

        Returns:
            ``(organizacion, token)``.

        Raises:
            ConflictoDatos: si la organización no tiene el pago pendiente.
        """
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.ORGANIZACION_COBRO
        )
        if not organizacion.pago_pendiente:
            raise ConflictoDatos("La organización no tiene pagos pendientes.", codigo="sin_pago")
        _, token = self.pagos.crear_cobro(
            organizacion.plan, organizacion=organizacion, usuario=usuario
        )
        self.repositorio.confirmar()
        return organizacion, token

    def obtener(self, id_organizacion, usuario):
        """Devuelve ``(organizacion, membresia)`` si el usuario es miembro."""
        return self._acceso(id_organizacion, usuario)

    def editar(self, id_organizacion, usuario, cambios):
        """Modifica los datos de la organización (RF11). Solo el Referente."""
        organizacion = self._como_referente(
            id_organizacion, usuario, auditoria.ORGANIZACION_EDICION
        )
        if cambios.get("tipo") not in (None, organizacion.tipo):
            mensaje = "El tipo de organización no puede cambiarse."
            raise ErrorValidacion(mensaje, {"tipo": mensaje})
        if organizacion.es_aseguradora and cambios.get("nombre") not in (None, organizacion.nombre):
            mensaje = "El nombre de una aseguradora es el del catálogo de la SSN y no se modifica."
            raise ErrorValidacion(mensaje, {"nombre": mensaje})
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

    def _desactivar_si_corresponde(self, miembro, organizacion, actor):
        """Desactiva la cuenta si se queda sin aseguradora (RN39).

        Solo aplica al perfil Aseguradora al salir de una aseguradora. Cierra
        sus sesiones abiertas incrementando la versión de sesión. No confirma:
        se guarda junto con la acción que la provoca.

        Returns:
            True si la cuenta quedó desactivada.
        """
        if (
            miembro.perfil != PERFIL_ASEGURADORA or not organizacion.es_aseguradora
            or self.repositorio.pertenece_a_otra_aseguradora(miembro.id, organizacion.id)
        ):
            return False
        miembro.activo = False
        miembro.version_sesion += 1
        self.registro.registrar(
            auditoria.CUENTA_DESACTIVACION, auditoria.EXITOSO, usuario=actor, recurso=miembro,
            detalle={"motivo": "sin_aseguradora", "id_organizacion": organizacion.id},
        )
        return True

    def _eliminar(self, organizacion, usuario, avisar, motivo="eliminacion"):
        """Elimina la organización con sus membresías e invitaciones (RN09 sin casos).

        Returns:
            True si la cuenta de ``usuario`` quedó desactivada (RN39).
        """
        nombre = organizacion.nombre
        miembros = [m.usuario for m in organizacion.membresias]
        self._auditar(
            auditoria.ORGANIZACION_ELIMINACION, auditoria.EXITOSO, usuario, organizacion,
            {"nombre": nombre, "miembros": len(miembros), "motivo": motivo,
             "casos_eliminados": self.cantidad_de_casos(organizacion),
             "sha256_eliminados": self._preparar_archivos(organizacion)},
        )
        desactivados = {
            miembro.id for miembro in miembros
            if self._desactivar_si_corresponde(miembro, organizacion, usuario)
        }
        self._quitar_con_casos(organizacion)
        self.repositorio.confirmar()
        self.borrar_archivos_pendientes()
        if avisar:
            for miembro in miembros:
                if miembro.id != usuario.id:
                    self.correos.enviar_aviso_eliminacion_organizacion(
                        miembro, nombre, miembro.id in desactivados
                    )
        return usuario.id in desactivados

    def _preparar_archivos(self, organizacion):
        """Anota los archivos de los casos de la organización y devuelve sus huellas (RN21)."""
        if not (self.archivos and self.casos):
            return []
        return self.archivos.preparar(self.casos.casos_de_organizacion(organizacion.id))

    def borrar_archivos_pendientes(self):
        """Borra del almacenamiento los archivos de los casos ya eliminados (RN21)."""
        if self.archivos:
            self.archivos.borrar_pendientes()

    def _quitar_con_casos(self, organizacion):
        """Suma a la transacción la eliminación de la organización y sus casos (RN09, RF18)."""
        for caso in self.casos.casos_de_organizacion(organizacion.id) if self.casos else []:
            self.repositorio.quitar(caso)
        self.repositorio.quitar(organizacion)

    def eliminar_por_baja(self, organizacion, usuario):
        """Elimina la organización de la que ``usuario`` es el único miembro, en su baja.

        No confirma: la baja confirma todo junto, así no queda una baja a
        medias si algo falla (RN08, RN09; CU06 2c). Después de confirmar, la
        baja llama a ``borrar_archivos_pendientes``.
        """
        self._auditar(
            auditoria.ORGANIZACION_ELIMINACION, auditoria.EXITOSO, usuario, organizacion,
            {"nombre": organizacion.nombre, "miembros": 1, "motivo": "baja_de_cuenta",
             "casos_eliminados": self.cantidad_de_casos(organizacion),
             "sha256_eliminados": self._preparar_archivos(organizacion)},
        )
        self._quitar_con_casos(organizacion)

    def eliminar(self, id_organizacion, usuario, confirmacion):
        """Elimina la organización si se escribe su nombre exacto (RF18). Solo el Referente.

        Returns:
            True si la cuenta del Referente quedó desactivada (RN39).
        """
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
        return self._eliminar(organizacion, usuario, avisar=True)

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
        self._reasignar_casos(organizacion, desvinculado, usuario)
        desactivada = self._desactivar_si_corresponde(desvinculado, organizacion, usuario)
        self.repositorio.quitar(membresia)
        self.repositorio.confirmar()
        self.correos.enviar_aviso_desvinculacion(desvinculado, organizacion, desactivada)

    def cantidad_de_casos(self, organizacion):
        """Cantidad de casos de la organización (RF18 CA1)."""
        return self.casos.cantidad_de_organizacion(organizacion.id) if self.casos else 0

    def _quitar_accesos(self, organizacion, miembro):
        """Quita los accesos individuales del miembro a casos de la organización."""
        for acceso in self.casos.accesos_en_organizacion(miembro.id, organizacion.id):
            self.repositorio.quitar(acceso)

    def _reasignar_casos(self, organizacion, desvinculado, referente):
        """Pasa al Referente los casos del desvinculado y le quita sus accesos (RN14, RF14 CA2).

        No confirma: se guarda junto con la desvinculación.
        """
        if not self.casos:
            return
        reasignados = []
        for caso in self.casos.casos_a_cargo_en(desvinculado.id, organizacion.id):
            propio = self.casos.acceso_individual(caso.id, referente.id)
            if propio is not None:
                self.repositorio.quitar(propio)
            caso.id_responsable = referente.id
            reasignados.append(caso.numero)
        self._quitar_accesos(organizacion, desvinculado)
        if reasignados:
            self._auditar(
                auditoria.CASO_TRANSFERENCIA, auditoria.EXITOSO, referente, organizacion,
                {"motivo": "desvinculacion", "casos": reasignados, "anterior": desvinculado.id,
                 "nuevo": referente.id},
            )

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
            ``(organizacion_eliminada, cuenta_desactivada)``: si la organización
            se eliminó porque era su único miembro y si la cuenta del usuario
            quedó desactivada por quedarse sin aseguradora (RN39).
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
            return True, self._eliminar(organizacion, usuario, avisar=False, motivo="abandono")

        a_cargo = self.casos.casos_a_cargo_en(usuario.id, organizacion.id) if self.casos else []
        if a_cargo:
            self._rechazar(
                ConflictoDatos(
                    f"Sos Responsable de {len(a_cargo)} "
                    f"{'caso' if len(a_cargo) == 1 else 'casos'} de la organización: "
                    "transferilos a otro miembro antes de abandonarla.",
                    codigo="debe_transferir_casos",
                ),
                auditoria.MEMBRESIA_ABANDONO, usuario, organizacion, "tiene_casos",
                {"casos": [caso.numero for caso in a_cargo]},
            )
        referente = self.repositorio.referente(organizacion.id).usuario
        self._auditar(auditoria.MEMBRESIA_ABANDONO, auditoria.EXITOSO, usuario, organizacion)
        if self.casos:
            self._quitar_accesos(organizacion, usuario)
        desactivada = self._desactivar_si_corresponde(usuario, organizacion, usuario)
        self.repositorio.quitar(membresia)
        self.repositorio.confirmar()
        self.correos.enviar_aviso_abandono(referente, organizacion, usuario)
        return False, desactivada

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
        if organizacion.pago_pendiente:
            self._rechazar(
                ConflictoDatos(
                    "Falta acreditar el pago del plan. Vas a poder invitar a tu equipo "
                    "cuando se acredite.",
                    codigo="pago_pendiente",
                ),
                accion, usuario, organizacion, "pago_pendiente", detalle,
            )
        if organizacion.pendiente:
            self._rechazar(
                ConflictoDatos(
                    "La aseguradora todavía no fue aprobada por el Administrador de la "
                    "plataforma. Vas a poder invitar a tu equipo cuando esté aprobada.",
                    codigo="organizacion_pendiente",
                ),
                accion, usuario, organizacion, "organizacion_pendiente", detalle,
            )
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

        if aceptar:
            self._incorporar(invitacion, usuario)
        else:
            invitacion.respondida_en = ahora_utc()
            invitacion.estado = INVITACION_RECHAZADA
            self._auditar(accion, auditoria.EXITOSO, usuario, organizacion, detalle)
        self.repositorio.confirmar()
        self._avisar_respuesta(invitacion, aceptar)
        return organizacion

    def _incorporar(self, invitacion, usuario):
        """Suma al usuario como Miembro y, si estaba desactivado, lo reactiva (RN39).

        No confirma: se guarda junto con la operación que la provoca.
        """
        organizacion = invitacion.organizacion
        invitacion.respondida_en = ahora_utc()
        invitacion.estado = INVITACION_ACEPTADA
        if self.repositorio.membresia(organizacion.id, usuario.id) is None:
            organizacion.membresias.append(
                Membresia(id_usuario=usuario.id, rol=ROL_MIEMBRO, cargo=invitacion.cargo)
            )
        self._auditar(
            auditoria.INVITACION_ACEPTACION, auditoria.EXITOSO, usuario, organizacion,
            {"id_invitacion": invitacion.id},
        )
        if not usuario.activo:
            usuario.activo = True
            self.registro.registrar(
                auditoria.CUENTA_REACTIVACION, auditoria.EXITOSO, usuario=usuario,
                recurso=usuario, detalle={"id_organizacion": organizacion.id},
            )

    def _avisar_respuesta(self, invitacion, aceptada):
        referente = self.repositorio.referente(invitacion.id_organizacion)
        self.correos.enviar_respuesta_invitacion(referente.usuario, invitacion, aceptada)

    def tiene_invitaciones_vigentes(self, correo):
        """True si el correo tiene invitaciones pendientes y vigentes (RN39)."""
        return bool(self.repositorio.invitaciones_pendientes_de_correo(correo, ahora_utc()))

    def incorporar_al_verificar(self, usuario):
        """Acepta las invitaciones vigentes de aseguradoras al verificar el correo (CA11 de la 021).

        Quien crea su cuenta desde la invitación de una aseguradora queda
        dentro de ella sin otro paso. No confirma: la verificación del correo
        confirma todo junto.

        Returns:
            Las invitaciones aceptadas, para avisar a sus Referentes después de confirmar.
        """
        aceptadas = [
            invitacion for invitacion in self.pendientes_de(usuario)
            if invitacion.organizacion.es_aseguradora
            and usuario.perfil == PERFIL_ASEGURADORA
        ]
        for invitacion in aceptadas:
            self._incorporar(invitacion, usuario)
        return aceptadas

    def avisar_incorporaciones(self, invitaciones):
        """Avisa a cada Referente que su invitación fue aceptada."""
        for invitacion in invitaciones:
            self._avisar_respuesta(invitacion, True)

    def invitacion_para_registro(self, token, correo):
        """Valida la invitación usada para registrarse (CA10 y CA12 de la 021).

        Raises:
            TokenInvalido: si el enlace no es válido.
            ConflictoDatos: si la invitación ya no está vigente.
            ErrorValidacion: si el correo no es el invitado.
        """
        invitacion = self.consultar_invitacion(token)
        if not invitacion.vigente(ahora_utc()):
            raise ConflictoDatos(
                "La invitación ya no está vigente.", codigo="invitacion_no_vigente"
            )
        if invitacion.correo != correo.strip().lower():
            mensaje = f"Tenés que registrarte con el correo invitado: {invitacion.correo}."
            raise ErrorValidacion(mensaje, {"correo": mensaje})
        return invitacion

    # --- Aseguradoras (funcionalidad 021) ---

    def exigir_aseguradora_libre(self, aseguradora):
        """Rechaza registrar una aseguradora que ya tiene organización (RN37).

        Raises:
            ConflictoDatos: con la indicación de pedir una invitación.
        """
        if self.repositorio.obtener_por_cuit(aseguradora.cuit) is not None:
            mensaje = (
                f"{aseguradora.denominacion} ya está registrada en la plataforma. Pedile a su "
                "Referente que te invite."
            )
            raise ConflictoDatos(
                mensaje, {"id_aseguradora": mensaje}, codigo="aseguradora_registrada"
            )

    def crear_aseguradora(self, usuario, aseguradora, plan=None):
        """Crea la organización de una aseguradora del catálogo con el usuario como Referente.

        Primero espera el pago del plan (032) y después la aprobación del
        Administrador (RN38). No confirma: se guarda junto con el registro de
        la cuenta.

        Returns:
            ``(organizacion, token)``: el token del enlace de pago.

        Raises:
            ConflictoDatos: si esa aseguradora ya está registrada (RN37).
        """
        self.exigir_aseguradora_libre(aseguradora)
        plan = plan or self.configuracion["PLAN_INICIAL_ORGANIZACION"]
        self.pagos.exigir_plan(plan)
        organizacion = Organizacion(
            nombre=aseguradora.denominacion, tipo=TIPO_ASEGURADORA, cuit=aseguradora.cuit,
            plan=plan, estado=ORGANIZACION_PAGO_PENDIENTE,
        )
        organizacion.membresias.append(Membresia(id_usuario=usuario.id, rol=ROL_REFERENTE))
        self.repositorio.preparar(organizacion)
        self._auditar(
            auditoria.ORGANIZACION_CREACION, auditoria.EXITOSO, usuario, organizacion,
            {"nombre": organizacion.nombre, "tipo": organizacion.tipo, "cuit": organizacion.cuit,
             "plan": organizacion.plan, "estado": organizacion.estado, "origen": "registro"},
        )
        _, token = self.pagos.crear_cobro(plan, organizacion=organizacion, usuario=usuario)
        return organizacion, token

    def _exigir_administrador(self, usuario):
        if usuario.rol != ROL_ADMINISTRADOR:
            raise AccesoDenegado(MENSAJE_SOLO_ADMINISTRADOR)

    def pendientes_de_aprobacion(self, usuario):
        """Aseguradoras pendientes con su Referente (CA7 de la 021). Solo el Administrador."""
        self._exigir_administrador(usuario)
        return [
            (organizacion, self.repositorio.referente(organizacion.id))
            for organizacion in self.repositorio.pendientes_de_aprobacion()
        ]

    def _pendiente(self, id_organizacion):
        organizacion = self.repositorio.obtener(id_organizacion)
        if organizacion is None or not organizacion.pendiente:
            raise NoEncontrado("La aseguradora no existe o ya fue revisada.")
        return organizacion

    def aprobar(self, usuario, id_organizacion):
        """Aprueba una aseguradora pendiente y avisa a su Referente (CA8 de la 021)."""
        self._exigir_administrador(usuario)
        organizacion = self._pendiente(id_organizacion)
        organizacion.estado = ORGANIZACION_ACTIVA
        organizacion.aprobada_en = ahora_utc()
        self._auditar(
            auditoria.ORGANIZACION_APROBACION, auditoria.EXITOSO, usuario, organizacion,
            {"cuit": organizacion.cuit},
        )
        self.repositorio.confirmar()
        referente = self.repositorio.referente(organizacion.id).usuario
        self.correos.enviar_aviso_aseguradora_aprobada(referente, organizacion)
        return organizacion

    def rechazar(self, usuario, id_organizacion, motivo):
        """Rechaza una aseguradora pendiente: se elimina y su Referente se desactiva (CA9).

        Se avisa al Referente con el motivo. Así la empresa queda libre para
        que la registre quien corresponda.
        """
        self._exigir_administrador(usuario)
        organizacion = self._pendiente(id_organizacion)
        referente = self.repositorio.referente(organizacion.id).usuario
        nombre = organizacion.nombre
        self._auditar(
            auditoria.ORGANIZACION_RECHAZO, auditoria.EXITOSO, usuario, organizacion,
            {"cuit": organizacion.cuit, "motivo": motivo},
        )
        # Lo pagado se devuelve (simulado) antes de eliminarla (CA6 de la 032).
        self.pagos.devolver_cobros(organizacion, usuario)
        self._eliminar(organizacion, usuario, avisar=False, motivo="rechazo")
        self.correos.enviar_aviso_aseguradora_rechazada(referente, nombre, motivo)
