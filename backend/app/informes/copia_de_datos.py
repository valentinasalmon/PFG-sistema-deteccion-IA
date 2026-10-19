"""Copia de los datos personales de una cuenta, en JSON y en PDF.

Recibe los objetos del modelo que ya reunió el servicio y arma un documento
que solo contiene datos de la persona: no incluye datos de otras personas ni
el contenido de los casos, que puede referirse a terceros (RF09 CA3).

Realiza: RF09 (CA1, CA3); RNF08 (CA4: derecho de acceso, Ley N.° 25.326, art. 14).
"""
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.esquemas.casos import NOMBRES_ESTADO
from app.esquemas.casos import NOMBRES_TIPO as NOMBRES_TIPO_CASO
from app.esquemas.organizaciones import NOMBRES_TIPO as NOMBRES_TIPO_ORGANIZACION

DIRECTORIO_PLANTILLAS = Path(__file__).resolve().parents[1] / "plantillas" / "informes"

NOMBRES_PERFIL = {"abogado": "Abogado", "aseguradora": "Aseguradora"}
NOMBRES_ROL_CUENTA = {"usuario": "Usuario", "administrador": "Administrador"}
NOMBRES_ROL_ORGANIZACION = {"referente": "Referente", "miembro": "Miembro"}

_entorno = Environment(
    loader=FileSystemLoader(DIRECTORIO_PLANTILLAS),
    autoescape=select_autoescape(["html"]),
)


def _fecha(valor):
    """Fecha y hora en ISO 8601 (UTC), o None."""
    return valor.isoformat() if valor else None


def _formatear(valor):
    """Fecha ISO como ``dd/mm/aaaa hh:mm`` para el PDF; las fechas sin hora, ``dd/mm/aaaa``."""
    if not valor:
        return "—"
    fecha, _, hora = valor.partition("T")
    anio, mes, dia = fecha.split("-")
    return f"{dia}/{mes}/{anio} {hora[:5]}".strip()


_entorno.filters["fecha"] = _formatear


def armar_copia(datos):
    """Arma el documento con los datos de la persona.

    Args:
        datos: diccionario con ``usuario``, ``membresias``, ``invitaciones``,
            ``casos``, ``actividad`` y ``generada_en``.

    Returns:
        Diccionario listo para serializar en JSON.
    """
    usuario = datos["usuario"]
    return {
        "generada_en": _fecha(datos["generada_en"]),
        "cuenta": {
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo,
            "perfil": NOMBRES_PERFIL[usuario.perfil],
            "colegio": usuario.colegio,
            "empresa": usuario.empresa,
            "rol": NOMBRES_ROL_CUENTA.get(usuario.rol, usuario.rol),
            "activa": usuario.activo,
            "creada_en": _fecha(usuario.creado_en),
            "correo_verificado_en": _fecha(usuario.correo_verificado_en),
        },
        "consentimiento": {
            "version_terminos": usuario.version_terminos,
            "aceptado_en": _fecha(usuario.aceptacion_terminos_en),
        },
        "organizaciones": [
            {
                "nombre": membresia.organizacion.nombre,
                "tipo": NOMBRES_TIPO_ORGANIZACION[membresia.organizacion.tipo],
                "rol": NOMBRES_ROL_ORGANIZACION[membresia.rol],
                "cargo": membresia.cargo,
                "incorporado_en": _fecha(membresia.incorporado_en),
            }
            for membresia in datos["membresias"]
        ],
        "invitaciones_pendientes": [
            {
                "organizacion": invitacion.organizacion.nombre,
                "cargo": invitacion.cargo,
                "recibida_en": _fecha(invitacion.creada_en),
                "vence_en": _fecha(invitacion.vence_en),
            }
            for invitacion in datos["invitaciones"]
        ],
        "casos_a_cargo": [
            {
                "numero": caso.numero,
                "tipo": NOMBRES_TIPO_CASO[caso.tipo],
                "estado": NOMBRES_ESTADO[caso.estado],
                "espacio": "Personal" if caso.es_personal else caso.organizacion.nombre,
                "fecha_hecho": caso.fecha_hecho.isoformat(),
                "creado_en": _fecha(caso.creado_en),
            }
            for caso in datos["casos"]
        ],
        "actividad": [
            {
                "fecha": _fecha(entrada.fecha),
                "accion": entrada.accion,
                "resultado": entrada.resultado,
                "ip": entrada.ip,
            }
            for entrada in datos["actividad"]
        ],
    }


def a_json(copia):
    """La copia como JSON legible (UTF-8, con sangría)."""
    return json.dumps(copia, ensure_ascii=False, indent=2).encode("utf-8")


def a_pdf(copia):
    """La copia como PDF, generado con WeasyPrint a partir de una plantilla HTML."""
    # Se importa aquí: WeasyPrint tarda en cargar y solo hace falta al pedir el PDF.
    from weasyprint import HTML  # pylint: disable=import-outside-toplevel

    html = _entorno.get_template("copia_de_datos.html").render(copia=copia)
    return HTML(string=html).write_pdf()
