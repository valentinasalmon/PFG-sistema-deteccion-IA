"""Capa 2: credenciales de contenido C2PA, con verificación de la firma.

Lee el manifiesto C2PA con c2pa-python y verifica su firma contra la lista de
confianza oficial del consorcio, guardada en ``recursos/confianza_c2pa``. Toma
del repositorio anterior (``valentinasalmon/TIF``) la interpretación del
origen digital IPTC de ``c2pa_service.py`` y la clasificación de las fallas de
``probar_c2pa_firma.py``; la revisión completa está en
``docs/funcionalidades/009-capa-c2pa/plan.md``.

La capa trabaja con los bytes en memoria, no descarga nada durante el análisis
(ni la lista de confianza, ni revocaciones, ni credenciales remotas) y no
accede a la base de datos.

Realiza: RF40 (CA1 a CA4), RF43 (CA1, CA2); RN26, RN27, RN28, RN29.
"""
import hashlib
import io
import json
from datetime import datetime, timezone
from functools import lru_cache
from importlib import metadata
from pathlib import Path

from app.analisis.base import (
    NIVEL_MAXIMO,
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
    anomalias_principales,
    calcular_nivel,
    describir_intensidad,
    texto_acotado,
)

try:
    import c2pa
except ImportError:  # pragma: no cover - se informa como capa no disponible
    c2pa = None

VERSION_CAPA = "1.0"
CARPETA_CONFIANZA = Path(__file__).resolve().parents[2] / "recursos" / "confianza_c2pa"
ARCHIVOS_CONFIANZA = ("C2PA-TRUST-LIST.pem", "C2PA-TSA-TRUST-LIST.pem")

# Usos extendidos de clave (EKU) aceptados en los certificados de firma, los
# mismos que configura el validador de referencia de C2PA. Sin esta lista,
# c2pa-python rechaza todo certificado con "certificate missing required EKU":
# esa fue la causa de que la sonda del TIF informara la firma de OpenAI como
# no confiable.
USOS_DE_CLAVE_ACEPTADOS = "\n".join((
    "1.3.6.1.4.1.62558.2.1",  # c2pa-kp-claimSigning
    "1.3.6.1.5.5.7.3.36",  # id-kp-documentSigning
    "1.3.6.1.5.5.7.3.4",  # id-kp-emailProtection
    "1.3.6.1.5.5.7.3.8",  # id-kp-timeStamping
    "1.3.6.1.5.5.7.3.9",  # id-kp-OCSPSigning
    "1.3.6.1.4.1.311.76.59.1.9",  # Microsoft C2PA Signing
)) + "\n"

TIPOS_MIME = {"jpeg": "image/jpeg", "png": "image/png"}

# --- Estado de la firma ---

FIRMA_CONFIABLE = "confiable"
FIRMA_NO_RECONOCIDA = "firmante_no_reconocido"
FIRMA_CONTENIDO_MODIFICADO = "contenido_modificado"
FIRMA_INVALIDA = "firma_invalida"
NOMBRES_ESTADO_FIRMA = {
    FIRMA_CONFIABLE: "Confiable: firma válida de un firmante de la lista de confianza de C2PA",
    FIRMA_NO_RECONOCIDA: "Firmante no reconocido: firma válida, fuera de la lista de confianza",
    FIRMA_CONTENIDO_MODIFICADO: "Archivo modificado después de firmarse",
    FIRMA_INVALIDA: "No válidas: la firma o el manifiesto no superan la validación",
}
CODIGOS_DE_CONFIANZA = ("signingCredential.untrusted",)
# Fallas que indican que la imagen o el manifiesto cambiaron después de firmarse.
MARCAS_DE_CONTENIDO_MODIFICADO = ("mismatch", "hashedURI")
EXPLICACIONES = {
    "signingCredential.untrusted":
        "el certificado del firmante no pertenece a la lista de confianza de C2PA",
    "signingCredential.invalid": "el certificado del firmante no es válido para firmar",
    "signingCredential.expired": "el certificado del firmante estaba vencido al firmar",
    "signingCredential.revoked": "el certificado del firmante fue revocado",
    "claimSignature.mismatch": "la firma no corresponde al contenido del manifiesto",
    "claimSignature.missing": "el manifiesto no tiene firma",
    "claimSignature.outsideValidity":
        "la firma se hizo fuera del período de validez del certificado",
    "assertion.dataHash.mismatch": "la imagen cambió después de firmarse",
    "assertion.hashedURI.mismatch": "una declaración del manifiesto cambió después de firmarse",
    "assertion.action.ingredientMismatch":
        "una acción registrada no coincide con los ingredientes del manifiesto",
}

