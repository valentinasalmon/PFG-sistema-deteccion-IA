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
    "ela": (
        "Cada vez que una foto se guarda en JPEG pierde un poco de calidad, de manera "
        "pareja en toda la imagen. Si una parte se pegó desde otra foto o se retocó y se "
        "volvió a guardar, esa parte suele haber perdido calidad de otra forma. Esta capa "
        "vuelve a comprimir la imagen y compara cuánto cambia cada zona: las que se "
        "apartan del resto quedan recuadradas en el mapa. Es una técnica orientativa: los "
        "bordes, los textos y las imágenes reenviadas por mensajería también producen "
        "diferencias, por eso sus resultados nunca superan el nivel de indicio moderado."
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

# Descargo pedido en la entrevista del 02/10/2026: resultado parcial, automatizado
# y que no reemplaza el criterio de un perito (ADR-0017).
DESCARGO = (
    "Este resultado es parcial: lo produjo un sistema automatizado de análisis que "
    "incluye técnicas de inteligencia artificial. Es una herramienta auxiliar y no "
    "reemplaza el criterio de un perito o criminalista, que es quien debe evaluar la "
    "evidencia y tomar la decisión final."
)

USO_PREVISTO = (
    "evidentIA es una herramienta de apoyo para abogados y aseguradoras. Sigue el "
    "principio de supervisión humana («persona en el circuito») "
    "del Reglamento (UE) 2024/1689 de Inteligencia Artificial y el sistema de gestión de "
    "la norma ISO/IEC 42001: la plataforma aporta indicios medibles y trazables, y la "
    "decisión sobre la evidencia siempre la toma una persona.",
    "Los umbrales de cada capa se publican en este informe para que el resultado pueda "
    "auditarse y reproducirse. El funcionamiento interno de los algoritmos no se detalla.",
    "Los porcentajes expresan la intensidad de las señales encontradas, no una "
    "probabilidad ni una certeza sobre el origen de la imagen.",
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

METODOLOGIA = (
    "Al cargar cada imagen, la plataforma guardó el archivo original sin modificarlo y "
    "calculó su huella digital SHA-256. Antes de analizarla volvió a calcular la huella y "
    "la comparó con la registrada: solo se analizan los archivos idénticos al original.",
    "Cada imagen se examinó con capas independientes, cada una con una técnica distinta. "
    "Cada capa informa su propio nivel de indicio; los niveles no se combinan en un "
    "puntaje único porque miden aspectos diferentes.",
    "El análisis es automático y reproducible: con el mismo archivo y las mismas "
    "versiones de los componentes, listadas al final, se obtiene el mismo resultado.",
)

GLOSARIO = (
    ("Indicio", "Señal técnica que suele aparecer en imágenes editadas o generadas. "
     "No prueba por sí sola una manipulación."),
    ("Huella digital SHA-256", "Código de 64 caracteres calculado a partir del archivo. "
     "Si el archivo cambia aunque sea un punto, la huella cambia por completo."),
    ("Metadatos", "Datos guardados dentro del archivo además de la imagen: dispositivo, "
     "fecha, programa de edición, ubicación."),
    ("C2PA", "Estándar de credenciales de contenido firmadas digitalmente que declaran "
     "quién creó o editó una imagen y con qué herramienta."),
    ("ELA", "Análisis de niveles de error: compara cómo cambia cada zona de una imagen "
     "JPEG al volver a comprimirla."),
    ("Cadena de custodia", "Registro que permite demostrar que la evidencia analizada es la "
     "misma que se cargó y que no se modificó en el camino."),
)

NOMBRES_SEVERIDAD = {
    "directo": "Directo",
    "fuerte": "Fuerte",
    "moderado": "Moderado",
    "debil": "Débil",
    "neutro": "Informativo",
}
ESTADOS_FIRMA = {
    "confiable": "Firma confiable",
    "firmante_no_reconocido": "Firmante no reconocido",
    "contenido_modificado": "Modificada después de firmarse",
    "firma_invalida": "Credenciales no válidas",
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
    "metadatos": "Revisa los datos internos del archivo: dispositivo, fechas y programas de edición.",
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
        "marcar una imagen auténtica (falsa alarma) o no detectar una edición cuidadosa. "
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
            "Ante una posible presentación fraudulenta, pedí la evaluación de un perito antes "
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


def _criterios(resultado):
    """Valores de referencia y valores obtenidos de una capa (entrevista del 02/10/2026).

    Muestra los umbrales numéricos con los que se juzga cada señal sin
    describir el algoritmo. Cada fila es (criterio, referencia sin edición,
    valor obtenido).
    """
    detalle = resultado.detalle or {}
    relevantes = sum(1 for a in resultado.anomalias if a.severidad in SEVERIDADES_RELEVANTES)
    hallazgos = str(relevantes) if relevantes else "Ninguna"
    filas = []
    if resultado.capa == "metadatos":
        filas += [
            ("Datos descriptivos del archivo (EXIF, XMP, IPTC)",
             "Presentes en una foto original de cámara o teléfono",
             "Ausentes" if detalle.get("sin_metadatos") else "Presentes"),
            ("Señales de edición, de generación o incoherencias de fechas",
             "Ninguna (una modificación más de 24 h después de la captura cuenta como señal)",
             hallazgos),
        ]
    elif resultado.capa == "c2pa":
        if detalle.get("sin_credenciales"):
            credenciales = "Ausentes"
        else:
            credenciales = ESTADOS_FIRMA.get(detalle.get("estado_firma"), "Presentes")
        filas += [
            ("Credenciales de contenido C2PA",
             "Ausentes, o firma confiable sin declaración de IA", credenciales),
            ("Declaraciones de IA o de edición en las credenciales", "Ninguna", hallazgos),
        ]
    elif resultado.capa == "ela":
        desvio = detalle.get("desvio_maximo")
        filas += [
            ("Regiones que se apartan del resto (mínimo 6 bloques de 16 × 16 píxeles)",
             "0", str(detalle.get("regiones", "—"))),
            ("Desvío medio de la región más marcada",
             "Menos de 10 desvíos robustos (umbral de indicio moderado); un bloque se "
             "marca desde 4", f"{desvio} desvíos".replace(".", ",") if desvio else "—"),
        ]
    filas.append(("Nivel de indicio de la capa", "0 % (sin señales)", f"{resultado.nivel} %"))
    return [{"criterio": c, "referencia": r, "obtenido": o} for c, r, o in filas]


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
        "conclusion": resultado.conclusion,
        "motivo": resultado.motivo,
        "version": resultado.version,
        "que_significa": QUE_SIGNIFICA.get(resultado.capa, QUE_SIGNIFICA_GENERICO),
        "criterios": _criterios(resultado) if disponible else [],
        "anomalias": [
            {
                "severidad": NOMBRES_SEVERIDAD.get(a.severidad, a.severidad),
                "descripcion": a.descripcion,
            }
            for a in resultado.anomalias
        ],
        "tabla": (resultado.detalle or {}).get("tabla", []),
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
    tecnicas = {"determinista": [{"nombre": "Integridad del archivo",
                                  "que_mira": "Compara la huella SHA-256 con la registrada al cargarlo."}],
                "probabilistico": []}
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
    # Columnas del resumen: las capas en el orden en que aparecen.
    columnas = list(dict.fromkeys(r["titulo_corto"] for i in imagenes for r in i["resultados"]))
    for imagen in imagenes:
        por_capa = {r["titulo_corto"]: r for r in imagen["resultados"]}
        imagen["resumen"] = [por_capa.get(columna) for columna in columnas]
    perfil = getattr(analisis.solicitante, "perfil", None)
    rubro = TEXTOS_RUBRO.get(perfil, TEXTOS_RUBRO["abogado"])
    return {
        "rubro": rubro,
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
        "metodologia": METODOLOGIA,
        "glosario": GLOSARIO,
        "imagenes": imagenes,
        "primera_carga": min(
            (i["cargada_en"] for i in imagenes if i["cargada_en"] is not None), default=None
        ),
        "columnas_resumen": columnas,
        "versiones": {
            "Plataforma": version_plataforma,
            **{TITULOS_CAPA.get(c, c): v for c, v in (analisis.versiones or {}).items()},
            "Plantilla del informe": VERSION_PLANTILLA,
            "WeasyPrint (generación del PDF)": version_weasyprint(),
        },
        "escala": ESCALA_DE_INDICIO,
        "leyenda": LEYENDA_PERICIAL,
        "descargo": DESCARGO,
        "uso_previsto": USO_PREVISTO,
        "limitaciones": LIMITACIONES,
    }


def generar_pdf(datos, generado_en):
    """El informe como PDF (bytes)."""
    return html_a_pdf("informe_analisis.html", informe=datos, generado_en=generado_en)
