"""Consultas agregadas para el tablero y los listados del Administrador (funcionalidad 014).

Solo devuelve cantidades y datos de cuentas y organizaciones: nunca casos,
imágenes ni informes identificables (RF21 CA2, RF22 CA2). Las series por mes
se agrupan en Python para funcionar igual en PostgreSQL y en SQLite.

Realiza: RF21, RF22.
"""
from collections import Counter

from sqlalchemy import func, or_

from app.extensiones import db
from app.modelos.analisis import Analisis
from app.modelos.caso import Caso
from app.modelos.organizacion import Membresia, Organizacion
from app.modelos.usuario import Usuario


def _por_mes(fechas):
    """Cantidad por mes (``AAAA-MM``), ordenada."""
    return dict(sorted(Counter(f.strftime("%Y-%m") for f in fechas).items()))


def _en_rango(columna, desde, hasta):
    condiciones = []
    if desde is not None:
        condiciones.append(columna >= desde)
    if hasta is not None:
        condiciones.append(columna < hasta)
    return condiciones


class RepositorioEstadisticas:
    """Indicadores agregados de la plataforma."""

    def contar_por(self, columna):
        """Cantidad de filas por cada valor de la columna."""
        return dict(db.session.query(columna, func.count()).group_by(columna).all())

    def usuarios_por_perfil(self):
        """Cuentas verificadas por perfil."""
        return dict(
            db.session.query(Usuario.perfil, func.count(Usuario.id))
            .filter(Usuario.correo_verificado_en.isnot(None))
            .group_by(Usuario.perfil).all()
        )

    def organizaciones_por(self, columna):
        """Organizaciones por tipo o por plan."""
        return self.contar_por(columna)

    def casos_por(self, columna):
        """Casos por estado o por tipo."""
        return self.contar_por(columna)

    def analisis_por_mes(self, desde, hasta):
        """Análisis pedidos en el rango, por mes."""
        fechas = db.session.query(Analisis.creado_en).filter(
            *_en_rango(Analisis.creado_en, desde, hasta)
        )
        return _por_mes(f for (f,) in fechas)

    def altas_por_mes(self, desde, hasta):
        """Cuentas creadas en el rango, por mes."""
        fechas = db.session.query(Usuario.creado_en).filter(
            *_en_rango(Usuario.creado_en, desde, hasta)
        )
        return _por_mes(f for (f,) in fechas)

    def usuarios(self, busqueda, perfil, pagina, por_pagina):
        """Cuentas para el listado, con búsqueda por nombre o correo (RF22)."""
        consulta = Usuario.query
        if busqueda:
            patron = f"%{busqueda.lower()}%"
            consulta = consulta.filter(or_(
                func.lower(Usuario.correo).like(patron),
                func.lower(Usuario.nombre + " " + Usuario.apellido).like(patron),
            ))
        if perfil:
            consulta = consulta.filter(Usuario.perfil == perfil)
        total = consulta.count()
        filas = (
            consulta.order_by(Usuario.creado_en.desc())
            .offset((pagina - 1) * por_pagina).limit(por_pagina).all()
        )
        return filas, total

    def organizaciones(self, busqueda, tipo, pagina, por_pagina):
        """Organizaciones con su cantidad de miembros para el listado (RF22)."""
        miembros = func.count(Membresia.id_usuario)
        consulta = (
            db.session.query(Organizacion, miembros)
            .outerjoin(Membresia, Membresia.id_organizacion == Organizacion.id)
            .group_by(Organizacion.id)
        )
        if busqueda:
            patron = f"%{busqueda.lower()}%"
            consulta = consulta.filter(func.lower(Organizacion.nombre).like(patron))
        if tipo:
            consulta = consulta.filter(Organizacion.tipo == tipo)
        total = consulta.count()
        filas = (
            consulta.order_by(Organizacion.nombre)
            .offset((pagina - 1) * por_pagina).limit(por_pagina).all()
        )
        return filas, total

    def analisis_del_espacio_desde(self, id_organizacion, id_responsable, desde):
        """Análisis pedidos desde una fecha en un espacio de trabajo (RF19 CA2).

        El espacio personal se identifica por su Responsable; el de una
        organización, por la organización.
        """
        consulta = db.session.query(func.count(Analisis.id)).join(Caso, Caso.id == Analisis.id_caso)
        if id_organizacion is not None:
            consulta = consulta.filter(Caso.id_organizacion == id_organizacion)
        else:
            consulta = consulta.filter(
                Caso.id_organizacion.is_(None), Caso.id_responsable == id_responsable
            )
        return consulta.filter(Analisis.creado_en >= desde).scalar()