# --- Origen digital (vocabulario IPTC) ---

ORIGENES = {
    "trainedalgorithmicmedia": "generada por un modelo de inteligencia artificial",
    "compositewithtrainedalgorithmicmedia":
        "compuesta con elementos generados por inteligencia artificial",
    "algorithmicmedia": "creada por un algoritmo, sin captura de una cámara",
    "compositesynthetic": "compuesta con elementos sintéticos",
    "digitalcapture": "captura de una cámara digital",
    "computationalcapture": "captura de un teléfono con procesamiento computacional",
    "negativefilm": "digitalización de un negativo fotográfico",
    "positivefilm": "digitalización de una diapositiva",
    "print": "digitalización de una copia impresa",
    "humanedits": "editada por una persona",
    "minorhumanedits": "con ediciones menores de una persona",
    "algorithmicallyenhanced": "mejorada por un algoritmo",
    "compositecapture": "compuesta con varias capturas",
    "screencapture": "captura de pantalla",
    "digitalcreation": "creada digitalmente por una persona",
    "datadrivenmedia": "generada a partir de datos",
    "virtualrecording": "grabación de un entorno virtual",
}
# Orígenes que declaran generación por IA: con firma confiable, nivel máximo (RN28).
ORIGENES_IA = ("trainedalgorithmicmedia", "compositewithtrainedalgorithmicmedia")
ORIGENES_SINTETICOS = (*ORIGENES_IA, "algorithmicmedia", "compositesynthetic")

# --- Acciones registradas ---

ACCIONES = {
    "c2pa.created": "creación",
    "c2pa.opened": "apertura",
    "c2pa.edited": "edición",
    "c2pa.edited.metadata": "edición de metadatos",
    "c2pa.converted": "conversión de formato",
    "c2pa.transcoded": "recodificación",
    "c2pa.repackaged": "reempaquetado",
    "c2pa.resized": "cambio de tamaño",
    "c2pa.cropped": "recorte",
    "c2pa.filtered": "filtro",
    "c2pa.color_adjustments": "ajuste de color",
    "c2pa.drawing": "dibujo",
    "c2pa.placed": "inserción de contenido",
    "c2pa.removed": "eliminación de contenido",
    "c2pa.watermarked": "marca de agua",
    "c2pa.watermarked.bound": "marca de agua",
    "c2pa.watermarked.unbound": "marca de agua",
    "c2pa.published": "publicación",
}
# Acciones que modifican lo que muestra la imagen (no solo su formato o tamaño).
ACCIONES_DE_EDICION = (
    "c2pa.edited", "c2pa.cropped", "c2pa.filtered", "c2pa.color_adjustments",
    "c2pa.drawing", "c2pa.placed", "c2pa.removed",
)

# Severidad de cada hallazgo según el estado de la firma (plan de la 009).
SEVERIDADES = {
    FIRMA_CONFIABLE: {"ia": SEVERIDAD_DIRECTO, "edicion": SEVERIDAD_FUERTE},
    FIRMA_NO_RECONOCIDA: {
        "ia": SEVERIDAD_FUERTE, "edicion": SEVERIDAD_MODERADO, "firma": SEVERIDAD_DEBIL,
    },
    FIRMA_CONTENIDO_MODIFICADO: {
        "ia": SEVERIDAD_MODERADO, "edicion": SEVERIDAD_DEBIL, "firma": SEVERIDAD_MODERADO,
    },
    FIRMA_INVALIDA: {
        "ia": SEVERIDAD_MODERADO, "edicion": SEVERIDAD_DEBIL, "firma": SEVERIDAD_MODERADO,
    },
}
ACLARACIONES = {
    FIRMA_CONFIABLE: "La firma es válida y el firmante está en la lista de confianza de C2PA.",
    FIRMA_NO_RECONOCIDA: (
        "La firma es válida, pero el firmante no está en la lista de confianza de C2PA: "
        "no se puede confirmar quién la emitió."
    ),
    FIRMA_CONTENIDO_MODIFICADO: (
        "El archivo cambió después de firmarse, así que la declaración no se puede "
        "atribuir con certeza a esta imagen."
    ),
    FIRMA_INVALIDA: (
        "Las credenciales no superan la validación, así que la declaración no se puede "
        "confirmar."
    ),
}

