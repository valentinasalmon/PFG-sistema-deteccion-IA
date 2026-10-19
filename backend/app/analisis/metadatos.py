"""Capa 1: análisis de metadatos EXIF, XMP, IPTC y PNG.

Reescritura mejorada de ``metadatos_service.py`` del repositorio anterior
(``valentinasalmon/TIF``): conserva sus reglas y su escala de severidad, y
agrega la fecha de lanzamiento del dispositivo, el origen sintético IPTC, la
ausencia de metadatos y el nivel de indicio de 0 a 100. La revisión completa
está en ``docs/funcionalidades/007-motor-de-analisis/plan.md``.

La imagen se pasa a ExifTool por la entrada estándar: no se escriben copias
de la evidencia en disco. La capa no accede a la base de datos.

Realiza: RF39 (CA1 a CA4), RF43 (CA1, CA2); RN26, RN27, RN29.
"""
import io
import json
import subprocess
from datetime import datetime, timedelta
from functools import lru_cache

from PIL import Image

from app.analisis.base import (
    RECOMENDACION,
    SEVERIDAD_DEBIL,
    SEVERIDAD_DIRECTO,
    SEVERIDAD_FUERTE,
    SEVERIDAD_MODERADO,
    SEVERIDAD_NEUTRO,
    Anomalia,
    CapaAnalisis,
    CapaNoDisponible,
    ResultadoCapa,
)
from app.analisis.dispositivos import fecha_de_lanzamiento

VERSION_CAPA = "1.0"

# --- Reglas editables (listas y umbrales) ---

EDITORES = (
    "photoshop", "lightroom", "gimp", "snapseed", "facetune", "picsart", "canva",
    "pixelmator", "affinity photo", "luminar", "remini", "meitu", "faceapp", "photoroom",
    "photopea", "paint.net", "fotor", "vsco",
)
GENERADORES = (
    "midjourney", "dall-e", "dall·e", "dalle", "stable diffusion", "stability ai", "firefly",
    "chatgpt", "openai", "gpt-4o", "gpt image", "google imagen", "gemini", "leonardo.ai",
    "ideogram", "black forest labs", "flux.1", "novelai", "comfyui", "automatic1111",
    "invokeai", "bing image creator", "microsoft designer",
)
PALABRAS_GENERACION_PNG = (
    "prompt", "negative prompt", "negative_prompt", "steps:", "sampler", "cfg scale",
    "cfg_scale", "seed:", "model hash", "workflow", "lora",
)
ORIGENES_SINTETICOS_IPTC = (
    "trainedalgorithmicmedia", "compositesynthetic", "algorithmicmedia",
    "compositewithtrainedalgorithmicmedia",
)
MARCAS_CON_MAKERNOTES = (
    "apple", "samsung", "xiaomi", "motorola", "huawei", "google", "canon", "nikon", "sony",
    "fujifilm", "olympus", "panasonic", "oneplus", "oppo", "vivo", "realme",
)
CAMPOS_DE_CAPTURA = (
    "ExposureTime", "FNumber", "ISO", "FocalLength", "Flash", "ExposureProgram", "MeteringMode",
)
UMBRAL_MODIFICACION = timedelta(hours=24)
# Las fechas EXIF no tienen zona horaria: se tolera un día respecto de la carga.
TOLERANCIA_ZONA_HORARIA = timedelta(days=1)
DIMENSIONES_TIPICAS_IA = {
    (512, 512), (768, 768), (1024, 1024), (1536, 1536), (2048, 2048),
    (1024, 1792), (1792, 1024),  # DALL·E 3
    (1024, 1536), (1536, 1024),  # GPT Image
    (832, 1216), (1216, 832), (896, 1152), (1152, 896), (768, 1344), (1344, 768),  # SDXL
}
# Grupos que describen la entrada estándar de ExifTool, no la imagen.
GRUPOS_IGNORADOS = ("SourceFile", "ExifTool:", "File:System:")
GRUPOS_DESCRIPTIVOS = ("EXIF:", "XMP:", "IPTC:", "MakerNotes:", "Photoshop:", "JUMBF:")
# Datos de las credenciales de contenido (C2PA) que ExifTool lee sin verificar
# la firma; la verificación es de la capa 2 (funcionalidad 009).
CAMPOS_C2PA_SOFTWARE = ("C2PASoftware",)
CAMPO_C2PA_ORIGEN = "C2PAOrigen"
ACLARACION_C2PA = " (dato de las credenciales de contenido C2PA, sin verificar su firma)"
NOTA_C2PA = (
    "Algunos datos provienen de las credenciales de contenido (C2PA) del archivo; la "
    "validez de su firma se verifica en la capa de credenciales de contenido."
)

