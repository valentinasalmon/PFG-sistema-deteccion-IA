"""Revisión automática del informe final del proyecto (funcionalidad 037).

Lee el texto del informe (exportado de Google Docs como texto sin formato o
leído con el conector de Google Drive) y detecta los errores mecánicos que un
evaluador de tesis marca primero: secciones vacías, párrafos duplicados,
numeración de tablas, figuras y capítulos, citas sin entrada en la
bibliografía (y al revés), listas con viñetas en un texto que va en prosa,
tiempo verbal pasado, marcadores sin completar, formato de números y
términos mal escritos. No reemplaza la lectura humana: la prepara, para que
el revisor dedique su tiempo a la argumentación y a la evidencia.

Las reglas que aplica están explicadas en
``docs/informe-final/guia-de-redaccion.md``.

Uso, desde ``backend/``::

    python herramientas/revisar_informe.py informe.txt [--json] [--salida revision.md]

Devuelve 1 si encuentra al menos un error, para poder usarlo como control.

Realiza: RNF19 (calidad de la documentación); funcionalidad 037.
"""
import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

ERROR = "error"
ADVERTENCIA = "advertencia"
SUGERENCIA = "sugerencia"
ORDEN_SEVERIDAD = {ERROR: 0, ADVERTENCIA: 1, SUGERENCIA: 2}

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
           "XI", "XII", "XIII", "XIV", "XV"]

# Capítulos que exige el protocolo de la cátedra (AE1 a AE3), en orden.
CAPITULOS_DEL_PROTOCOLO = [
    "DEFINICIÓN DEL PROYECTO",
    "RELEVAMIENTO E INVESTIGACIÓN DE MERCADO",
    "ENTORNO Y DOMINIO DEL SISTEMA DE INFORMACIÓN",
    "MODELO DE NEGOCIOS DEL PROYECTO",
    "PLANIFICACIÓN DEL PROYECTO",
    "METODOLOGÍAS DE GESTIÓN",
    "MARKETING DEL PROYECTO",
    "PROPIEDAD INTELECTUAL",
    "DISEÑO DE SOLUCIÓN",
    "RECURSOS DEL PROYECTO",
    "OPORTUNIDADES DEL PROYECTO",
    "LECCIONES APRENDIDAS DEL PROYECTO",
    "ENTREGABLES",
]

# Términos con una forma correcta única en el informe.
TERMINOS = {
    r"\bEvidentIA\b": "evidentIA (la marca va con minúscula inicial)",
    r"\bEVIDENTIA\b(?! ESTUDIO)": "evidentIA (salvo al citar la marca registrada por terceros)",
    r"\bBasico\b": "Básico",
    r"\bImagenes\b": "Imágenes",
    r"\bimagenes\b": "imágenes",
    r"\bDenominacion\b": "Denominación",
    r"\bBitacora\b": "Bitácora",
    r"\bbitacora\b": "bitácora",
    r"\bfotografias\b": "fotografías",
    r"\bimégenes\b": "imágenes",
    r"\bGuión\b": "Guion (sin tilde desde la Ortografía de 2010)",
    r"\bguión\b": "guion (sin tilde desde la Ortografía de 2010)",
    r"\bComcepto\b": "Concepto",
    r"\bsalidad\b": "salida",
}

EXTRANJERISMOS = ["deepfake", "deepfakes", "mirror node", "testnet", "mainnet", "webhook"]

# Frases que suenan a veredicto: el sistema solo informa indicios (RN27).
VEREDICTOS = [
    r"la imagen es (falsa|aut[eé]ntica|real|ver[ií]dica)",
    r"(demuestra|confirma|prueba|garantiza) que la imagen",
    r"detecta (con certeza|sin error)",
    r"100 ?% (seguro|confiable|preciso)",
    r"\bimagen (falsa|adulterada) confirmada\b",
]