SIN_CREDENCIALES = (
    "Sin credenciales de contenido. La imagen no tiene un manifiesto C2PA. La mayoría "
    "de las fotos de teléfonos y cámaras todavía no lo incluye, y las aplicaciones de "
    "mensajería y las capturas de pantalla lo eliminan, por lo que su ausencia no "
    "constituye evidencia de autenticidad ni de manipulación."
)


class ManifiestoIlegible(Exception):
    """La imagen tiene credenciales C2PA que c2pa-python no puede leer."""


@lru_cache(maxsize=4)
def _leer_lista_de_confianza(carpeta):
    """Certificados de la lista de confianza y su versión (huella abreviada).

    Raises:
        CapaNoDisponible: si falta algún archivo de la lista.
    """
    textos, versiones = [], []
    for nombre in ARCHIVOS_CONFIANZA:
        ruta = Path(carpeta) / nombre
        try:
            contenido = ruta.read_bytes()
        except OSError as error:
            raise CapaNoDisponible(
                "No se encontró la lista de confianza de C2PA en el servidor de análisis."
            ) from error
        textos.append(contenido.decode("utf-8"))
        versiones.append(hashlib.sha256(contenido).hexdigest()[:12])
    return "\n".join(textos), "/".join(versiones)


def _version_c2pa_python():
    """Versión instalada de c2pa-python, o None si no está disponible."""
    try:
        return metadata.version("c2pa-python")
    except metadata.PackageNotFoundError:
        return None


def _fecha_de_firma(valor):
    """Fecha ISO de la firma como ``28/09/2026 18:20:55 UTC``; si no se entiende, tal cual."""
    try:
        fecha = datetime.fromisoformat(str(valor))
    except ValueError:
        return str(valor or "")
    if fecha.tzinfo is not None:
        fecha = fecha.astimezone(timezone.utc)
    return fecha.strftime("%d/%m/%Y %H:%M:%S UTC")


def _nombre_de_agente(agente):
    """Nombre y versión de un ``softwareAgent`` (texto o diccionario)."""
    if isinstance(agente, dict):
        partes = (agente.get("name"), agente.get("version"))
        return " ".join(str(p) for p in partes if p)
    return str(agente or "")


def _clave_de_origen(valor):
    """``http://cv.iptc.org/.../trainedAlgorithmicMedia`` → ``trainedalgorithmicmedia``."""
    return str(valor or "").rstrip("/").rsplit("/", 1)[-1].lower()


def _unicos(valores):
    """Valores no vacíos sin repetir, en su orden de aparición."""
    return list(dict.fromkeys(v for v in valores if v))