# --- Nivel de indicio (documentado en el plan de la 007) ---

BASES = {
    SEVERIDAD_DIRECTO: 90, SEVERIDAD_FUERTE: 70, SEVERIDAD_MODERADO: 45,
    SEVERIDAD_DEBIL: 20, SEVERIDAD_NEUTRO: 0,
}
INCREMENTO_POR_ANOMALIA = 10
NIVEL_MAXIMO = 90  # el máximo del sistema corresponde a C2PA (RN28)

# Campos de la tabla de metadatos relevantes (RF39 CA4): etiqueta y claves posibles.
CAMPOS_TABLA = (
    ("Fabricante", ("Make",)),
    ("Modelo", ("Model",)),
    ("Lente", ("LensModel",)),
    ("Software", ("Software",)),
    ("Herramienta de creación", ("CreatorTool",)),
    ("Fecha de captura", ("DateTimeOriginal",)),
    ("Fecha de creación", ("CreateDate",)),
    ("Fecha de modificación", ("ModifyDate",)),
    ("Exposición", ("ExposureTime",)),
    ("Apertura", ("FNumber",)),
    ("ISO", ("ISO",)),
    ("Distancia focal", ("FocalLength",)),
    ("Ubicación GPS", ("GPSPosition",)),
    ("Origen declarado (IPTC)", ("DigitalSourceType", CAMPO_C2PA_ORIGEN)),
    ("Generador declarado (C2PA)", CAMPOS_C2PA_SOFTWARE),
    ("Descripción", ("ImageDescription", "Description")),
)
LARGO_MAXIMO_VALOR = 300


def _texto(valor):
    """Texto acotado; ExifTool puede devolver números o estructuras (regresión del TIF)."""
    if isinstance(valor, (dict, list)):
        valor = json.dumps(valor, ensure_ascii=False)
    texto = str(valor).strip()
    return texto if len(texto) <= LARGO_MAXIMO_VALOR else texto[:LARGO_MAXIMO_VALOR] + "…"