# Pretérito en voz pasiva refleja o en tercera persona: el informe va en presente.
PRETERITO = re.compile(
    r"\b(se \w+(?:ó|aron|ieron)|fue|fueron|hubo|realizó|realizaron|permitió|"
    r"obtuvo|decidió|eligió|implementó|desarrolló|utilizó|detectó|encontró)\b",
    re.IGNORECASE,
)

MARCADORES = re.compile(
    r"\[(?:completar|a definir|pendiente|confirmar|actualizar|horas|marca|modelo|"
    r"el valor|sin costo|costo|gasto|insertar)[^\]]*\]|\(completar\)|"
    r"\bcompletar\b|\?\s*\||\\?\[[^\]]*≥[^\]]*\]",
    re.IGNORECASE,
)


@dataclass
class Hallazgo:
    """Una observación de la revisión, con su ubicación y cómo corregirla."""

    severidad: str
    regla: str
    linea: int
    texto: str
    correccion: str


def limpiar(linea):
    """Saca las marcas de Markdown y de comentarios que agrega la exportación."""
    linea = re.sub(r"<comment_(start|end) id=[^>]*>", "", linea)
    linea = re.sub(r"\[([^\]]*)\]\(\?tab=[^)]*\)", r"\1", linea)
    linea = linea.replace("**", "").replace("\\[", "[").replace("\\]", "]")
    linea = re.sub(r"^#+\s*", "", linea)
    return linea.strip()


def sin_tildes(texto):
    """Devuelve el texto en mayúsculas y sin tildes, para comparar títulos."""
    normalizado = unicodedata.normalize("NFD", texto.upper())
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def extracto(texto, largo=110):
    """Recorta el texto para mostrarlo en el informe de revisión."""
    texto = " ".join(texto.split())
    return texto if len(texto) <= largo else texto[: largo - 1] + "…"


class Informe:
    """El texto del informe dividido en líneas y en sus partes principales."""

    def __init__(self, texto):
        self.originales = texto.splitlines()
        self.lineas = [limpiar(original) for original in self.originales]
        self.inicio_cuerpo = self._buscar(r"^resumen$", 0)
        self.inicio_bibliografia = self._buscar(r"^bibliograf[ií]a$", len(self.lineas))
        self.inicio_anexos = self._buscar(r"^anexos$", len(self.lineas))
        self.fin_indice = self._fin_del_indice()

    def _buscar(self, patron, por_defecto):
        """Primera línea que coincide con el patrón (sin distinguir mayúsculas)."""
        for numero, linea in enumerate(self.lineas):
            if re.match(patron, linea, re.IGNORECASE):
                return numero
        return por_defecto

    def _fin_del_indice(self):
        """Última línea de los índices (general y de tablas y figuras)."""
        ultima = self.inicio_cuerpo
        for numero, original in enumerate(self.originales):
            if "?tab=" in original:
                ultima = numero
        return ultima

    def cuerpo(self):
        """Líneas del cuerpo: después de los índices y antes de la bibliografía."""
        for numero in range(self.inicio_cuerpo, self.inicio_bibliografia):
            if self.inicio_cuerpo < numero <= self.fin_indice:
                continue
            yield numero, self.lineas[numero]

    def es_tabla(self, numero):
        """Indica si la línea es una fila de tabla en Markdown."""
        return self.originales[numero].lstrip().startswith("|")

    def es_titulo(self, numero):
        """Indica si la línea es un título (Markdown o un título conocido)."""
        original = self.originales[numero].lstrip()
        if original.startswith("#") and not original.startswith("#####"):
            return bool(self.lineas[numero])
        return bool(re.match(r"^CAP[IÍ]TULO\b", self.lineas[numero]))

    def nivel(self, numero):
        """Nivel del título: cantidad de «#» en Markdown; un capítulo es el nivel 1."""
        original = self.originales[numero].lstrip()
        if re.match(r"^#*\s*\**CAP[IÍ]TULO", original):
            return 1
        return len(original) - len(original.lstrip("#")) or 2

    def bibliografia(self):
        """Entradas de la bibliografía, con su número de línea."""
        for numero in range(self.inicio_bibliografia + 1, self.inicio_anexos):
            if self.lineas[numero]:
                yield numero, self.lineas[numero]


