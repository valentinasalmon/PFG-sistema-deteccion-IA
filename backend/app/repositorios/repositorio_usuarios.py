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

    def guardar(self, usuario):
        """Inserta o actualiza el usuario y confirma la transacción."""
        db.session.add(usuario)
        db.session.commit()
        return usuario
