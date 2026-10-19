"""Informe PDF de un análisis: datos, textos explicativos y conversión a PDF.

Arma un documento sencillo y explicativo para personas sin formación
técnica: cada capa tiene un recuadro "¿Qué significa?" y el informe termina
con las limitaciones y la advertencia legal. Nunca emite un veredicto ni
combina las capas en un puntaje (RN27). No accede a la base de datos ni al
almacenamiento: recibe los objetos y las miniaturas ya leídas.

Realiza: RF44 (CA1, CA2), RNF07 (CA3), RNF23 (CA2); RN27, RN29.
"""
import base64

from app.esquemas.casos import NOMBRES_TIPO as NOMBRES_TIPO_CASO
from app.informes.plantillas import html_a_pdf, version_weasyprint

VERSION_PLANTILLA = "1.0"

TITULOS_CAPA = {
    "metadatos": "Capa 1 · Metadatos",
    "c2pa": "Capa 2 · Credenciales de contenido (C2PA)",
}

QUE_SIGNIFICA = {
    "metadatos": (
        "Las fotos y las imágenes guardan datos ocultos además de la imagen: el "
        "teléfono o la cámara que las tomó, la fecha, el programa con el que se "
        "editaron y, a veces, la ubicación. Esta capa revisa esos datos y busca "
        "señales de edición o de generación por inteligencia artificial, y también "
        "incoherencias, como una fecha de captura posterior a la carga. "
        "Las aplicaciones de mensajería y las redes sociales suelen borrar estos "
        "datos, por lo que su ausencia no indica por sí sola una manipulación, y "
        "quien quiera alterar una imagen también puede modificarlos."
    ),
    "c2pa": (
        "Algunas herramientas, como ChatGPT, Gemini o Adobe Firefly, y algunas cámaras "
        "agregan a la imagen unas credenciales de contenido: una declaración firmada "
        "digitalmente que dice quién la hizo, con qué herramienta, si la generó una "
        "inteligencia artificial y qué ediciones tuvo. Esta capa comprueba esa firma con "
        "la lista de confianza del consorcio C2PA, que reúne a los emisores reconocidos. "
        "Si la firma es confiable y declara inteligencia artificial, es el indicio más "
        "fuerte de la plataforma. Que una imagen no tenga credenciales es lo más habitual: "
        "muchas cámaras no las agregan y WhatsApp o una captura de pantalla las eliminan, "
        "por lo que su ausencia no indica que la imagen sea original."
    ),
}
QUE_SIGNIFICA_GENERICO = (
    "Esta capa busca señales técnicas de edición o de generación artificial. Su "
    "resultado debe leerse junto con las demás capas."
)

# Leyenda exigida en todas las páginas del informe (RNF23 CA2).
LEYENDA_PERICIAL = (
    "Este informe no constituye un dictamen pericial. Consulte a un profesional especializado."
)

ESCALA_DE_INDICIO = (
    "Cada capa expresa su resultado como un nivel de indicio de 0 % a 100 %. Un nivel "
    "alto significa que la capa encontró señales que suelen aparecer en imágenes "
    "editadas o generadas; un nivel bajo, que no las encontró. No expresa una "
    "probabilidad sobre el origen de la imagen, y los niveles de distintas capas no se "
    "suman ni se promedian: cada capa mira un aspecto distinto."
)

LIMITACIONES = (
    "Este informe presenta indicios técnicos obtenidos de forma automatizada. No "
    "constituye un dictamen pericial ni emite una conclusión sobre la autenticidad "
    "de las imágenes.",
    "La ausencia de indicios no garantiza que una imagen no haya sido modificada, y "
    "la presencia de indicios no prueba por sí sola una manipulación: hay "
    "procesamientos legítimos, como la compresión o el recorte, que dejan señales "
    "similares.",
    "Los metadatos pueden ser eliminados o alterados por aplicaciones de mensajería, "
    "redes sociales o por cualquier persona con las herramientas adecuadas.",
    "Las técnicas de generación de imágenes evolucionan constantemente; los métodos de "
    "detección pueden no reconocer generadores nuevos.",
    "Se recomienda que un perito especializado en informática forense evalúe estos "
    "resultados antes de utilizarlos en un proceso judicial o administrativo.",
)