def revisar_secciones_vacias(informe):
    """Un título seguido directamente por otro título es una sección vacía."""
    hallazgos = []
    titulos = [n for n, _ in informe.cuerpo() if informe.es_titulo(n)]
    for actual, siguiente in zip(titulos, titulos[1:]):
        intermedias = [informe.lineas[n] for n in range(actual + 1, siguiente)
                       if informe.lineas[n]]
        abre_subtitulo = informe.nivel(siguiente) > informe.nivel(actual)
        if not intermedias and not abre_subtitulo:
            hallazgos.append(Hallazgo(ERROR, "Sección vacía", actual + 1,
                                      extracto(informe.lineas[actual]),
                                      "Redactar la sección o quitar el título."))
    return hallazgos


def revisar_duplicados(informe):
    """Párrafos largos idénticos en dos lugares del cuerpo."""
    hallazgos = []
    vistos = {}
    for numero, linea in informe.cuerpo():
        if len(linea) < 200 or informe.es_tabla(numero):
            continue
        clave = " ".join(linea.lower().split())
        if clave in vistos:
            hallazgos.append(Hallazgo(
                ERROR, "Párrafo duplicado", numero + 1, extracto(linea),
                f"El mismo párrafo ya está en la línea {vistos[clave] + 1}: "
                "quitar uno o reemplazarlo por el texto que corresponde a esa sección."))
        else:
            vistos[clave] = numero
    return hallazgos


def revisar_capitulos(informe):
    """Los capítulos van numerados del I en adelante, sin repetir ni saltar."""
    hallazgos = []
    esperado = 0
    for numero, linea in informe.cuerpo():
        coincidencia = re.match(r"^CAP[IÍ]TULO\s+([IVXL]+)\s*[-:–]?\s*(.*)$", linea)
        if not coincidencia:
            continue
        romano, titulo = coincidencia.groups()
        correcto = ROMANOS[esperado] if esperado < len(ROMANOS) else None
        if romano != correcto:
            hallazgos.append(Hallazgo(
                ERROR, "Numeración de capítulos", numero + 1, extracto(linea),
                f"Este capítulo debería ser el {correcto}."))
        if esperado < len(CAPITULOS_DEL_PROTOCOLO) and \
                sin_tildes(CAPITULOS_DEL_PROTOCOLO[esperado]) not in sin_tildes(titulo):
            hallazgos.append(Hallazgo(
                ADVERTENCIA, "Orden del protocolo", numero + 1, extracto(linea),
                f"El protocolo pone en este lugar «{CAPITULOS_DEL_PROTOCOLO[esperado]}»."))
        esperado += 1
    if esperado and esperado < len(CAPITULOS_DEL_PROTOCOLO):
        faltan = ", ".join(CAPITULOS_DEL_PROTOCOLO[esperado:])
        hallazgos.append(Hallazgo(ERROR, "Capítulos faltantes", 0, faltan,
                                  "Agregar los capítulos que exige el protocolo."))
    return hallazgos


