"""Acceso a datos de los usuarios (patrón Repository)."""
from app.extensiones import db
from app.modelos.usuario import Usuario


class RepositorioUsuarios:
    """Consultas y persistencia de ``Usuario``."""

    def obtener_por_id(self, id_usuario):
        """Devuelve el usuario con ese identificador, o None."""
        return db.session.get(Usuario, id_usuario)

    def obtener_por_correo(self, correo):
        """Devuelve el usuario con ese correo (sin distinguir mayúsculas), o None."""
        return Usuario.query.filter_by(correo=correo.strip().lower()).first()

    def existe_correo(self, correo):
        """True si el correo ya pertenece a alguna cuenta."""
        return self.obtener_por_correo(correo) is not None

    def preparar(self, usuario):
        """Agrega un usuario nuevo a la transacción y le asigna su identificador, sin confirmar.

        Permite registrar en la auditoría la creación de la cuenta con su
        identificador y confirmar ambas cosas juntas al llamar a ``guardar``.
        """
        db.session.add(usuario)
        db.session.flush()
        return usuario

    def guardar(self, usuario):
        """Inserta o actualiza el usuario y confirma la transacción."""
        db.session.add(usuario)
        db.session.commit()
        return usuario