@lru_cache(maxsize=4)
def version_exiftool(ruta):
    """Versión instalada de ExifTool, o None si no está disponible."""
    try:
        salida = subprocess.run(
            [ruta, "-ver"], capture_output=True, text=True, timeout=10, check=True
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return salida.stdout.strip() or None


def _declaraciones_c2pa(datos):
    """Software y origen que declaran las acciones C2PA, leídas por ExifTool con ``-struct``.

    Devuelve un diccionario con ``C2PASoftware`` y ``C2PAOrigen`` (textos
    separados por punto y coma), solo con los que aparezcan.
    """
    softwares, origenes = [], []
    for clave, valor in datos.items():
        if not clave.startswith("JUMBF:"):
            continue
        if clave.endswith(":Claim_generator_info") and isinstance(valor, dict):
            softwares.append(_texto(valor.get("name", "")))
        if clave.endswith(":Actions") and isinstance(valor, list):
            for accion in (a for a in valor if isinstance(a, dict)):
                agente = accion.get("softwareAgent")
                nombre = agente.get("name") if isinstance(agente, dict) else agente
                softwares.append(_texto(nombre or ""))
                origenes.append(_texto(accion.get("digitalSourceType") or ""))
    resultado = {}
    if any(softwares):
        resultado["C2PASoftware"] = "; ".join(dict.fromkeys(s for s in softwares if s))
    if any(origenes):
        resultado["C2PAOrigen"] = "; ".join(dict.fromkeys(o for o in origenes if o))
    return resultado


def _fecha_exif(valor):
    """Fecha EXIF ``AAAA:MM:DD HH:MM:SS`` (se ignoran fracciones y zona), o None."""
    texto = str(valor or "").strip()[:19]
    try:
        return datetime.strptime(texto, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


class CapaMetadatos(CapaAnalisis):
    """Busca en los metadatos indicios de edición, generación o inconsistencias."""

    nombre = "metadatos"
    titulo = "Metadatos"

    def __init__(self, ruta_exiftool="exiftool", tiempo_espera=20):
        self.ruta_exiftool = ruta_exiftool
        self.tiempo_espera = tiempo_espera

    def version(self):
        """Versión de la capa y de ExifTool (RN29)."""
        exiftool = version_exiftool(self.ruta_exiftool) or "no disponible"
        return f"{VERSION_CAPA} (ExifTool {exiftool})"

    # --- Extracción ---

    def extraer(self, contenido):
        """Metadatos con grupo (``EXIF:IFD0:Make``) y también con el nombre solo (``Make``).

        Raises:
            CapaNoDisponible: si ExifTool no está instalado, tarda demasiado o
                devuelve algo ilegible.
        """
        try:
            salida = subprocess.run(
                [self.ruta_exiftool, "-json", "-G0:1", "-struct", "-charset", "utf8", "-"],
                input=contenido, capture_output=True, timeout=self.tiempo_espera, check=False,
            )
        except FileNotFoundError as error:
            raise CapaNoDisponible(
                "ExifTool no está instalado en el servidor de análisis."
            ) from error
        except subprocess.TimeoutExpired as error:
            raise CapaNoDisponible("ExifTool tardó demasiado en leer la imagen.") from error
        try:
            crudo = json.loads(salida.stdout.decode("utf-8", errors="replace"))[0]
        except (ValueError, IndexError) as error:
            raise CapaNoDisponible("No se pudieron leer los metadatos de la imagen.") from error
        datos = {
            clave: valor for clave, valor in crudo.items()
            if not clave.startswith(GRUPOS_IGNORADOS)
        }
        # Los nombres solos permiten buscar "Make" sin saber el grupo; si un
        # nombre aparece en varios grupos, prevalece el primero (como en el TIF).
        for clave, valor in list(datos.items()):
            datos.setdefault(clave.rsplit(":", 1)[-1], valor)
        datos.update(_declaraciones_c2pa(datos))
        return datos

    @staticmethod
    def textos_png(contenido):
        """Bloques de texto de un PNG (tEXt, iTXt, zTXt) leídos con Pillow."""
        try:
            with Image.open(io.BytesIO(contenido)) as imagen:
                return {
                    str(clave): valor for clave, valor in imagen.info.items()
                    if isinstance(valor, str)
                }
        except OSError:
            return {}

    # --- Reglas: cada una devuelve una lista de anomalías, quizás vacía ---

    @staticmethod
    def regla_software(datos):
        """Editor o generador declarado en Software, CreatorTool o el historial (RF39 CA1)."""
        campos = (
            "Software", "CreatorTool", "ProcessingSoftware", "HistorySoftwareAgent",
            *CAMPOS_C2PA_SOFTWARE,
        )
        anomalias = []
        for lista, que in ((GENERADORES, "un generador de imágenes"), (EDITORES, "un editor")):
            for campo in campos:
                valor = _texto(datos.get(campo) or "")
                coincidencia = next((n for n in lista if n in valor.lower()), None)
                if coincidencia:
                    aclaracion = ACLARACION_C2PA if campo in CAMPOS_C2PA_SOFTWARE else ""
                    anomalias.append(Anomalia(
                        campo, valor,
                        f"El archivo declara procesamiento con «{valor}», que corresponde a "
                        f"{que}.{aclaracion}",
                        SEVERIDAD_DIRECTO,
                    ))
                    break
        return anomalias

    @staticmethod
    def regla_historial(datos):
        """Historial de edición registrado en XMP (xmpMM:History)."""
        historial = datos.get("History")
        if not historial:
            return []
        pasos = historial if isinstance(historial, list) else [historial]
        acciones = ", ".join(
            _texto(p.get("Action", "")) if isinstance(p, dict) else _texto(p) for p in pasos
        )
        return [Anomalia(
            "xmpMM:History", acciones or _texto(historial),
            f"El archivo tiene un historial de edición registrado en XMP con {len(pasos)} "
            "paso(s).",
            SEVERIDAD_DIRECTO,
        )]

    @staticmethod
    def regla_origen_iptc(datos):
        """Origen sintético declarado con el vocabulario IPTC, en XMP o en C2PA."""
        for campo, aclaracion in (
            ("DigitalSourceType", ""), (CAMPO_C2PA_ORIGEN, ACLARACION_C2PA),
        ):
            valor = _texto(datos.get(campo) or "")
            if any(origen in valor.lower() for origen in ORIGENES_SINTETICOS_IPTC):
                return [Anomalia(
                    campo, valor,
                    "Los metadatos declaran que el contenido fue creado o modificado con un "
                    f"sistema de inteligencia artificial, según el vocabulario IPTC{aclaracion}.",
                    SEVERIDAD_DIRECTO,
                )]
        return []

    @staticmethod
    def regla_parametros_png(textos_png):
        """Parámetros de generación de IA en los bloques de texto de un PNG."""
        texto = " ".join(f"{clave} {valor}" for clave, valor in textos_png.items()).lower()
        encontradas = [p.rstrip(":") for p in PALABRAS_GENERACION_PNG if p in texto]
        if not encontradas:
            return []
        return [Anomalia(
            "PNG tEXt/iTXt", ", ".join(encontradas),
            "Los datos de texto del PNG contienen parámetros típicos de herramientas de "
            f"generación de imágenes: {', '.join(encontradas)}.",
            SEVERIDAD_DIRECTO,
        )]

    @staticmethod
    def regla_makernotes(datos):
        """Marca conocida sin el bloque propietario (MakerNotes) que suele incluir."""
        marca = _texto(datos.get("Make") or "")
        if not any(m in marca.lower() for m in MARCAS_CON_MAKERNOTES):
            return []
        if any(clave.startswith("MakerNotes:") for clave in datos):
            return []
        return [Anomalia(
            "MakerNotes", "ausente",
            f"El dispositivo declarado es «{marca}», pero no se encontró el bloque de datos "
            "propietario (MakerNotes) que ese fabricante suele incluir.",
            SEVERIDAD_FUERTE,
        )]

    @staticmethod
    def regla_cronologia(datos, contexto):
        """Fechas imposibles o inconsistentes (RF39 CA2)."""
        anomalias = []
        captura = _fecha_exif(datos.get("DateTimeOriginal") or datos.get("CreateDate"))
        modificacion = _fecha_exif(datos.get("ModifyDate"))
        if captura and captura > contexto.cargada_en + TOLERANCIA_ZONA_HORARIA:
            anomalias.append(Anomalia(
                "DateTimeOriginal", captura.isoformat(sep=" "),
                "La fecha de captura declarada es posterior a la fecha en que la imagen se "
                "cargó en la plataforma, lo que resulta cronológicamente imposible.",
                SEVERIDAD_FUERTE,
            ))
        lanzamiento = fecha_de_lanzamiento(datos.get("Model"))
        if captura and lanzamiento and captura.date() < lanzamiento:
            anomalias.append(Anomalia(
                "DateTimeOriginal / Model",
                f"captura {captura.date().isoformat()}, lanzamiento {lanzamiento.isoformat()}",
                f"La fecha de captura es anterior al lanzamiento del dispositivo declarado "
                f"(«{_texto(datos.get('Model'))}»), lo que resulta cronológicamente imposible.",
                SEVERIDAD_FUERTE,
            ))
        if captura and modificacion and modificacion - captura > UMBRAL_MODIFICACION:
            diferencia = modificacion - captura
            anomalias.append(Anomalia(
                "ModifyDate / DateTimeOriginal", f"diferencia de {diferencia}",
                "La fecha de última modificación es posterior a la de captura por más de "
                f"{int(UMBRAL_MODIFICACION.total_seconds() // 3600)} horas, lo que sugiere "
                "un procesamiento posterior.",
                SEVERIDAD_MODERADO,
            ))
        return anomalias

    @staticmethod
    def regla_bloque_captura(datos):
        """Dispositivo declarado sin ninguno de los parámetros técnicos de una cámara."""
        tiene_dispositivo = datos.get("Make") or datos.get("Model")
        if not tiene_dispositivo or any(datos.get(campo) for campo in CAMPOS_DE_CAPTURA):
            return []
        return [Anomalia(
            "Parámetros de captura", "ausentes",
            "El dispositivo está declarado, pero faltan todos los parámetros técnicos que "
            "registra una cámara real (exposición, apertura, ISO, distancia focal).",
            SEVERIDAD_MODERADO,
        )]

    @staticmethod
    def regla_dimensiones(contexto):
        """Resolución típica de la salida de modelos generativos."""
        if (contexto.ancho, contexto.alto) not in DIMENSIONES_TIPICAS_IA:
            return []
        return [Anomalia(
            "Dimensiones", f"{contexto.ancho} × {contexto.alto}",
            f"La imagen mide {contexto.ancho} × {contexto.alto} píxeles, una resolución "
            "habitual en la salida de modelos generativos. Por sí sola es un indicio débil.",
            SEVERIDAD_DEBIL,
        )]

    @staticmethod
    def sin_metadatos(datos, textos_png):
        """True si la imagen no conserva metadatos descriptivos (RF39 CA3)."""
        return not textos_png and not any(
            clave.startswith(GRUPOS_DESCRIPTIVOS) for clave in datos
        )

    # --- Resultado ---

    @staticmethod
    def calcular_nivel(anomalias):
        """Nivel de indicio de 0 a 90 (método documentado en el plan de la 007)."""
        if not anomalias:
            return 0
        bases = sorted((BASES[a.severidad] for a in anomalias), reverse=True)
        adicionales = sum(1 for base in bases[1:] if base >= BASES[SEVERIDAD_MODERADO])
        return min(NIVEL_MAXIMO, bases[0] + INCREMENTO_POR_ANOMALIA * adicionales)

    @staticmethod
    def redactar_conclusion(nivel, anomalias, sin_metadatos):
        """Conclusión redactada como indicio, siempre con la recomendación (RN27)."""
        if sin_metadatos and nivel == 0:
            texto = (
                "La imagen no conserva metadatos descriptivos. Es habitual cuando pasa por "
                "aplicaciones de mensajería o redes sociales, que los eliminan al recomprimirla, "
                "y por sí solo no indica manipulación."
            )
        elif nivel == 0:
            texto = (
                "No se encontraron indicios de edición ni de generación en los metadatos. La "
                "ausencia de indicios en esta capa no descarta modificaciones: conviene "
                "contrastarla con las demás capas."
            )
        else:
            principales = sorted(anomalias, key=lambda a: BASES[a.severidad], reverse=True)[:2]
            if nivel >= BASES[SEVERIDAD_FUERTE]:
                intensidad = "indicios fuertes"
            elif nivel >= BASES[SEVERIDAD_MODERADO]:
                intensidad = "indicios moderados"
            else:
                intensidad = "indicios débiles"
            texto = (
                f"Los metadatos presentan {intensidad} de edición, generación o "
                "inconsistencias. " + " ".join(a.descripcion for a in principales)
            )
            if any(a.campo in (*CAMPOS_C2PA_SOFTWARE, CAMPO_C2PA_ORIGEN) for a in anomalias):
                texto = f"{texto} {NOTA_C2PA}"
        return f"{texto} {RECOMENDACION}"

    @staticmethod
    def tabla(datos, contexto, textos_png):
        """Metadatos relevantes para mostrar en el resultado (RF39 CA4)."""
        filas = [{"campo": "Dimensiones", "valor": f"{contexto.ancho} × {contexto.alto} píxeles"}]
        for etiqueta, claves in CAMPOS_TABLA:
            valor = next((datos[c] for c in claves if datos.get(c) not in (None, "")), None)
            if valor is not None:
                filas.append({"campo": etiqueta, "valor": _texto(valor)})
        if textos_png:
            filas.append({
                "campo": "Textos del PNG",
                "valor": _texto("; ".join(f"{k}: {v}" for k, v in textos_png.items())),
            })
        return filas

    def analizar(self, contenido, contexto):
        """Aplica todas las reglas y arma el resultado de la capa (RF39, RF43)."""
        datos = self.extraer(contenido)
        textos_png = self.textos_png(contenido) if contexto.formato == "png" else {}
        sin_metadatos = self.sin_metadatos(datos, textos_png)

        anomalias = []
        anomalias += self.regla_software(datos)
        anomalias += self.regla_historial(datos)
        anomalias += self.regla_origen_iptc(datos)
        anomalias += self.regla_parametros_png(textos_png)
        anomalias += self.regla_makernotes(datos)
        anomalias += self.regla_cronologia(datos, contexto)
        anomalias += self.regla_bloque_captura(datos)
        anomalias += self.regla_dimensiones(contexto)
        nivel = self.calcular_nivel(anomalias)
        if sin_metadatos:
            anomalias.append(Anomalia(
                "Metadatos", "ausentes",
                "La imagen no conserva metadatos EXIF ni XMP. Puede deberse a la "
                "recompresión de aplicaciones de mensajería o redes sociales y no implica "
                "manipulación por sí misma.",
                SEVERIDAD_NEUTRO,
            ))
        return ResultadoCapa(
            nivel=nivel,
            anomalias=anomalias,
            conclusion=self.redactar_conclusion(nivel, anomalias, sin_metadatos),
            detalle={
                "tabla": self.tabla(datos, contexto, textos_png),
                "sin_metadatos": sin_metadatos,
            },
        )