def revisar_numeracion(informe, tipo):
    """Tablas o figuras: numeradas en orden, citadas en el texto y con su nota."""
    hallazgos = []
    rotulo = re.compile(rf"^{tipo}\s*(\d*)\s*\.", re.IGNORECASE)
    numeros = []
    for numero, linea in informe.cuerpo():
        coincidencia = rotulo.match(linea)
        if not coincidencia:
            continue
        if not coincidencia.group(1):
            hallazgos.append(Hallazgo(ERROR, f"{tipo} sin número", numero + 1,
                                      extracto(linea), f"Numerar la {tipo.lower()}."))
            continue
        valor = int(coincidencia.group(1))
        esperado = (numeros[-1][0] + 1) if numeros else 1
        if valor != esperado:
            hallazgos.append(Hallazgo(
                ERROR, f"Numeración de {tipo.lower()}s", numero + 1, extracto(linea),
                f"Se esperaba la {tipo} {esperado}: renumerar y actualizar el índice."))
        numeros.append((valor, numero))
        siguientes = " ".join(informe.lineas[numero + 1: numero + 40])
        if not re.search(r"\bNota\.", siguientes):
            hallazgos.append(Hallazgo(
                ADVERTENCIA, f"{tipo} sin nota", numero + 1, extracto(linea),
                "Agregar debajo la nota en cursiva: «Nota. Elaboración propia…» (APA 7)."))
    texto = "\n".join(texto for _, texto in informe.cuerpo() if not rotulo.match(texto))
    for valor, numero in numeros:
        if not re.search(rf"\b{tipo}s?\s+(\d+\s*(a|y|,)\s*)*{valor}\b", texto, re.I):
            hallazgos.append(Hallazgo(
                ADVERTENCIA, f"{tipo} no citada", numero + 1, f"{tipo} {valor}",
                f"Mencionar la {tipo.lower()} en el texto antes de que aparezca."))
    return hallazgos


CITA = re.compile(
    r"\(([^()]*?(?:\d{4}[a-z]?|s\.\s?f\.)[^()]*?)\)"
    r"|([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ.\-]+(?:\s(?:et al\.|y\s[A-ZÁÉÍÓÚÑ]\w+))?)"
    r"\s\((\d{4}[a-z]?|s\.\s?f\.)\)"
)


def autor_clave(texto):
    """Normaliza el autor de una cita o entrada para poder compararlos."""
    texto = re.sub(r"\[[^\]]*\]", "", texto)
    texto = re.sub(r"\bet al\.?", "", texto)
    texto = sin_tildes(texto).replace(",", " ").replace(".", " ")
    palabras = [p for p in texto.split() if p not in {"Y", "&", "DE", "DEL", "LA", "EL"}]
    return palabras[0] if palabras else ""


def es_autor(texto):
    """Descarta paréntesis que tienen un año pero no son citas (fechas, medidas)."""
    return bool(texto) and texto[0].isupper() and not re.search(r"[\d:=/]", texto)


def alias_del_texto(informe):
    """Siglas definidas al citar, como «International Organization for Standardization [ISO]»."""
    alias = {}
    for _, linea in informe.cuerpo():
        for nombre, sigla in re.findall(r"([A-ZÁÉÍÓÚ][\w ]+?)\s\[(\w+)\]", linea):
            alias[sin_tildes(sigla)] = autor_clave(nombre)
    return alias


def citas_del_texto(informe):
    """Pares (autor, año) citados en el cuerpo, con la línea de la primera cita."""
    citas = {}
    for numero, linea in informe.cuerpo():
        for coincidencia in CITA.finditer(linea):
            if coincidencia.group(1):
                partes = re.split(r";", coincidencia.group(1))
                for parte in partes:
                    anio = re.search(r"(\d{4}[a-z]?|s\.\s?f\.)", parte)
                    if not anio or len(parte) > 120:
                        continue
                    autor = parte[: anio.start()].strip(" ,")
                    autor = re.sub(r"^(ver|véase|según)\s+", "", autor, flags=re.I)
                    if not es_autor(autor) or not re.match(r"(19|20)\d\d|s\.", anio.group(1)):
                        continue
                    citas.setdefault((autor_clave(autor), anio.group(1).replace(" ", "")),
                                     (numero, autor))
            else:
                citas.setdefault((autor_clave(coincidencia.group(2)),
                                  coincidencia.group(3).replace(" ", "")),
                                 (numero, coincidencia.group(2)))
    return citas


