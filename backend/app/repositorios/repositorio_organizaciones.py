"""Acceso a organizaciones, membresías e invitaciones (patrón Repository).

Realiza: RF10 a RF18.
"""
from app.extensiones import db
from app.modelos.organizacion import (
    INVITACION_PENDIENTE,
    Invitacion,
    Membresia,
    Organizacion,
)
from app.modelos.usuario import Usuario


class RepositorioOrganizaciones:
    """Consultas y persistencia de las organizaciones y sus miembros."""

    def obtener(self, id_organizacion):
        """Devuelve la organización, o None."""
        return db.session.get(Organizacion, id_organizacion)

    def membresia(self, id_organizacion, id_usuario):
        """Devuelve la membresía del usuario en la organización, o None."""
        return Membresia.query.filter_by(
            id_organizacion=id_organizacion, id_usuario=id_usuario
        ).first()

    def membresias_de_usuario(self, id_usuario):
        """Membresías del usuario, con su organización, ordenadas por nombre."""
        return (
            Membresia.query.join(Organizacion)
            .filter(Membresia.id_usuario == id_usuario)
            .order_by(Organizacion.nombre, Organizacion.id)
            .all()
        )

    def miembros(self, id_organizacion):
        """Membresías de la organización: primero el Referente, luego por apellido."""
        return (
            Membresia.query.join(Usuario)
            .filter(Membresia.id_organizacion == id_organizacion)
            .order_by(Membresia.rol.desc(), Usuario.apellido, Usuario.nombre)
            .all()
        )

    def referente(self, id_organizacion):
        """Membresía del Referente de la organización."""
        return Membresia.query.filter_by(id_organizacion=id_organizacion, rol="referente").first()

    def cantidad_de_miembros(self, id_organizacion):
        """Cantidad de miembros de la organización."""
        return Membresia.query.filter_by(id_organizacion=id_organizacion).count()

    def es_miembro_por_correo(self, id_organizacion, correo):
        """True si el correo pertenece a un miembro de la organización."""
        return (
            Membresia.query.join(Usuario)
            .filter(Membresia.id_organizacion == id_organizacion, Usuario.correo == correo)
            .first()
            is not None
        )

    def invitacion(self, id_invitacion):
        """Devuelve la invitación, o None."""
        return db.session.get(Invitacion, id_invitacion)

    def invitaciones_pendientes(self, id_organizacion):
        """Invitaciones pendientes de la organización (vigentes o vencidas)."""
        return (
            Invitacion.query.filter_by(id_organizacion=id_organizacion, estado=INVITACION_PENDIENTE)
            .order_by(Invitacion.creada_en)
            .all()
        )

    def invitacion_pendiente(self, id_organizacion, correo):
        """Invitación pendiente al correo en la organización, o None."""
        return Invitacion.query.filter_by(
            id_organizacion=id_organizacion, correo=correo, estado=INVITACION_PENDIENTE
        ).first()

    def invitaciones_pendientes_de_correo(self, correo, momento):
        """Invitaciones pendientes y vigentes dirigidas a un correo."""
        return (
            Invitacion.query.filter(
                Invitacion.correo == correo,
                Invitacion.estado == INVITACION_PENDIENTE,
                Invitacion.vence_en > momento,
            )
            .order_by(Invitacion.creada_en)
            .all()
        )

    def cantidad_de_invitaciones_vigentes(self, id_organizacion, momento):
        """Invitaciones pendientes y no vencidas: cuentan para el límite del plan."""
        return Invitacion.query.filter(
            Invitacion.id_organizacion == id_organizacion,
            Invitacion.estado == INVITACION_PENDIENTE,
            Invitacion.vence_en > momento,
        ).count()

    def preparar(self, entidad):
        """Agrega la entidad a la transacción y le asigna identificador, sin confirmar."""
        db.session.add(entidad)
        db.session.flush()
        return entidad

    def quitar(self, entidad):
        """Marca la entidad para eliminarla al confirmar."""
        db.session.delete(entidad)

    def confirmar(self):
        """Confirma la transacción en curso (la acción y su entrada de auditoría)."""
        db.session.commit()
