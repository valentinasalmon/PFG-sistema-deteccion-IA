"""Informe PDF de un análisis: datos, textos explicativos y conversión a PDF.

Versión breve y autosuficiente (funcionalidad 025), pensada para quien
analiza imágenes todos los días y necesita leer el informe en pocos minutos:

1. Caso y solicitud.
2. Evidencia y cadena de custodia: cada archivo con su huella, la
   verificación de integridad y el sello en Hedera, y una cronología breve.
3. Escala de lectura: la tabla de niveles de indicio.
4. Resultados por imagen: por cada capa, si su resultado es determinista o
   probabilístico, el nivel y lo que encontró en una o dos frases.
5. Resultados deterministas y probabilísticos: qué diferencia hay.
6. Qué hacer ahora, y al final el aviso de alcance y el descargo (ADR-0017).

El lenguaje cambia según el perfil de quien pidió el análisis (Abogado o
Aseguradora, RF54). Nunca emite veredictos (RN27).

No accede a la base de datos ni al almacenamiento: recibe los objetos y las
miniaturas ya leídas.

Realiza: RF44 (CA1, CA2), RF54, RNF07 (CA3), RNF23 (CA2); RN27, RN29.
"""
import base64
from pathlib import Path

from app.esquemas.casos import NOMBRES_TIPO as NOMBRES_TIPO_CASO
from app.informes.plantillas import html_a_pdf, version_weasyprint

VERSION_PLANTILLA = "2.0"

TITULOS_CAPA = {
    "metadatos": "Capa 1 · Metadatos",
    "c2pa": "Capa 2 · Credenciales de contenido (C2PA)",
    "ela": "Capa 3 · Niveles de error (ELA)",
}

QUE_SIGNIFICA_GENERICO = (
    "Esta capa busca señales técnicas de edición o de generación artificial. Su "
    "resultado debe leerse junto con las demás capas."
)

# Leyenda exigida en todas las páginas del informe (RNF23 CA2).
LEYENDA_PERICIAL = (
    "Este informe no constituye un dictamen pericial. Consulte a un profesional especializado."
)

# Descargo pedido en la entrevista del 02/10/2026: resultado parcial, automatizado
# y que no reemplaza el criterio de un perito (ADR-0017).
DESCARGO = (
    "Este resultado es parcial: lo produjo un sistema automatizado de análisis que "
    "incluye técnicas de inteligencia artificial. Es una herramienta auxiliar y no "
    "reemplaza el criterio de un perito o criminalista, que es quien debe evaluar la "
    "evidencia y tomar la decisión final."
)

# Bandas de la escala de lectura; coinciden con describir_intensidad() de las capas
# y con las que muestra la pantalla de resultados.
BANDAS_DE_INDICIO = (
    {"desde": 70, "nombre": "Indicios fuertes", "clase": "fuerte", "rango": "70 % a 100 %"},
    {"desde": 45, "nombre": "Indicios moderados", "clase": "moderado", "rango": "45 % a 69 %"},
    {"desde": 1, "nombre": "Indicios débiles", "clase": "debil", "rango": "1 % a 44 %"},
    {"desde": 0, "nombre": "Sin indicios", "clase": "ninguno", "rango": "0 %"},
)

TITULOS_CORTOS = {
    "metadatos": "Metadatos",
    "c2pa": "Credenciales de contenido",
    "ela": "Niveles de error",
}

SEVERIDADES_RELEVANTES = ("directo", "fuerte", "moderado")

NOMBRES_PERFIL = {"abogado": "Abogado", "aseguradora": "Aseguradora"}

# Tipo de resultado de cada capa (funcionalidad 025).
# - Determinista: comprueba un hecho verificable (un dato existe o no, una firma
#   es válida o no). Con el mismo archivo da siempre lo mismo y un tercero
#   puede comprobarlo con otras herramientas.
# - Probabilístico: estima, con umbrales estadísticos o un modelo entrenado,
#   qué tan parecida es la imagen a una editada o generada. Es reproducible,
#   pero puede dar falsas alarmas o pasar por alto una edición.
TIPO_DE_RESULTADO = {
    "integridad": "determinista",
    "metadatos": "determinista",
    "c2pa": "determinista",
    "ela": "probabilistico",
    "red_neuronal": "probabilistico",
}
NOMBRES_TIPO_RESULTADO = {"determinista": "Determinista", "probabilistico": "Probabilístico"}

QUE_MIRA = {
    "metadatos": "Revisa los datos internos del archivo: dispositivo, fechas y programas de "
                 "edición.",
    "c2pa": "Busca credenciales de contenido firmadas que declaren inteligencia artificial o "
            "ediciones.",
    "ela": "Compara cómo se comprime cada zona para detectar partes pegadas o retocadas.",
    "red_neuronal": "Un modelo entrenado estima si la imagen se parece a una generada por IA.",
}