def entradas_de_bibliografia(informe):
    """Pares (autor, año) de cada entrada de la bibliografía."""
    entradas = {}
    alias = {}
    for numero, linea in informe.bibliografia():
        coincidencia = re.match(r"^(.+?)\s\((\d{4}[a-z]?|s\.\s?f\.)", linea)
        if not coincidencia:
            continue
        autor, anio = coincidencia.groups()
        clave = (autor_clave(autor), anio.replace(" ", ""))
        entradas[clave] = (numero, linea)
    return entradas, alias


def revisar_citas(informe):
    """Toda cita tiene su entrada en la bibliografía y toda entrada se cita."""
    hallazgos = []
    citas = {}
    alias = alias_del_texto(informe)
    for (autor, anio), datos in citas_del_texto(informe).items():
        citas.setdefault((alias.get(autor, autor), anio), datos)
    entradas, _ = entradas_de_bibliografia(informe)
    autores_completos = {clave: sin_tildes(linea.split("(")[0])
                         for clave, (_, linea) in entradas.items()}
    texto_cuerpo = sin_tildes(" ".join(texto for _, texto in informe.cuerpo()))
    for (autor, anio), (numero, original) in sorted(citas.items(), key=lambda c: c[1][0]):
        if (autor, anio) in entradas or any(
                anio == a and re.search(rf"\b{re.escape(autor)}\b", autores_completos[(au, a)])
                for (au, a) in entradas):
            continue
        mismo_autor = [a for (au, a) in entradas if au == autor]
        detalle = (f"En la bibliografía «{original}» figura con el año "
                   f"{', '.join(mismo_autor)}: unificar." if mismo_autor else
                   "Agregar la entrada a la bibliografía (APA 7) o corregir la cita.")
        hallazgos.append(Hallazgo(ERROR, "Cita sin entrada en la bibliografía",
                                  numero + 1, f"({original}, {anio})", detalle))
    for (autor, anio), (numero, linea) in entradas.items():
        citada = (autor, anio) in citas or (autor and autor in texto_cuerpo and anio
                                            in texto_cuerpo)
        if not citada:
            hallazgos.append(Hallazgo(
                ADVERTENCIA, "Entrada de la bibliografía sin citar", numero + 1,
                extracto(linea, 90), "Citarla en el texto o quitarla (APA 7)."))
    return hallazgos + revisar_formato_bibliografia(informe)


def revisar_formato_bibliografia(informe):
    """Orden alfabético, letras de año y conector de autores (APA 7)."""
    hallazgos = []
    anterior = ""
    for numero, linea in informe.bibliografia():
        actual = sin_tildes(linea)
        if anterior and actual < anterior and re.match(r"^\S", linea):
            hallazgos.append(Hallazgo(
                ADVERTENCIA, "Bibliografía fuera de orden", numero + 1,
                extracto(linea, 70), "Ordenar alfabéticamente por autor (APA 7)."))
        anterior = actual
        if re.search(r"\(\d{4}[a-z]\)", linea):
            letra = re.search(r"\((\d{4})([a-z])\)", linea)
            hermanas = [otra for _, otra in informe.bibliografia()
                        if f"({letra.group(1)}" in otra and autor_clave(otra) == autor_clave(linea)]
            if len(hermanas) < 2:
                hallazgos.append(Hallazgo(
                    ADVERTENCIA, "Letra de año sin pareja", numero + 1, extracto(linea, 70),
                    "La letra (2026a, 2026b) solo se usa si hay dos obras del mismo autor y año."))
        if " & " in linea:
            hallazgos.append(Hallazgo(SUGERENCIA, "Conector de autores", numero + 1,
                                      extracto(linea, 70),
                                      "En una bibliografía en español, «y» en lugar de «&»."))
    return hallazgos


