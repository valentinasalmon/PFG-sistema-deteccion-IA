"""Casos: creación, consulta, edición, estados, accesos, transferencia y eliminación.

Permisos (RN20): el Responsable puede todo; el Colaborador consulta y edita;
el Lector solo consulta. Quien no tiene permiso recibe ``NoEncontrado``, como
si el caso no existiera (RNF05). Cada operación, exitosa o rechazada, queda
en la auditoría en la misma transacción.

Realiza: RF23 a RF33; RN12, RN13, RN16 a RN21, RN30; RNF05, RNF06.
"""
from datetime import date, timedelta
from uuid import uuid4

from app.modelos.caso import (
    ESTADO_ANALIZADO,
    ESTADO_ARCHIVADO,
    ESTADO_BORRADOR,
    ESTADO_CERRADO,
    ESTADO_EN_ANALISIS,
    NIVEL_COLABORACION,
    NIVEL_LECTURA,
    AccesoCaso,
    Caso,
    normalizar_texto,
)
from app.modelos.organizacion import ORGANIZACION_ACTIVA
from app.modelos.usuario import PERFIL_ASEGURADORA
from app.servicios import auditoria
from app.servicios.errores import AccesoDenegado, ConflictoDatos, ErrorValidacion, NoEncontrado
from app.utilidades.tiempo import ahora_utc

PERMISO_RESPONSABLE = "responsable"
JERARQUIA = {NIVEL_LECTURA: 1, NIVEL_COLABORACION: 2, PERMISO_RESPONSABLE: 3}
ESTADOS_EDITABLES = (ESTADO_BORRADOR, ESTADO_ANALIZADO)
CAMPOS_EDITABLES = ("tipo", "fecha_hecho", "lugar", "expediente", "descripcion")
ANIOS_DE_RETENCION = 5  # RN30: plazo de prescripción genérico (CCyC, art. 2560)

MENSAJE_NO_ENCONTRADO = "El caso no existe o no tenés acceso a él."
MENSAJE_SOLO_RESPONSABLE = "Solo el Responsable del caso puede hacer esto."


DIAS_AVISO_RETENCION = 30  # RN31
ESTADOS_CON_RETENCION = (ESTADO_CERRADO, ESTADO_ARCHIVADO)


def sumar_un_anio(momento):
    """El mismo instante un año después (el 29 de febrero pasa al 28)."""
    try:
        return momento.replace(year=momento.year + 1)
    except ValueError:
        return momento.replace(year=momento.year + 1, day=28)


def vencimiento_de_retencion(caso):
    """Fecha en que vence la retención de un caso cerrado o archivado (RN30), o None."""
    if caso.retencion_desde is None:
        return None
    desde = caso.retencion_desde
    try:
        return desde.replace(year=desde.year + ANIOS_DE_RETENCION)
    except ValueError:  # 29 de febrero
        return desde.replace(year=desde.year + ANIOS_DE_RETENCION, day=28)


