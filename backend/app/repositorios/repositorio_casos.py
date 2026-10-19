"""Acceso a casos y a sus accesos compartidos (patrón Repository).

Realiza: RF23 a RF33; RN12, RN13, RN20; RNF05 (los listados nunca incluyen
casos sin permiso).
"""
from sqlalchemy import exists, func, or_

from app.extensiones import db
from app.repositorios.base import RepositorioBase
from app.modelos.caso import ESTADO_ARCHIVADO, AccesoCaso, Caso
from app.modelos.organizacion import Membresia


class RepositorioCasos(RepositorioBase):
    """Consultas y persistencia de casos."""

    def obtener(self, id_caso):
        """Devuelve el caso, o None."""
        return db.session.get(Caso, id_caso)

    @staticmethod
    def _condicion_de_acceso(id_usuario):
        """Casos que el usuario puede ver: los suyos y los compartidos con él (RF26 CA4).

        Un acceso de un caso de organización solo vale si el usuario sigue
        siendo miembro de esa organización (RF30 CA2).
        """
        es_miembro = exists().where(
            Membresia.id_organizacion == Caso.id_organizacion,
            Membresia.id_usuario == id_usuario,
        )
        tiene_acceso = exists().where(
            AccesoCaso.id_caso == Caso.id,
            or_(AccesoCaso.id_usuario == id_usuario, AccesoCaso.toda_organizacion.is_(True)),
        )
        return or_(Caso.id_responsable == id_usuario, es_miembro & tiene_acceso)

    def buscar(self, id_usuario, filtros, pagina, por_pagina):
        """Casos accesibles con los filtros de RF26, por última actualización.

        Args:
            filtros: diccionario con ``numero``, ``expediente`` (ya normalizado),
                ``estado``, ``tipo``, ``espacio`` (``"personal"`` o el id de
                una organización), ``desde`` y ``hasta`` (fechas del hecho).

        Returns:
            ``(casos, total)``.
        """
        consulta = Caso.query.filter(self._condicion_de_acceso(id_usuario))
        if filtros.get("estado"):
            consulta = consulta.filter(Caso.estado == filtros["estado"])
        else:
            consulta = consulta.filter(Caso.estado != ESTADO_ARCHIVADO)
        if filtros.get("numero"):
            consulta = consulta.filter(Caso.numero.ilike(f"%{filtros['numero']}%"))
        if filtros.get("expediente"):
            consulta = consulta.filter(
                Caso.expediente_normalizado.like(f"%{filtros['expediente']}%")
            )
        if filtros.get("tipo"):
            consulta = consulta.filter(Caso.tipo == filtros["tipo"])
        if filtros.get("espacio") == "personal":
            consulta = consulta.filter(Caso.id_organizacion.is_(None))
        elif filtros.get("espacio"):
            consulta = consulta.filter(Caso.id_organizacion == int(filtros["espacio"]))
        if filtros.get("desde"):
            consulta = consulta.filter(Caso.fecha_hecho >= filtros["desde"])
        if filtros.get("hasta"):
            consulta = consulta.filter(Caso.fecha_hecho <= filtros["hasta"])
        total = consulta.count()
        casos = (
            consulta.order_by(Caso.actualizado_en.desc(), Caso.id.desc())
            .offset((pagina - 1) * por_pagina)
            .limit(por_pagina)
            .all()
        )
        return casos, total

    def accesos(self, id_caso):
        """Accesos compartidos del caso."""
        return AccesoCaso.query.filter_by(id_caso=id_caso).order_by(AccesoCaso.otorgado_en).all()

    def acceso_individual(self, id_caso, id_usuario):
        """Acceso del usuario al caso, o None."""
        return AccesoCaso.query.filter_by(id_caso=id_caso, id_usuario=id_usuario).first()

    def acceso_de_organizacion(self, id_caso):
        """Acceso de toda la organización al caso, o None."""
        return AccesoCaso.query.filter_by(id_caso=id_caso, toda_organizacion=True).first()

    def acceso_por_id(self, id_acceso):
        """Devuelve el acceso, o None."""
        return db.session.get(AccesoCaso, id_acceso)

    def casos_a_cargo_en(self, id_usuario, id_organizacion):
        """Casos de la organización de los que el usuario es Responsable (RN14)."""
        return Caso.query.filter_by(
            id_responsable=id_usuario, id_organizacion=id_organizacion
        ).all()

    def casos_a_cargo(self, id_usuario):
        """Todos los casos de los que el usuario es Responsable, por número (RF08 CA1)."""
        return Caso.query.filter_by(id_responsable=id_usuario).order_by(Caso.numero).all()

    def accesos_de_usuario(self, id_usuario):
        """Accesos individuales del usuario a casos de cualquier organización."""
        return AccesoCaso.query.filter_by(id_usuario=id_usuario).all()

    def cantidad_de_organizacion(self, id_organizacion):
        """Cantidad de casos de la organización (RF18 CA1)."""
        return Caso.query.filter_by(id_organizacion=id_organizacion).count()

    def casos_de_organizacion(self, id_organizacion):
        """Casos de la organización, para eliminarlos con ella (RN09)."""
        return Caso.query.filter_by(id_organizacion=id_organizacion).all()

    def accesos_en_organizacion(self, id_usuario, id_organizacion):
        """Accesos individuales del usuario a casos de la organización."""
        return (
            AccesoCaso.query.join(Caso)
            .filter(AccesoCaso.id_usuario == id_usuario, Caso.id_organizacion == id_organizacion)
            .all()
        )

    def transferencias_para(self, id_usuario):
        """Casos personales cuya transferencia espera que el usuario la acepte (RF33 CA2)."""
        return (
            Caso.query.filter_by(transferencia_a=id_usuario)
            .order_by(Caso.transferencia_en)
            .all()
        )

    def cantidad_por_estado(self, id_usuario):
        """Cantidad de casos accesibles por estado, para el inicio."""
        filas = (
            db.session.query(Caso.estado, func.count(Caso.id))
            .filter(self._condicion_de_acceso(id_usuario))
            .group_by(Caso.estado)
            .all()
        )
        return dict(filas)