def revisar_listas(informe):
    """El informe va en prosa: no lleva viñetas ni listas numeradas en el cuerpo."""
    hallazgos = []
    for numero, linea in informe.cuerpo():
        original = informe.originales[numero]
        if re.match(r"^\s*([-*•]|\d+[.)])\s+\S", original) and not informe.es_tabla(numero):
            hallazgos.append(Hallazgo(
                ADVERTENCIA, "Lista con viñetas", numero + 1, extracto(linea),
                "Pasar la lista a texto corrido (enumeración en una oración)."))
    return hallazgos


def revisar_redaccion(informe):
    """Tiempo verbal, veredictos, términos, marcadores y formato de números."""
    hallazgos = []
    for numero, linea in informe.cuerpo():
        if not linea or informe.es_titulo(numero):
            continue
        sin_citas = re.sub(r"«[^»]*»|\"[^\"]*\"", "", linea)
        if not informe.es_tabla(numero) and not linea.startswith("Nota."):
            for verbo in sorted({m.group(0) for m in PRETERITO.finditer(sin_citas)}):
                hallazgos.append(Hallazgo(
                    ADVERTENCIA, "Tiempo verbal", numero + 1, extracto(linea),
                    f"«{verbo}» está en pasado: el informe se redacta en presente "
                    "(«se realiza»), salvo un hecho externo fechado."))
        for patron in VEREDICTOS:
            if re.search(patron, sin_citas, re.IGNORECASE):
                hallazgos.append(Hallazgo(
                    ERROR, "Redacción de veredicto", numero + 1, extracto(linea),
                    "El sistema informa indicios, nunca veredictos (RN27): reformular."))
        for patron, correcto in TERMINOS.items():
            if re.search(patron, linea):
                hallazgos.append(Hallazgo(ADVERTENCIA, "Término", numero + 1,
                                          extracto(linea), f"Usar {correcto}."))
        for palabra in EXTRANJERISMOS:
            if re.search(rf"(?<![*\w]){palabra}(?![*\w])", informe.originales[numero]):
                hallazgos.append(Hallazgo(SUGERENCIA, "Extranjerismo", numero + 1, extracto(linea),
                                          f"«{palabra}» va en cursiva (extranjerismo)."))
        if MARCADORES.search(informe.originales[numero]):
            hallazgos.append(Hallazgo(ERROR, "Marcador sin completar", numero + 1,
                                      extracto(linea), "Completar el dato antes de entregar."))
    return hallazgos + revisar_numeros(informe)


def revisar_numeros(informe):
    """Formato de números, porcentajes y espacios."""
    hallazgos = []
    for numero, linea in informe.cuerpo():
        if not linea or informe.es_titulo(numero):
            continue
        if re.search(r"\d, \d", linea) and not informe.es_tabla(numero):
            hallazgos.append(Hallazgo(ADVERTENCIA, "Número partido", numero + 1,
                                      extracto(linea), "Sin espacio después de la coma decimal."))
        if re.search(r"\d,\s?\d\s?%|\d%", linea) and re.search(r"\d%", linea):
            hallazgos.append(Hallazgo(SUGERENCIA, "Porcentaje", numero + 1, extracto(linea),
                                      "Espacio entre el número y el signo: «45,5 %»."))
        if re.search(r"(?<![\w.])0\.\d+\b", linea):
            hallazgos.append(Hallazgo(SUGERENCIA, "Separador decimal", numero + 1,
                                      extracto(linea),
                                      "En español, coma decimal (0,85), salvo versiones."))
        if "  " in informe.originales[numero].strip() and not informe.es_tabla(numero):
            hallazgos.append(Hallazgo(SUGERENCIA, "Doble espacio", numero + 1, extracto(linea),
                                      "Dejar un solo espacio."))
    return hallazgos