NOMBRES_SEVERIDAD = {
    "directo": "Directo",
    "fuerte": "Fuerte",
    "moderado": "Moderado",
    "debil": "Débil",
    "neutro": "Informativo",
}
NOMBRES_PERFIL = {"abogado": "Abogado", "aseguradora": "Aseguradora"}


def _miniatura_como_dato(contenido):
    """Miniatura JPEG embebida en el HTML, así el PDF no depende de enlaces."""
    if not contenido:
        return None
    return "data:image/jpeg;base64," + base64.b64encode(contenido).decode("ascii")


def _solicitante(analisis):
    usuario = analisis.solicitante
    if usuario is None:
        return {"nombre": "Cuenta eliminada", "perfil": "—", "institucion": None}
    return {
        "nombre": f"{usuario.nombre} {usuario.apellido}",
        "perfil": NOMBRES_PERFIL.get(usuario.perfil, usuario.perfil),
        "institucion": usuario.colegio or usuario.empresa,
        "etiqueta_institucion": "Colegio de abogados" if usuario.colegio else "Empresa",
    }


def _resultado(resultado):
    return {
        "titulo": TITULOS_CAPA.get(resultado.capa, resultado.capa),
        "disponible": resultado.estado == "completado",
        "nivel": resultado.nivel,
        "conclusion": resultado.conclusion,
        "motivo": resultado.motivo,
        "version": resultado.version,
        "que_significa": QUE_SIGNIFICA.get(resultado.capa, QUE_SIGNIFICA_GENERICO),
        "anomalias": [
            {
                "severidad": NOMBRES_SEVERIDAD.get(a.severidad, a.severidad),
                "descripcion": a.descripcion,
            }
            for a in resultado.anomalias
        ],
        "tabla": (resultado.detalle or {}).get("tabla", []),
    }


def armar_datos(analisis, miniaturas, version_plataforma):
    """Datos del informe a partir del análisis.

    Args:
        miniaturas: diccionario ``id de AnalisisImagen -> bytes`` de cada vista reducida.
        version_plataforma: versión de la aplicación (RN29).
    """
    caso = analisis.caso
    return {
        "caso": {
            "numero": caso.numero,
            "expediente": caso.expediente,
            "tipo": NOMBRES_TIPO_CASO[caso.tipo],
            "fecha_hecho": caso.fecha_hecho,
            "lugar": caso.lugar,
            "espacio": "Personal" if caso.es_personal else caso.organizacion.nombre,
        },
        "solicitante": _solicitante(analisis),
        "analisis": {
            "id": analisis.id,
            "pedido_en": analisis.creado_en,
            "iniciado_en": analisis.iniciado_en,
        },
        "imagenes": [
            {
                "nombre": incluida.nombre,
                "huella": incluida.huella,
                "miniatura": _miniatura_como_dato(miniaturas.get(incluida.id)),
                "integridad": incluida.integridad,
                "resultados": [_resultado(r) for r in incluida.resultados],
            }
            for incluida in analisis.imagenes
        ],
        "versiones": {
            "Plataforma": version_plataforma,
            **{TITULOS_CAPA.get(c, c): v for c, v in (analisis.versiones or {}).items()},
            "Plantilla del informe": VERSION_PLANTILLA,
            "WeasyPrint (generación del PDF)": version_weasyprint(),
        },
        "escala": ESCALA_DE_INDICIO,
        "leyenda": LEYENDA_PERICIAL,
        "limitaciones": LIMITACIONES,
    }


def generar_pdf(datos, generado_en):
    """El informe como PDF (bytes)."""
    return html_a_pdf("informe_analisis.html", informe=datos, generado_en=generado_en)
