"""Diagnóstico de qué llega al servidor cuando se sube una foto (funcionalidad 047).

Según el camino que use la persona (la galería, la cámara o la app Archivos del
iPhone, o la galería de Android), el celular puede entregar la foto convertida
y sin metadatos. No hay información confiable de qué hace cada versión de iOS,
así que se mide: este servicio lee una foto y devuelve qué trae, sin guardarla.

Lo usa la página pública «Probar mi celular» y alimenta la decisión del camino
recomendado para subir fotos desde el iPhone.

Realiza: CA1 de la funcionalidad 047; RF39 (metadatos), RN22 (formatos).
"""
from app.analisis.base import CapaNoDisponible
from app.analisis.metadatos import CapaMetadatos
from app.servicios.errores import ErrorValidacion
from app.utilidades.imagenes import detectar_formato

NOMBRES_FORMATO = {"jpeg": "JPEG", "png": "PNG", "heic": "HEIC (formato del iPhone)"}
CLAVES_GPS = ("GPSLatitude", "GPSPosition", "Composite:GPSLatitude")
CLAVES_FECHA = ("DateTimeOriginal", "CreateDate")


def describir_navegador(agente):
    """Sistema y navegador a partir del *User-Agent*, sin guardar el texto completo."""
    agente = agente or ""
    if "iPhone" in agente or "iPad" in agente:
        sistema = "iPhone o iPad"
        if "OS " in agente:
            version = agente.split("OS ", 1)[1].split(" ", 1)[0].replace("_", ".")
            sistema = f"{sistema} (iOS {version})"
    elif "Android" in agente:
        sistema = "Android"
    elif "Windows" in agente:
        sistema = "Windows"
    elif "Mac OS" in agente:
        sistema = "Mac"
    else:
        sistema = "otro"
    if "CriOS" in agente or ("Chrome" in agente and "Edg" not in agente):
        navegador = "Chrome"
    elif "FxiOS" in agente or "Firefox" in agente:
        navegador = "Firefox"
    elif "Edg" in agente:
        navegador = "Edge"
    elif "Safari" in agente:
        navegador = "Safari"
    else:
        navegador = "otro"
    return {"sistema": sistema, "navegador": navegador}


def _primero(datos, claves):
    for clave in claves:
        if datos.get(clave) not in (None, ""):
            return str(datos[clave])
    return None


class ServicioDiagnostico:
    """Lee una foto subida y describe lo que trae, sin guardarla."""

    def __init__(self, capa_metadatos, tamanio_maximo):
        """
        Args:
            capa_metadatos: ``CapaMetadatos`` (usa su lector de ExifTool).
            tamanio_maximo: tamaño máximo aceptado en bytes (RN22).
        """
        self.capa_metadatos = capa_metadatos
        self.tamanio_maximo = tamanio_maximo

    def diagnosticar(self, contenido, agente=None):
        """Describe qué llegó: formato, metadatos, cámara, fecha y ubicación.

        Raises:
            ErrorValidacion: si no llegó un archivo, es muy grande o no es una
                imagen JPEG, PNG o HEIC.
        """
        if not contenido:
            raise ErrorValidacion("Elegí una foto para probar.")
        if len(contenido) > self.tamanio_maximo:
            raise ErrorValidacion("La foto supera el tamaño máximo permitido.")
        formato = detectar_formato(contenido)
        if formato is None:
            raise ErrorValidacion("El archivo no es una imagen JPEG, PNG o HEIC.")
        try:
            datos = self.capa_metadatos.extraer(contenido)
            leidos = True
        except CapaNoDisponible:
            datos, leidos = {}, False
        exif = [clave for clave in datos if clave.startswith("EXIF:")]
        return {
            "formato": NOMBRES_FORMATO[formato],
            "es_heic": formato == "heic",
            "tamanio_kb": round(len(contenido) / 1024),
            "metadatos_leidos": leidos,
            "campos_exif": len(exif),
            "marca": _primero(datos, ("Make",)),
            "modelo": _primero(datos, ("Model",)),
            "programa": _primero(datos, ("Software",)),
            "fecha_captura": _primero(datos, CLAVES_FECHA),
            "tiene_ubicacion": _primero(datos, CLAVES_GPS) is not None,
            "dispositivo": describir_navegador(agente),
        }


def crear_capa_para_diagnostico(configuracion):
    """La misma capa de metadatos que usa el análisis, con el ExifTool configurado."""
    return CapaMetadatos(configuracion["RUTA_EXIFTOOL"])