class CapaC2PA(CapaAnalisis):
    """Verifica las credenciales de contenido C2PA de la imagen (capa 2)."""

    nombre = "c2pa"
    titulo = "Credenciales de contenido"

    def __init__(self, carpeta_confianza=CARPETA_CONFIANZA):
        self.carpeta_confianza = str(carpeta_confianza)
        self._contexto = None

    def version(self):
        """Versión de la capa, de c2pa-python y de la lista de confianza (RN29)."""
        biblioteca = _version_c2pa_python() or "no disponible"
        try:
            _, lista = _leer_lista_de_confianza(self.carpeta_confianza)
        except CapaNoDisponible:
            lista = "no disponible"
        return f"{VERSION_CAPA} (c2pa-python {biblioteca}, lista de confianza {lista})"

    # --- Lectura ---

    def contexto(self):
        """Contexto de validación de c2pa-python, creado una sola vez por capa.

        Raises:
            CapaNoDisponible: si falta la biblioteca o la lista de confianza.
        """
        if c2pa is None:
            raise CapaNoDisponible(
                "La biblioteca c2pa-python no está instalada en el servidor de análisis."
            )
        if self._contexto is None:
            certificados, _ = _leer_lista_de_confianza(self.carpeta_confianza)
            self._contexto = c2pa.Context(c2pa.Settings.from_dict({
                "trust": {
                    "trust_anchors": certificados,
                    "trust_config": USOS_DE_CLAVE_ACEPTADOS,
                },
                "verify": {
                    "verify_trust": True,
                    "verify_timestamp_trust": True,
                    "ocsp_fetch": False,
                    "remote_manifest_fetch": False,
                },
            }))
        return self._contexto

    def leer(self, contenido, formato):
        """Manifiesto activo y validación, o None si la imagen no tiene credenciales.

        Returns:
            dict con ``estado`` (Trusted, Valid o Invalid), ``manifiesto`` (el
            manifiesto activo) y ``validacion`` (resultados del manifiesto activo).

        Raises:
            CapaNoDisponible: si falta la biblioteca o la lista de confianza.
            ManifiestoIlegible: si hay credenciales pero no se pueden leer.
        """
        contexto = self.contexto()
        try:
            with c2pa.Reader(
                TIPOS_MIME.get(formato, f"image/{formato}"), io.BytesIO(contenido),
                context=contexto,
            ) as lector:
                estado = str(lector.get_validation_state())
                validacion = (lector.get_validation_results() or {}).get("activeManifest", {})
                almacen = json.loads(lector.json())
        except c2pa.C2paError.ManifestNotFound:
            return None
        except c2pa.C2paError as error:
            raise ManifiestoIlegible(str(error)) from error
        manifiesto = almacen.get("manifests", {}).get(almacen.get("active_manifest"), {})
        return {"estado": estado, "manifiesto": manifiesto, "validacion": validacion}

    # --- Interpretación (funciones puras sobre lo leído) ---

    @staticmethod
    def estado_de_la_firma(estado, validacion):
        """Uno de los cuatro estados de la firma, a partir de las fallas informadas."""
        codigos = [f.get("code", "") for f in validacion.get("failure", [])]
        if estado == "Trusted" and not codigos:
            return FIRMA_CONFIABLE
        if any(m in c for c in codigos for m in MARCAS_DE_CONTENIDO_MODIFICADO):
            return FIRMA_CONTENIDO_MODIFICADO
        if any(c not in CODIGOS_DE_CONFIANZA for c in codigos):
            return FIRMA_INVALIDA
        return FIRMA_NO_RECONOCIDA

    @staticmethod
    def acciones(manifiesto):
        """Acciones registradas en las declaraciones ``c2pa.actions`` del manifiesto."""
        encontradas = []
        for asercion in manifiesto.get("assertions", []):
            if not str(asercion.get("label", "")).startswith("c2pa.actions"):
                continue
            datos = asercion.get("data") or {}
            encontradas += [a for a in datos.get("actions", []) if isinstance(a, dict)]
        return encontradas

    @staticmethod
    def datos(lectura):
        """Datos del manifiesto que se informan (RF40 CA4)."""
        manifiesto, validacion = lectura["manifiesto"], lectura["validacion"]
        acciones = CapaC2PA.acciones(manifiesto)
        firma = manifiesto.get("signature_info") or {}
        generadores = manifiesto.get("claim_generator_info") or []
        herramientas = [_nombre_de_agente(g) for g in generadores if isinstance(g, dict)]
        if not herramientas and manifiesto.get("claim_generator"):
            herramientas = [str(manifiesto["claim_generator"])]
        codigos = {
            c.get("code") for clave in ("success", "informational")
            for c in validacion.get(clave, [])
        }
        if "timeStamp.trusted" in codigos:
            sello = "Verificado por una autoridad de la lista de confianza"
        elif "timeStamp.validated" in codigos:
            sello = "Válido, emitido por una autoridad fuera de la lista de confianza"
        else:
            sello = "Sin sello de tiempo verificable"
        return {
            "estado_firma": CapaC2PA.estado_de_la_firma(lectura["estado"], validacion),
            "firmante": " · ".join(_unicos([firma.get("issuer"), firma.get("common_name")])),
            "fecha_firma": _fecha_de_firma(firma["time"]) if firma.get("time") else "",
            "herramientas": _unicos(herramientas),
            "agentes": _unicos(_nombre_de_agente(a.get("softwareAgent")) for a in acciones),
            "origenes": _unicos(_clave_de_origen(a.get("digitalSourceType")) for a in acciones),
            "acciones": _unicos(a.get("action") for a in acciones),
            "sello_de_tiempo": sello,
            "fallas": [
                {"codigo": f.get("code", ""), "explicacion": f.get("explanation", "")}
                for f in validacion.get("failure", [])
            ],
        }

    @staticmethod
    def explicar_fallas(fallas):
        """Fallas de la validación en español, con el código entre paréntesis."""
        return "; ".join(
            f"{EXPLICACIONES.get(f['codigo'], texto_acotado(f['explicacion']))} ({f['codigo']})"
            for f in fallas
        )

    @staticmethod
    def hallazgos(datos):
        """Anomalías según la declaración de origen, las ediciones y la firma."""
        estado = datos["estado_firma"]
        severidades = SEVERIDADES[estado]
        herramienta = ", ".join(datos["agentes"] or datos["herramientas"]) or "no declarada"
        anomalias = []
        sinteticos = [o for o in datos["origenes"] if o in ORIGENES_SINTETICOS]
        if sinteticos:
            origen = sinteticos[0]
            anomalias.append(Anomalia(
                "Origen declarado (C2PA)", origen,
                f"Las credenciales de contenido declaran que la imagen fue {ORIGENES[origen]} "
                f"(herramienta declarada: «{texto_acotado(herramienta)}»). {ACLARACIONES[estado]}",
                severidades["ia"],
            ))
        ediciones = [a for a in datos["acciones"] if a in ACCIONES_DE_EDICION]
        if ediciones:
            nombres = ", ".join(ACCIONES[a] for a in ediciones)
            anomalias.append(Anomalia(
                "Acciones registradas (C2PA)", ", ".join(ediciones),
                f"Las credenciales de contenido registran ediciones de la imagen: {nombres}. "
                f"{ACLARACIONES[estado]}",
                severidades["edicion"],
            ))
        if estado == FIRMA_NO_RECONOCIDA:
            anomalias.append(Anomalia(
                "Firma", texto_acotado(datos["firmante"] or "sin firmante"),
                f"El firmante «{texto_acotado(datos['firmante'] or 'sin nombre')}» no está en "
                "la lista de confianza de C2PA. La firma es válida, pero no se puede confirmar "
                "la identidad de quien la emitió.",
                severidades["firma"],
            ))
        elif estado == FIRMA_CONTENIDO_MODIFICADO:
            anomalias.append(Anomalia(
                "Firma", ", ".join(f["codigo"] for f in datos["fallas"]),
                "La imagen o sus credenciales cambiaron después de firmarse: la firma ya no "
                "coincide con el contenido. Puede deberse a una edición posterior o a "
                "credenciales copiadas de otro archivo. Detalle de la validación: "
                f"{CapaC2PA.explicar_fallas(datos['fallas'])}.",
                severidades["firma"],
            ))
        elif estado == FIRMA_INVALIDA:
            anomalias.append(Anomalia(
                "Firma", ", ".join(f["codigo"] for f in datos["fallas"]),
                "La firma o el manifiesto de las credenciales de contenido no superan la "
                f"validación. Detalle: {CapaC2PA.explicar_fallas(datos['fallas'])}.",
                severidades["firma"],
            ))
        return anomalias

    @staticmethod
    def calcular_nivel(datos, anomalias):
        """100 % si una firma confiable declara IA (RN28); si no, el método común (hasta 90)."""
        declara_ia = any(o in ORIGENES_IA for o in datos["origenes"])
        if datos["estado_firma"] == FIRMA_CONFIABLE and declara_ia:
            return NIVEL_MAXIMO
        return calcular_nivel(anomalias)

    @staticmethod
    def redactar_conclusion(nivel, anomalias, datos):
        """Conclusión redactada como indicio, siempre con la recomendación (RN27)."""
        firmante = texto_acotado(datos["firmante"] or "sin nombre")
        if nivel == NIVEL_MAXIMO:
            origen = next(o for o in datos["origenes"] if o in ORIGENES_IA)
            texto = (
                f"La imagen tiene credenciales de contenido con firma confiable de «{firmante}» "
                f"que declaran que fue {ORIGENES[origen]}. Es el indicio más fuerte que informa "
                "la plataforma: la declaración proviene de la herramienta que generó el archivo "
                "y la firma muestra que la imagen no cambió desde entonces."
            )
        elif nivel == 0:
            texto = (
                f"La imagen tiene credenciales de contenido firmadas por «{firmante}» que no "
                "declaran generación por inteligencia artificial ni ediciones. Las credenciales "
                "describen lo que declaró quien firmó y no descartan modificaciones que no "
                "hayan quedado registradas."
            )
        else:
            principales = anomalias_principales(anomalias)
            intensidad = describir_intensidad(nivel)
            texto = f"Las credenciales de contenido presentan {intensidad}. " + " ".join(
                a.descripcion for a in principales
            )
        return f"{texto} {RECOMENDACION}"

    @staticmethod
    def tabla(datos):
        """Datos de las credenciales para mostrar en el resultado (RF40 CA4)."""
        filas = [
            ("Estado de la firma", NOMBRES_ESTADO_FIRMA[datos["estado_firma"]]),
            ("Firmante", datos["firmante"]),
            ("Fecha de la firma", datos["fecha_firma"]),
            ("Herramienta declarada", ", ".join(datos["herramientas"])),
            ("Agente de software", ", ".join(datos["agentes"])),
            ("Origen declarado", ", ".join(ORIGENES.get(o, o) for o in datos["origenes"])),
            ("Acciones registradas", ", ".join(
                _unicos(ACCIONES.get(a, a) for a in datos["acciones"])
            )),
            ("Sello de tiempo de la firma", datos["sello_de_tiempo"]),
            ("Detalle de la validación", CapaC2PA.explicar_fallas(datos["fallas"])),
        ]
        return [
            {"campo": campo, "valor": texto_acotado(valor)} for campo, valor in filas if valor
        ]

    def analizar(self, contenido, contexto):
        """Lee y verifica las credenciales y arma el resultado de la capa (RF40, RF43)."""
        try:
            lectura = self.leer(contenido, contexto.formato)
        except ManifiestoIlegible as error:
            anomalias = [Anomalia(
                "Manifiesto C2PA", texto_acotado(error),
                "El archivo contiene credenciales de contenido que no se pudieron leer: "
                "pueden estar dañadas o incompletas.",
                SEVERIDAD_MODERADO,
            )]
            nivel = calcular_nivel(anomalias)
            return ResultadoCapa(
                nivel=nivel, anomalias=anomalias,
                conclusion=(
                    "Las credenciales de contenido presentan indicios moderados. "
                    f"{anomalias[0].descripcion} {RECOMENDACION}"
                ),
                detalle={"tabla": [], "sin_credenciales": False, "estado_firma": None},
            )
        if lectura is None:
            return ResultadoCapa(
                nivel=0,
                anomalias=[Anomalia(
                    "Manifiesto C2PA", "ausente", SIN_CREDENCIALES, SEVERIDAD_NEUTRO,
                )],
                conclusion=f"{SIN_CREDENCIALES} {RECOMENDACION}",
                detalle={"tabla": [], "sin_credenciales": True, "estado_firma": None},
            )
        datos = self.datos(lectura)
        anomalias = self.hallazgos(datos)
        nivel = self.calcular_nivel(datos, anomalias)
        return ResultadoCapa(
            nivel=nivel,
            anomalias=anomalias,
            conclusion=self.redactar_conclusion(nivel, anomalias, datos),
            detalle={
                "tabla": self.tabla(datos),
                "sin_credenciales": False,
                "estado_firma": datos["estado_firma"],
            },
        )