EXPLICACION_TIPOS = {
    "determinista": (
        "Comprueban hechos verificables: si el archivo es idéntico al cargado, qué datos "
        "internos tiene o si trae una firma digital válida. Con el mismo archivo dan siempre "
        "el mismo resultado, y otra persona puede comprobarlo con sus propias herramientas."
    ),
    "probabilistico": (
        "Estiman, con umbrales estadísticos o modelos entrenados, qué tan parecida es la "
        "imagen a una editada o generada. Son reproducibles, pero son una estimación: pueden "
        "señalar una imagen sin ediciones o no detectar una edición cuidadosa. "
        "Por eso su nivel nunca debe leerse como una certeza."
    ),
}

# Lenguaje según el perfil de quien pidió el análisis (RF54).
TEXTOS_RUBRO = {
    "abogado": {
        "titulo": "Informe técnico de imágenes",
        "etiqueta_referencia": "Expediente",
        "intro": (
            "Resultado del análisis automatizado de las imágenes del caso, para evaluar si "
            "conviene ofrecerlas como prueba o pedir una pericia."
        ),
        "que_hacer": (
            "Si alguna imagen tiene indicios moderados o fuertes, pedí una pericia informática "
            "antes de ofrecerla como prueba.",
            "Si todas están sin indicios o con indicios débiles, el análisis no encontró "
            "señales relevantes, pero eso no garantiza su autenticidad.",
            "Conservá este PDF junto con la huella de cada archivo: le permiten al perito "
            "comprobar que analiza la misma evidencia.",
        ),
    },
    "aseguradora": {
        "titulo": "Informe de verificación de fotos del siniestro",
        "etiqueta_referencia": "N.° de siniestro",
        "intro": (
            "Resultado del análisis automatizado de las fotos presentadas en el siniestro, "
            "como apoyo para decidir si se liquida o se deriva a verificación."
        ),
        "que_hacer": (
            "Si alguna foto tiene indicios moderados o fuertes, derivá el siniestro a "
            "verificación o inspección antes de liquidar.",
            "Si todas están sin indicios o con indicios débiles, el análisis no encontró "
            "señales relevantes, pero eso no garantiza su autenticidad.",
            "Ante una posible presentación irregular, pedí la evaluación de un perito antes "
            "de rechazar el reclamo.",
        ),
    },
}


LOGO = Path(__file__).resolve().parents[1] / "plantillas" / "informes" / "logo.png"


def banda_de_indicio(nivel):
    """Banda de la escala de lectura que corresponde a un nivel de 0 a 100."""
    return next(b for b in BANDAS_DE_INDICIO if nivel >= b["desde"])


def _tamanio_legible(octetos):
    """Tamaño de archivo en KB o MB, con coma decimal."""
    if octetos is None:
        return "—"
    if octetos >= 1024 * 1024:
        return f"{octetos / 1024 / 1024:.1f} MB".replace(".", ",")
    return f"{octetos / 1024:.0f} KB"


def _miniatura_como_dato(contenido, tipo="image/jpeg"):
    """Imagen embebida en el HTML (miniatura o mapa ELA), así el PDF no depende de enlaces."""
    if not contenido:
        return None
    return f"data:{tipo};base64," + base64.b64encode(contenido).decode("ascii")


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


def _primera_oracion(texto):
    """La primera oración de un texto, para la versión breve del informe."""
    texto = (texto or "").strip()
    corte = texto.find(". ")
    return texto if corte == -1 else texto[:corte + 1]


def _hallazgos_principales(anomalias, maximo=2):
    """Hasta ``maximo`` hallazgos relevantes, cada uno en una oración."""
    relevantes = [a for a in anomalias if a.severidad in SEVERIDADES_RELEVANTES]
    return [_primera_oracion(a.descripcion) for a in relevantes[:maximo]]


def _resultado(resultado, imagenes_de_capas):
    disponible = resultado.estado == "completado"
    return {
        "titulo": TITULOS_CAPA.get(resultado.capa, resultado.capa),
        "titulo_corto": TITULOS_CORTOS.get(resultado.capa, resultado.capa),
        "tipo": TIPO_DE_RESULTADO.get(resultado.capa, "probabilistico"),
        "que_mira": QUE_MIRA.get(resultado.capa, QUE_SIGNIFICA_GENERICO),
        "lectura": _primera_oracion(resultado.conclusion),
        "principales": _hallazgos_principales(resultado.anomalias) if disponible else [],
        "disponible": disponible,
        "nivel": resultado.nivel,
        "banda": banda_de_indicio(resultado.nivel or 0) if disponible else None,
        "motivo": resultado.motivo,
        "imagen": _miniatura_como_dato(
            imagenes_de_capas.get(getattr(resultado, "id", None)), "image/png"
        ),
    }