def revisar_coherencia(informe):
    """Contradicciones conocidas entre partes del informe."""
    hallazgos = []
    cuerpo = " ".join(texto for _, texto in informe.cuerpo())
    if re.search(r"F1[- ]?score", cuerpo) and re.search(r"\bAUC\b", cuerpo):
        hallazgos.append(Hallazgo(
            ADVERTENCIA, "Criterio del clasificador", 0, "F1-score y AUC",
            "OE4, el MVP y el testing deben usar el mismo criterio de aceptación (CP-07)."))
    for numero, linea in informe.cuerpo():
        if re.search(r"Blockchain Federal Argentina|\bBFA\b", linea) and not re.search(
                r"reemplaz|migr|original|descart|falla|inicial|propuest|evalu|plan", linea, re.I):
            hallazgos.append(Hallazgo(
                ADVERTENCIA, "Proveedor del sello", numero + 1, extracto(linea),
                "El sello se registra en Hedera: BFA solo se menciona como antecedente."))
    resumen = []
    for numero in range(informe.inicio_cuerpo + 1, len(informe.lineas)):
        if informe.originales[numero].lstrip().startswith("#") or "?tab=" in \
                informe.originales[numero] or informe.lineas[numero].lower() == "índice":
            break
        resumen.append(informe.lineas[numero])
    palabras = len(" ".join(resumen).split())
    if palabras > 350:
        hallazgos.append(Hallazgo(
            ADVERTENCIA, "Extensión del resumen", informe.inicio_cuerpo + 1,
            f"{palabras} palabras", "Un resumen académico ronda las 150 a 300 palabras."))
    return hallazgos


REVISIONES = [revisar_secciones_vacias, revisar_duplicados, revisar_capitulos,
              lambda i: revisar_numeracion(i, "Tabla"),
              lambda i: revisar_numeracion(i, "Figura"),
              revisar_citas, revisar_listas, revisar_redaccion, revisar_coherencia]


def revisar(texto):
    """Aplica todas las revisiones y devuelve los hallazgos ordenados."""
    informe = Informe(texto)
    hallazgos = []
    for revision in REVISIONES:
        hallazgos.extend(revision(informe))
    return sorted(hallazgos, key=lambda h: (ORDEN_SEVERIDAD[h.severidad], h.linea))


def a_markdown(hallazgos):
    """Arma el informe de revisión en Markdown, agrupado por severidad."""
    partes = ["# Revisión automática del informe", ""]
    resumen = {s: sum(1 for h in hallazgos if h.severidad == s) for s in ORDEN_SEVERIDAD}
    partes.append(f"Errores: {resumen[ERROR]} · Advertencias: {resumen[ADVERTENCIA]} · "
                  f"Sugerencias: {resumen[SUGERENCIA]}")
    for severidad in ORDEN_SEVERIDAD:
        grupo = [h for h in hallazgos if h.severidad == severidad]
        if not grupo:
            continue
        partes += ["", f"## {severidad.capitalize()}es" if severidad == ERROR
                   else f"## {severidad.capitalize()}s", "",
                   "| Línea | Regla | Texto | Corrección |", "|---|---|---|---|"]
        for h in grupo:
            texto = h.texto.replace("|", "\\|")
            partes.append(f"| {h.linea or '—'} | {h.regla} | {texto} | {h.correccion} |")
    return "\n".join(partes) + "\n"


def main(argumentos=None):
    """Punto de entrada por línea de comandos."""
    analizador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analizador.add_argument("archivo", type=Path, help="Texto del informe (.txt o .md)")
    analizador.add_argument("--json", action="store_true", help="Salida en JSON")
    analizador.add_argument("--salida", type=Path, help="Guardar la revisión en un archivo")
    opciones = analizador.parse_args(argumentos)
    hallazgos = revisar(opciones.archivo.read_text(encoding="utf-8"))
    salida = (json.dumps([asdict(h) for h in hallazgos], ensure_ascii=False, indent=2)
              if opciones.json else a_markdown(hallazgos))
    if opciones.salida:
        opciones.salida.write_text(salida, encoding="utf-8")
    else:
        sys.stdout.write(salida)
    return 1 if any(h.severidad == ERROR for h in hallazgos) else 0


if __name__ == "__main__":
    sys.exit(main())