class ServicioCasos:  # pylint: disable=too-many-public-methods
    """Operaciones sobre casos y sus accesos."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorio, organizaciones, usuarios, correos, registro, archivos=None
    ):
        """
        Args:
            repositorio: ``RepositorioCasos``.
            organizaciones: ``RepositorioOrganizaciones``, para membresías.
            usuarios: ``RepositorioUsuarios``, para transferir casos personales.
            registro: ``ServicioAuditoria``.
            archivos: ``ArchivosDeCasos``, que borra las imágenes de los casos
                eliminados (RN21).
        """
        self.repositorio = repositorio
        self.organizaciones = organizaciones
        self.usuarios = usuarios
        self.correos = correos
        self.registro = registro
        self.archivos = archivos

    # --- Permisos ---

    def permiso(self, caso, usuario):
        """Permiso efectivo del usuario sobre el caso: el más alto que tenga (RF30 CA3).

        Returns:
            ``"responsable"``, ``"colaboracion"``, ``"lectura"`` o None.
        """
        if caso.id_responsable == usuario.id:
            return PERMISO_RESPONSABLE
        if caso.es_personal:
            return None
        if self.organizaciones.membresia(caso.id_organizacion, usuario.id) is None:
            return None
        niveles = [
            acceso.nivel for acceso in (
                self.repositorio.acceso_individual(caso.id, usuario.id),
                self.repositorio.acceso_de_organizacion(caso.id),
            ) if acceso is not None
        ]
        return max(niveles, key=JERARQUIA.get) if niveles else None

    def _auditar(self, accion, resultado, usuario, caso, detalle=None, confirmar=False):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        return self.registro.registrar(
            accion, resultado, usuario=usuario, recurso=(auditoria.TIPO_CASO, caso.id),
            detalle={"numero": caso.numero, **(detalle or {})}, confirmar=confirmar,
        )

    def _rechazar(self, error, accion, usuario, caso, motivo):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        self._auditar(accion, auditoria.RECHAZADO, usuario, caso, {"motivo": motivo}, True)
        raise error

    def _caso(self, id_caso, usuario, minimo, accion=None):
        """Devuelve ``(caso, permiso)`` si el usuario alcanza el permiso mínimo.

        Sin ningún permiso: ``NoEncontrado`` (RNF05). Con un permiso menor:
        se registra el rechazo y ``AccesoDenegado``.
        """
        caso = self.repositorio.obtener(id_caso)
        permiso = self.permiso(caso, usuario) if caso is not None else None
        if permiso is None:
            raise NoEncontrado(MENSAJE_NO_ENCONTRADO)
        if JERARQUIA[permiso] < JERARQUIA[minimo]:
            mensaje = (
                MENSAJE_SOLO_RESPONSABLE if minimo == PERMISO_RESPONSABLE
                else "Tu permiso sobre este caso es de solo lectura."
            )
            self._rechazar(AccesoDenegado(mensaje), accion, usuario, caso, "permiso_insuficiente")
        return caso, permiso

    def caso_con_permiso(self, id_caso, usuario, minimo, accion=None):
        """Devuelve ``(caso, permiso)`` si el usuario alcanza el permiso mínimo.

        Lo usan los servicios que trabajan dentro de un caso, como las
        imágenes, para aplicar los mismos permisos (RN20, RNF05).
        """
        return self._caso(id_caso, usuario, minimo, accion)

    @staticmethod
    def _tocar(caso):
        caso.actualizado_en = ahora_utc()

    # --- Crear y consultar (RF23, RF24, RF26) ---

    def _validar_fecha(self, fecha):
        if fecha > date.today():
            mensaje = "La fecha del hecho no puede ser posterior a hoy."
            raise ErrorValidacion(mensaje, {"fecha_hecho": mensaje})

    def _espacio(self, usuario, espacio):
        """Valida el espacio elegido y devuelve el id de la organización o None (RN12)."""
        if espacio == "personal":
            if usuario.perfil == PERFIL_ASEGURADORA:
                mensaje = (
                    "Como parte de una aseguradora, tus casos son de la aseguradora: "
                    "elegila como espacio de trabajo."
                )
                raise ErrorValidacion(mensaje, {"espacio": mensaje})
            return None
        try:
            id_organizacion = int(espacio)
        except (TypeError, ValueError) as error:
            raise ErrorValidacion(
                "El espacio no es válido.", {"espacio": "El espacio no es válido."}
            ) from error
        membresia = self.organizaciones.membresia(id_organizacion, usuario.id)
        if membresia is None or membresia.organizacion.estado != ORGANIZACION_ACTIVA:
            mensaje = "Solo podés crear casos en organizaciones activas de las que sos miembro."
            raise ErrorValidacion(mensaje, {"espacio": mensaje})
        return id_organizacion

    def crear(self, usuario, datos):
        """Crea un caso en Borrador con el usuario como Responsable (RF23).

        Args:
            datos: ``espacio`` (``"personal"`` o id de organización), ``tipo``,
                ``fecha_hecho``, ``lugar`` y, opcionales, ``expediente`` y ``descripcion``.
        """
        self._validar_fecha(datos["fecha_hecho"])
        id_organizacion = self._espacio(usuario, datos["espacio"])
        ahora = ahora_utc()
        caso = Caso(
            # Número provisorio: el definitivo usa el identificador (secuencia global, RN16).
            numero=f"TMP-{uuid4().hex[:16]}",
            id_organizacion=id_organizacion, id_responsable=usuario.id,
            tipo=datos["tipo"], fecha_hecho=datos["fecha_hecho"], lugar=datos["lugar"],
            expediente=datos.get("expediente") or None,
            expediente_normalizado=normalizar_texto(datos.get("expediente")),
            descripcion=datos.get("descripcion") or None,
            estado=ESTADO_BORRADOR, creado_en=ahora, actualizado_en=ahora,
        )
        self.repositorio.preparar(caso)
        caso.numero = f"CASO-{ahora.year}-{caso.id:06d}"
        self._auditar(
            auditoria.CASO_CREACION, auditoria.EXITOSO, usuario, caso,
            {"espacio": "personal" if id_organizacion is None else id_organizacion,
             "tipo": caso.tipo},
        )
        self.repositorio.confirmar()
        return caso

    def detalle(self, id_caso, usuario):
        """Devuelve ``(caso, permiso)`` si el usuario tiene algún permiso (RF24)."""
        return self._caso(id_caso, usuario, NIVEL_LECTURA)

    def listar(self, usuario, filtros, pagina=1, por_pagina=20):
        """Casos accesibles, con búsqueda y filtros (RF26)."""
        filtros = dict(filtros)
        filtros["expediente"] = normalizar_texto(filtros.get("expediente"))
        filtros["busqueda_normalizada"] = normalizar_texto(filtros.get("busqueda"))
        return self.repositorio.buscar(usuario.id, filtros, pagina, por_pagina)

    def accesos(self, caso):
        """Accesos compartidos del caso."""
        return self.repositorio.accesos(caso.id)

    def resumen(self, usuario):
        """Cantidad de casos accesibles por estado."""
        return self.repositorio.cantidad_por_estado(usuario.id)

    # --- Editar y estados (RF25, RF27 a RF29) ---

    def editar(self, id_caso, usuario, cambios):
        """Modifica los datos del caso (RF25). Responsable o Colaborador; no en solo lectura."""
        accion = auditoria.CASO_EDICION
        caso, _ = self._caso(id_caso, usuario, NIVEL_COLABORACION, accion)
        if caso.estado not in ESTADOS_EDITABLES:
            self._rechazar(
                ConflictoDatos(
                    "El caso está cerrado o archivado y es de solo lectura. "
                    "Reabrilo para editarlo.",
                    codigo="caso_solo_lectura",
                ),
                accion, usuario, caso, "solo_lectura",
            )
        if cambios.get("fecha_hecho") is not None:
            self._validar_fecha(cambios["fecha_hecho"])
        modificados = {}
        for campo in CAMPOS_EDITABLES:
            if campo not in cambios:
                continue
            nuevo = cambios[campo]
            if campo in ("expediente", "descripcion"):
                nuevo = nuevo or None
            elif nuevo is None:
                continue
            anterior = getattr(caso, campo)
            if nuevo != anterior:
                modificados[campo] = {"anterior": _texto(anterior), "nuevo": _texto(nuevo)}
                setattr(caso, campo, nuevo)
        if modificados:
            caso.expediente_normalizado = normalizar_texto(caso.expediente)
            self._tocar(caso)
            self._auditar(accion, auditoria.EXITOSO, usuario, caso, {"cambios": modificados})
            self.repositorio.confirmar()
        return caso

    def cambiar_estado(self, id_caso, usuario, operacion):
        """Cierra, archiva, desarchiva o reabre el caso (RF27 a RF29, RN18). Solo el Responsable."""
        accion = auditoria.CASO_CAMBIO_ESTADO
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        anterior = caso.estado
        if operacion == "cerrar" and anterior == ESTADO_EN_ANALISIS:
            self._rechazar(
                ConflictoDatos(
                    "El caso tiene un análisis en curso: vas a poder cerrarlo cuando termine.",
                    codigo="caso_en_analisis",
                ),
                accion, usuario, caso, "en_analisis",
            )
        transiciones = {
            ("cerrar", ESTADO_BORRADOR): ESTADO_CERRADO,
            ("cerrar", ESTADO_ANALIZADO): ESTADO_CERRADO,
            ("archivar", ESTADO_CERRADO): ESTADO_ARCHIVADO,
            ("desarchivar", ESTADO_ARCHIVADO): ESTADO_CERRADO,
            ("reabrir", ESTADO_CERRADO): None,
            ("reabrir", ESTADO_ARCHIVADO): None,
        }
        if (operacion, anterior) not in transiciones:
            self._rechazar(
                ConflictoDatos(
                    "Esa operación no está permitida en el estado actual del caso.",
                    codigo="transicion_invalida",
                ),
                accion, usuario, caso, f"{operacion}_desde_{anterior}",
            )
        nuevo = transiciones[(operacion, anterior)]
        if operacion == "cerrar":
            caso.retencion_desde = ahora_utc()
        elif operacion == "reabrir":
            nuevo = ESTADO_ANALIZADO if caso.tiene_informes else ESTADO_BORRADOR
            caso.retencion_desde = None
        caso.estado = nuevo
        self._tocar(caso)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"operacion": operacion, "anterior": anterior, "nuevo": nuevo},
        )
        self.repositorio.confirmar()
        return caso

    # --- Compartir (RF30, RF31) ---

    def _exigir_organizacion(self, caso, usuario, accion):
        if caso.es_personal:
            self._rechazar(
                ConflictoDatos(
                    "Los casos del espacio personal no se comparten. Para trabajar en equipo, "
                    "creá el caso en una organización.",
                    codigo="caso_personal",
                ),
                accion, usuario, caso, "caso_personal",
            )

    def _miembros_a_avisar(self, caso, acceso):
        """Destinatarios de un acceso: el miembro o toda la organización, sin el Responsable."""
        if acceso.toda_organizacion:
            return [
                m.usuario for m in self.organizaciones.miembros(caso.id_organizacion)
                if m.id_usuario != caso.id_responsable
            ]
        return [acceso.usuario]

    def compartir(self, id_caso, usuario, nivel, id_usuario=None):
        """Comparte el caso con un miembro o, sin ``id_usuario``, con toda la organización (RF30).

        Si el destinatario ya tenía un acceso, se actualiza su nivel.
        """
        accion = auditoria.CASO_COMPARTIR
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        self._exigir_organizacion(caso, usuario, accion)
        if id_usuario is None:
            acceso = self.repositorio.acceso_de_organizacion(caso.id)
            if acceso is None:
                acceso = AccesoCaso(caso=caso, toda_organizacion=True, nivel=nivel)
        else:
            if id_usuario == caso.id_responsable:
                mensaje = "Sos el Responsable: ya tenés todos los permisos sobre el caso."
                raise ErrorValidacion(mensaje, {"id_usuario": mensaje})
            if self.organizaciones.membresia(caso.id_organizacion, id_usuario) is None:
                mensaje = "Solo podés compartir el caso con miembros de su organización."
                self._rechazar(
                    ErrorValidacion(mensaje, {"id_usuario": mensaje}),
                    accion, usuario, caso, "no_es_miembro",
                )
            acceso = self.repositorio.acceso_individual(caso.id, id_usuario)
            if acceso is None:
                acceso = AccesoCaso(caso=caso, id_usuario=id_usuario, nivel=nivel)
        acceso.nivel = nivel
        self.repositorio.preparar(acceso)
        self._tocar(caso)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"id_usuario": id_usuario, "toda_organizacion": id_usuario is None, "nivel": nivel},
        )
        self.repositorio.confirmar()
        for destinatario in self._miembros_a_avisar(caso, acceso):
            self.correos.enviar_aviso_acceso_caso(destinatario, caso, "otorgado", nivel)
        return acceso

    def _acceso_de(self, caso, id_acceso):
        acceso = self.repositorio.acceso_por_id(id_acceso)
        if acceso is None or acceso.id_caso != caso.id:
            raise NoEncontrado("El acceso no existe.")
        return acceso

    def modificar_acceso(self, id_caso, usuario, id_acceso, nivel):
        """Cambia el nivel de un acceso; vale desde la siguiente solicitud (RF31 CA2)."""
        accion = auditoria.CASO_ACCESO_MODIFICACION
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        acceso = self._acceso_de(caso, id_acceso)
        anterior = acceso.nivel
        acceso.nivel = nivel
        self._tocar(caso)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"id_acceso": acceso.id, "nivel": {"anterior": anterior, "nuevo": nivel}},
        )
        self.repositorio.confirmar()
        for destinatario in self._miembros_a_avisar(caso, acceso):
            self.correos.enviar_aviso_acceso_caso(destinatario, caso, "modificado", nivel)
        return acceso

    def revocar_acceso(self, id_caso, usuario, id_acceso):
        """Quita un acceso; el usuario lo pierde de inmediato (RF31 CA1)."""
        accion = auditoria.CASO_ACCESO_REVOCACION
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        acceso = self._acceso_de(caso, id_acceso)
        afectados = self._miembros_a_avisar(caso, acceso)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"id_usuario": acceso.id_usuario, "toda_organizacion": acceso.toda_organizacion},
        )
        self.repositorio.quitar(acceso)
        self._tocar(caso)
        self.repositorio.confirmar()
        for destinatario in afectados:
            self.correos.enviar_aviso_acceso_caso(destinatario, caso, "revocado", None)

    # --- Transferir (RF33) ---

    def transferir(self, id_caso, usuario, destino, conservar_colaboracion=True):
        """Transfiere la responsabilidad del caso (RF33).

        Args:
            destino: en un caso de organización, el id del miembro; en un caso
                personal, el correo de otro usuario registrado, que debe aceptarla.

        Returns:
            True si la transferencia quedó aplicada; False si espera la aceptación.
        """
        accion = auditoria.CASO_TRANSFERENCIA
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        if caso.estado == ESTADO_EN_ANALISIS:
            raise ConflictoDatos("El caso tiene un análisis en curso.", codigo="caso_en_analisis")
        if caso.es_personal:
            self._solicitar_transferencia(caso, usuario, destino)
            return False
        try:
            id_destino = int(destino)
        except (TypeError, ValueError) as error:
            raise ErrorValidacion(
                "Elegí un miembro de la organización.", {"destino": "Elegí un miembro."}
            ) from error
        if id_destino == usuario.id or self.organizaciones.membresia(
            caso.id_organizacion, id_destino
        ) is None:
            mensaje = "Elegí otro miembro de la organización del caso."
            self._rechazar(
                ErrorValidacion(mensaje, {"destino": mensaje}), accion, usuario, caso,
                "destino_invalido",
            )
        nuevo = self.usuarios.obtener_por_id(id_destino)
        self._asignar_responsable(caso, nuevo, conservar_colaboracion)
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"anterior": usuario.id, "nuevo": nuevo.id,
             "conserva_colaboracion": conservar_colaboracion},
        )
        self.repositorio.confirmar()
        self.correos.enviar_aviso_transferencia_caso(nuevo, caso, True, usuario)
        self.correos.enviar_aviso_transferencia_caso(usuario, caso, False, nuevo)
        return True

    def _asignar_responsable(self, caso, nuevo, conservar_colaboracion):
        """Cambia el Responsable; el anterior puede conservar Colaboración (RF33 CA1)."""
        anterior = caso.id_responsable
        propio = self.repositorio.acceso_individual(caso.id, nuevo.id)
        if propio is not None:
            self.repositorio.quitar(propio)
        caso.id_responsable = nuevo.id
        if conservar_colaboracion and not caso.es_personal:
            acceso = self.repositorio.acceso_individual(caso.id, anterior)
            if acceso is None:
                self.repositorio.preparar(
                    AccesoCaso(caso=caso, id_usuario=anterior, nivel=NIVEL_COLABORACION)
                )
            else:
                acceso.nivel = NIVEL_COLABORACION
        self._tocar(caso)

    def _solicitar_transferencia(self, caso, usuario, correo):
        """Pide a otro usuario que acepte un caso personal (RF33 CA2)."""
        accion = auditoria.CASO_TRANSFERENCIA
        destinatario = self.usuarios.obtener_por_correo(str(correo or ""))
        if (
            destinatario is None or not destinatario.verificado or not destinatario.activo
            or destinatario.id == usuario.id or destinatario.perfil == PERFIL_ASEGURADORA
        ):
            mensaje = (
                "Indicá el correo de otra persona registrada con perfil Abogado: los casos "
                "personales solo pueden pasar al espacio personal de un abogado."
            )
            self._rechazar(
                ErrorValidacion(mensaje, {"destino": mensaje}), accion, usuario, caso,
                "destino_invalido",
            )
        caso.transferencia_a = destinatario.id
        caso.transferencia_en = ahora_utc()
        self._auditar(
            accion, auditoria.EXITOSO, usuario, caso,
            {"solicitud": True, "destinatario": destinatario.id},
        )
        self.repositorio.confirmar()
        self.correos.enviar_solicitud_transferencia_caso(destinatario, caso, usuario)

    def transferencias_pendientes(self, usuario):
        """Casos personales que esperan que el usuario acepte su transferencia."""
        return self.repositorio.transferencias_para(usuario.id)

    def responder_transferencia(self, id_caso, usuario, aceptar):
        """Acepta o rechaza la transferencia de un caso personal (RF33 CA2)."""
        caso = self.repositorio.obtener(id_caso)
        if caso is None or caso.transferencia_a != usuario.id:
            raise NoEncontrado("No hay una transferencia pendiente de ese caso para vos.")
        anterior = caso.responsable
        caso.transferencia_a = None
        caso.transferencia_en = None
        if aceptar:
            caso.id_responsable = usuario.id
            self._tocar(caso)
        self._auditar(
            auditoria.CASO_TRANSFERENCIA, auditoria.EXITOSO, usuario, caso,
            {"respuesta": "aceptada" if aceptar else "rechazada", "anterior": anterior.id},
        )
        self.repositorio.confirmar()
        self.correos.enviar_respuesta_transferencia_caso(anterior, caso, usuario, aceptar)
        return caso

    def cancelar_transferencia(self, id_caso, usuario):
        """El Responsable retira una transferencia que todavía no fue aceptada."""
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, auditoria.CASO_TRANSFERENCIA)
        if caso.transferencia_a is None:
            raise NoEncontrado("El caso no tiene una transferencia pendiente.")
        caso.transferencia_a = None
        caso.transferencia_en = None
        self._auditar(
            auditoria.CASO_TRANSFERENCIA, auditoria.EXITOSO, usuario, caso, {"cancelada": True}
        )
        self.repositorio.confirmar()

    # --- Eliminar (RF32) ---

    def _con_acceso(self, caso):
        """Usuarios con acceso al caso, sin el Responsable, para avisarles."""
        if caso.es_personal:
            return []
        if self.repositorio.acceso_de_organizacion(caso.id) is not None:
            return [
                m.usuario for m in self.organizaciones.miembros(caso.id_organizacion)
                if m.id_usuario != caso.id_responsable
            ]
        return [a.usuario for a in self.repositorio.accesos(caso.id) if a.usuario is not None]

    def eliminar(self, id_caso, usuario, confirmacion):
        """Elimina el caso de forma definitiva escribiendo su número (RF32, RN21).

        La auditoría conserva la constancia y las huellas de las imágenes, cuyos
        archivos se borran del almacenamiento después de confirmar.
        """
        accion = auditoria.CASO_ELIMINACION
        caso, _ = self._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        if caso.estado == ESTADO_EN_ANALISIS:
            self._rechazar(
                ConflictoDatos(
                    "El caso tiene un análisis en curso: vas a poder eliminarlo cuando termine.",
                    codigo="caso_en_analisis",
                ),
                accion, usuario, caso, "en_analisis",
            )
        if (confirmacion or "").strip().upper() != caso.numero:
            mensaje = "Escribí el número exacto del caso para confirmar."
            self._rechazar(
                ErrorValidacion(mensaje, {"confirmacion": mensaje}), accion, usuario, caso,
                "confirmacion_incorrecta",
            )
        avisar = self._con_acceso(caso)
        numero = caso.numero
        huellas = self.archivos.preparar([caso]) if self.archivos else []
        self._auditar(accion, auditoria.EXITOSO, usuario, caso, {"sha256_eliminados": huellas})
        self.repositorio.quitar(caso)
        self.repositorio.confirmar()
        if self.archivos:
            self.archivos.borrar_pendientes()
        for destinatario in avisar:
            self.correos.enviar_aviso_caso_eliminado(destinatario, numero, usuario)


class TareasDeRetencion:
    """Prórroga y tarea diaria de retención de los casos (funcionalidad 015).

    Se separa de ``ServicioCasos`` para que la tarea programada no necesite una
    sesión de usuario: la ejecuta el sistema y la auditoría la registra sin
    usuario.

    Realiza: RF49 (CA1, CA2), RF50 (CA1), RF51 (CA1, CA2); RN30 a RN33.
    """

    def __init__(self, casos):
        """
        Args:
            casos: ``ServicioCasos``, del que se reutilizan el repositorio, los
                permisos, los correos, los archivos y la auditoría.
        """
        self.casos = casos

    def prorrogar(self, id_caso, usuario, motivo):
        """Extiende 1 año la destrucción de un caso cerrado o archivado (RF51). Solo el Responsable.

        La prórroga corre el inicio del plazo un año: así la fecha de
        destrucción se extiende 1 año sin agregar columnas.

        Raises:
            ErrorValidacion: sin motivo.
            ConflictoDatos: si el caso no está cerrado ni archivado.
        """
        # pylint: disable=protected-access
        accion = auditoria.CASO_PRORROGA_RETENCION
        caso, _ = self.casos._caso(id_caso, usuario, PERMISO_RESPONSABLE, accion)
        if caso.estado not in ESTADOS_CON_RETENCION or caso.retencion_desde is None:
            self.casos._rechazar(ConflictoDatos(
                "Solo se puede prorrogar un caso cerrado o archivado.", codigo="sin_retencion",
            ), accion, usuario, caso, "estado")
        motivo = (motivo or "").strip()
        if not motivo:
            mensaje = "Indicá el motivo de la prórroga, por ejemplo, un juicio en trámite."
            self.casos._rechazar(
                ErrorValidacion(mensaje, {"motivo": mensaje}), accion, usuario, caso, "sin_motivo"
            )
        anterior = vencimiento_de_retencion(caso)
        caso.retencion_desde = sumar_un_anio(caso.retencion_desde)
        nuevo = vencimiento_de_retencion(caso)
        self.casos._auditar(accion, auditoria.EXITOSO, usuario, caso, {
            "motivo": motivo, "vencia": anterior.isoformat(), "vence": nuevo.isoformat(),
        })
        self.casos.repositorio.confirmar()
        return caso, nuevo

    def procesar(self, ahora=None):
        """Tarea diaria: avisa a 30 días y destruye los casos vencidos (RF49, RF50).

        El aviso se envía el día en que faltan exactamente 30 días, así una
        tarea diaria lo manda una sola vez. La destrucción aplica RN21: se
        audita con el número y las huellas de los archivos y después se borran.

        Returns:
            Diccionario con las cantidades de ``avisados`` y ``destruidos``.
        """
        # pylint: disable=protected-access
        ahora = ahora or ahora_utc()
        dia_del_aviso = (ahora + timedelta(days=DIAS_AVISO_RETENCION)).date()
        avisados = destruidos = 0
        for caso in self.casos.repositorio.con_retencion():
            if caso.estado not in ESTADOS_CON_RETENCION:
                continue
            vence = vencimiento_de_retencion(caso)
            if vence <= ahora:
                huellas = self.casos.archivos.preparar([caso]) if self.casos.archivos else []
                self.casos._auditar(
                    auditoria.CASO_DESTRUCCION_RETENCION, auditoria.EXITOSO, None, caso,
                    {"sha256_eliminados": huellas, "vencio": vence.isoformat()},
                )
                self.casos.repositorio.quitar(caso)
                self.casos.repositorio.confirmar()
                if self.casos.archivos:
                    self.casos.archivos.borrar_pendientes()
                destruidos += 1
            elif vence.date() == dia_del_aviso and caso.responsable is not None:
                self.casos.correos.enviar_aviso_retencion(caso.responsable, caso, vence)
                self.casos._auditar(
                    auditoria.CASO_AVISO_RETENCION, auditoria.EXITOSO, None, caso,
                    {"vence": vence.isoformat()}, confirmar=True,
                )
                avisados += 1
        return {"avisados": avisados, "destruidos": destruidos}


def _texto(valor):
    """Representación para la auditoría (las fechas se guardan como texto ISO)."""
    return valor.isoformat() if isinstance(valor, date) else valor