def _sello(original):
    """Texto del sello de tiempo de la imagen en Hedera (funcionalidad 023, RF37 CA2)."""
    estado = getattr(original, "sello_estado", None)
    if estado == "sellado":
        fecha = original.sello_fecha.strftime("%d/%m/%Y %H:%M UTC") if original.sello_fecha else ""
        if original.sello_simulado:
            return f"Sello simulado del entorno de pruebas ({fecha}): no tiene validez."
        return f"Hedera, {fecha} · {original.sello_referencia}"
    if estado in ("pendiente", "enviado"):
        return "Pendiente de confirmación en Hedera"
    if estado == "fallido":
        return "Sin sello (Hedera no respondió)"
    return "No solicitado"


def _imagen(incluida, miniaturas, imagenes_de_capas):
    """Identificación de una imagen analizada, su cadena de custodia y sus resultados."""
    original = getattr(incluida, "imagen", None)
    cargo = getattr(original, "usuario", None)
    return {
        "nombre": incluida.nombre,
        "huella": incluida.huella,
        "miniatura": _miniatura_como_dato(miniaturas.get(incluida.id)),
        "integridad": incluida.integridad,
        "formato": (getattr(original, "formato", None) or "—").upper(),
        "dimensiones": (
            f"{original.ancho} × {original.alto} píxeles" if original is not None else "—"
        ),
        "tamanio": _tamanio_legible(getattr(original, "tamanio", None)),
        "cargada_en": getattr(original, "cargada_en", None),
        "cargada_por": f"{cargo.nombre} {cargo.apellido}" if cargo is not None else "—",
        "sello": _sello(original),
        "resultados": [_resultado(r, imagenes_de_capas) for r in incluida.resultados],
    }


def _tipos(imagenes):
    """Los dos tipos de resultado, con las técnicas de este informe que usan cada uno."""
    integridad = {"nombre": "Integridad del archivo",
                  "que_mira": "Compara la huella SHA-256 con la registrada al cargarlo."}
    tecnicas = {"determinista": [integridad], "probabilistico": []}
    vistas = set()
    for imagen in imagenes:
        for resultado in imagen["resultados"]:
            if resultado["titulo_corto"] not in vistas:
                vistas.add(resultado["titulo_corto"])
                tecnicas[resultado["tipo"]].append(
                    {"nombre": resultado["titulo_corto"], "que_mira": resultado["que_mira"]}
                )
    return [
        {"clave": clave, "nombre": NOMBRES_TIPO_RESULTADO[clave], "explicacion": texto,
         "tecnicas": tecnicas[clave]}
        for clave, texto in EXPLICACION_TIPOS.items()
    ]


def armar_datos(analisis, miniaturas, version_plataforma, imagenes_de_capas=None):
    """Datos del informe a partir del análisis.

    Args:
        miniaturas: diccionario ``id de AnalisisImagen -> bytes`` de cada vista reducida.
        imagenes_de_capas: diccionario ``id de ResultadoCapa -> bytes`` (mapas ELA, 011).
        version_plataforma: versión de la aplicación (RN29).
    """
    caso = analisis.caso
    imagenes_de_capas = imagenes_de_capas or {}
    imagenes = [_imagen(incluida, miniaturas, imagenes_de_capas) for incluida in analisis.imagenes]
    perfil = getattr(analisis.solicitante, "perfil", None)
    rubro = TEXTOS_RUBRO.get(perfil, TEXTOS_RUBRO["abogado"])
    return {
        "rubro": rubro,
        # Código, URL y QR de verificación: los agrega ServicioInformes (026).
        "verificacion": None,
        "tipos": _tipos(imagenes),
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
            "finalizado_en": getattr(analisis, "finalizado_en", None),
        },
        "logo": _miniatura_como_dato(LOGO.read_bytes(), "image/png"),
        "bandas": BANDAS_DE_INDICIO,
        "imagenes": imagenes,
        "primera_carga": min(
            (i["cargada_en"] for i in imagenes if i["cargada_en"] is not None), default=None
        ),
        "versiones": {
            "Plataforma": version_plataforma,
            **{TITULOS_CAPA.get(c, c): v for c, v in (analisis.versiones or {}).items()},
            "Plantilla del informe": VERSION_PLANTILLA,
            "WeasyPrint (generación del PDF)": version_weasyprint(),
        },
        "leyenda": LEYENDA_PERICIAL,
        "descargo": DESCARGO,
    }


def generar_pdf(datos, generado_en):
    """El informe como PDF (bytes)."""
    return html_a_pdf("informe_analisis.html", informe=datos, generado_en=generado_en)
