"""Derechos sobre los datos personales: copia (acceso) y eliminación de la cuenta (supresión).

La copia se arma al momento y no se guarda: el enlace firmado vence a los
15 minutos y además exige la sesión de la misma persona.

La eliminación exige antes que la persona resuelva sus casos y sus
organizaciones, para no dejar casos sin Responsable ni organizaciones sin
Referente. Todo se confirma en una sola transacción: o se elimina la cuenta
con todo lo que depende de ella, o no se elimina nada.

Realiza: RF08, RF09; RN05, RN08, RN09, RN34; RNF06 (CA5); RNF08 (CA4).
"""
from app.informes import copia_de_datos
from app.servicios import auditoria, contrasenias
from app.servicios.errores import ConflictoDatos, ErrorValidacion, TokenInvalido
from app.servicios.tokens import PROPOSITO_COPIA_DATOS
from app.utilidades.tiempo import ahora_utc

FORMATOS_COPIA = {
    "json": ("application/json", copia_de_datos.a_json),
    "pdf": ("application/pdf", copia_de_datos.a_pdf),
}


class ServicioDatosPersonales:
    """Copia de los datos personales y eliminación de la cuenta propia."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, repositorios, organizaciones, correos, tokens, configuracion, registro
    ):
        """
        Args:
            repositorios: diccionario con los repositorios ``usuarios``,
                ``organizaciones``, ``casos`` y ``auditoria``.
            organizaciones: ``ServicioOrganizaciones``, para eliminar las
                organizaciones de un solo miembro con las mismas reglas (RN09).
            registro: ``ServicioAuditoria`` donde se registra cada operación.
        """
        self.usuarios = repositorios["usuarios"]
        self.membresias = repositorios["organizaciones"]
        self.casos = repositorios["casos"]
        self.actividad = repositorios["auditoria"]
        self.organizaciones = organizaciones
        self.correos = correos
        self.tokens = tokens
        self.vigencia_copia = configuracion["VIGENCIA_COPIA_DATOS"]
        self.registro = registro

    # --- Copia de los datos personales (RF09) ---

    def solicitar_copia(self, usuario):
        """Genera el token de descarga de la copia y avisa por correo (RF09 CA1, CA2).

        Returns:
            ``(token, vence_en)``.
        """
        token = self.tokens.generar(PROPOSITO_COPIA_DATOS, {"id": usuario.id})
        vence_en = ahora_utc() + self.vigencia_copia
        self.registro.registrar(
            auditoria.CUENTA_COPIA_SOLICITUD, auditoria.EXITOSO, usuario=usuario,
            recurso=usuario, confirmar=True,
        )
        self.correos.enviar_aviso_copia_de_datos(usuario)
        return token, vence_en

    def descargar_copia(self, usuario, token, formato):
        """Devuelve la copia en el formato pedido si el token es vigente y de esta persona.

        Returns:
            ``(contenido, tipo_mime)``.

        Raises:
            TokenInvalido: si el token venció, fue alterado o es de otra cuenta
                (RF09 CA3; CA4 de la funcionalidad).
        """
        try:
            datos = self.tokens.leer(
                PROPOSITO_COPIA_DATOS, token, self.vigencia_copia
            )
            if datos.get("id") != usuario.id:
                raise TokenInvalido(
                    "El enlace no es válido. Generá una copia nueva.", "otra_cuenta"
                )
        except TokenInvalido as error:
            self.registro.registrar(
                auditoria.CUENTA_COPIA_DESCARGA, auditoria.FALLIDO, usuario=usuario,
                recurso=usuario, detalle={"motivo": error.motivo, "formato": formato},
                confirmar=True,
            )
            raise
        tipo_mime, convertir = FORMATOS_COPIA[formato]
        contenido = convertir(self._armar_copia(usuario))
        self.registro.registrar(
            auditoria.CUENTA_COPIA_DESCARGA, auditoria.EXITOSO, usuario=usuario,
            recurso=usuario, detalle={"formato": formato}, confirmar=True,
        )
        return contenido, tipo_mime

    def _armar_copia(self, usuario):
        """Reúne los datos de la persona y arma el documento (RF09 CA1, CA3)."""
        return copia_de_datos.armar_copia({
            "usuario": usuario,
            "membresias": self.membresias.membresias_de_usuario(usuario.id),
            "invitaciones": self.membresias.invitaciones_pendientes_de_correo(
                usuario.correo, ahora_utc()
            ),
            "casos": self.casos.casos_a_cargo(usuario.id),
            "actividad": self.actividad.de_usuario(usuario.id),
            "generada_en": ahora_utc(),
        })

    # --- Eliminación de la cuenta (RF08) ---

    def situacion_para_baja(self, usuario):
        """Qué tiene que resolver la persona antes de eliminar su cuenta (RF08 CA1, CA2).

        Returns:
            Diccionario con:
            - ``casos``: casos de los que es Responsable, salvo los de las
              organizaciones que se eliminan con la cuenta;
            - ``referente_de``: organizaciones en las que es Referente y hay
              otros miembros (tiene que designar a otro, RN08);
            - ``a_eliminar``: organizaciones en las que es el único miembro,
              que se eliminan con sus casos (RN08, RN09).
        """
        referente_de, a_eliminar = [], []
        for membresia in self.membresias.membresias_de_usuario(usuario.id):
            organizacion = membresia.organizacion
            if self.membresias.cantidad_de_miembros(organizacion.id) == 1:
                a_eliminar.append(organizacion)
            elif membresia.es_referente:
                referente_de.append(organizacion)
        excluidas = {organizacion.id for organizacion in a_eliminar}
        casos = [
            caso for caso in self.casos.casos_a_cargo(usuario.id)
            if caso.id_organizacion not in excluidas
        ]
        return {"casos": casos, "referente_de": referente_de, "a_eliminar": a_eliminar}

    def cantidad_de_casos(self, organizacion):
        """Cantidad de casos que se eliminan con la organización (CU06 2c)."""
        return self.organizaciones.cantidad_de_casos(organizacion)

    def eliminar_cuenta(self, usuario, contrasenia):
        """Elimina la cuenta con todo lo que depende de ella (RF08 CA3, CA4).

        Raises:
            ErrorValidacion: si la contraseña no es correcta (CA8).
            ConflictoDatos: si quedan casos u organizaciones por resolver
                (RN05, RN08; CA5, CA6).
        """
        if not contrasenias.verificar(contrasenia, usuario.hash_contrasenia):
            self.registro.registrar(
                auditoria.CUENTA_ELIMINACION, auditoria.FALLIDO, usuario=usuario,
                recurso=usuario, detalle={"motivo": "contrasenia_incorrecta"}, confirmar=True,
            )
            mensaje = "La contraseña no es correcta."
            raise ErrorValidacion(mensaje, {"contrasenia": mensaje})

        situacion = self.situacion_para_baja(usuario)
        if situacion["casos"] or situacion["referente_de"]:
            self.registro.registrar(
                auditoria.CUENTA_ELIMINACION, auditoria.RECHAZADO, usuario=usuario,
                recurso=usuario, confirmar=True,
                detalle={
                    "motivo": "pendientes_sin_resolver",
                    "casos": len(situacion["casos"]),
                    "organizaciones_sin_referente": len(situacion["referente_de"]),
                },
            )
            raise ConflictoDatos(
                "Antes de eliminar tu cuenta, transferí o eliminá tus casos y designá "
                "otro Referente en tus organizaciones.",
                codigo="baja_pendiente",
            )

        correo, nombre = usuario.correo, usuario.nombre
        eliminadas = [organizacion.nombre for organizacion in situacion["a_eliminar"]]
        for organizacion in situacion["a_eliminar"]:
            self.organizaciones.eliminar_por_baja(organizacion, usuario)
        self._quitar_dependencias(usuario)
        # La entrada se registra antes de eliminar la cuenta; al eliminarla,
        # la base deja la entrada sin usuario (RN34, RNF06 CA5).
        self.registro.registrar(
            auditoria.CUENTA_ELIMINACION, auditoria.EXITOSO, usuario=usuario, recurso=usuario,
            detalle={"organizaciones_eliminadas": len(eliminadas)},
        )
        self.usuarios.eliminar(usuario)
        self.casos.confirmar()
        self.correos.enviar_confirmacion_eliminacion_cuenta(correo, nombre, eliminadas)

    def _quitar_dependencias(self, usuario):
        """Quita membresías, accesos, invitaciones a su correo y transferencias pendientes.

        Las membresías y los accesos también se eliminarían en cascada en la
        base; se quitan explícitamente para que la sesión del ORM no conserve
        objetos que ya no existen.
        """
        for membresia in self.membresias.membresias_de_usuario(usuario.id):
            self.membresias.quitar(membresia)
        for acceso in self.casos.accesos_de_usuario(usuario.id):
            self.casos.quitar(acceso)
        for invitacion in self.membresias.invitaciones_de_correo(usuario.correo):
            self.membresias.quitar(invitacion)
        for caso in self.casos.transferencias_para(usuario.id):
            caso.transferencia_a = None
            caso.transferencia_en = None
