"""Descarga del catálogo de aseguradoras de la SSN desde los datos abiertos (052).

La Superintendencia de Seguros de la Nación publica «Entidades aseguradoras y
reaseguradoras activas» en el portal nacional de datos abiertos (CKAN, licencia
CC-BY-4.0). Primero se consulta el conjunto de datos con la API de CKAN
(``package_show``), que dice dónde está hoy el CSV y cuándo se actualizó, y
recién después se baja el archivo: si la SSN lo publica en otra dirección, la
tarea sigue funcionando.

Realiza: RN36, RN37 (CP-18); 052.
"""
import json
from urllib import error, request

URL_PAQUETE = (
    "https://datos.gob.ar/api/3/action/package_show?id=entidades-aseguradoras-y-reaseguradoras"
)
TIEMPO_ESPERA = 30  # segundos
TAMANIO_MAXIMO = 2 * 1024 * 1024  # el archivo pesa ~32 kB; más de 2 MB no es el esperado
NOMBRE_ARCHIVO = "entidades-activas"


class FuenteSsnNoDisponible(Exception):
    """El portal de datos abiertos no respondió o no trae el CSV esperado."""


class FuenteSsn:
    """Lee el CSV vigente de entidades activas de la SSN."""

    def __init__(self, url_paquete=URL_PAQUETE, tiempo_espera=TIEMPO_ESPERA):
        self.url_paquete = url_paquete
        self.tiempo_espera = tiempo_espera

    def _leer(self, url):
        solicitud = request.Request(url, headers={"User-Agent": "evidentIA-catalogo/1.0"})
        try:
            with request.urlopen(solicitud, timeout=self.tiempo_espera) as respuesta:
                contenido = respuesta.read(TAMANIO_MAXIMO + 1)
        except (error.URLError, TimeoutError) as falla:
            raise FuenteSsnNoDisponible(f"No respondió {url}: {falla}") from falla
        if len(contenido) > TAMANIO_MAXIMO:
            raise FuenteSsnNoDisponible(f"El archivo de {url} supera {TAMANIO_MAXIMO} bytes.")
        return contenido

    def recurso_vigente(self):
        """Dirección y fecha de actualización del CSV de entidades activas."""
        try:
            paquete = json.loads(self._leer(self.url_paquete))["result"]
        except (ValueError, KeyError) as falla:
            raise FuenteSsnNoDisponible(
                "La respuesta de datos.gob.ar no es la esperada."
            ) from falla
        csvs = [r for r in paquete.get("resources", []) if (r.get("format") or "").upper() == "CSV"]
        elegido = next((r for r in csvs if NOMBRE_ARCHIVO in (r.get("url") or "")), None)
        elegido = elegido or (csvs[0] if csvs else None)
        if not elegido or not (elegido.get("url") or "").startswith("https://"):
            raise FuenteSsnNoDisponible("El conjunto de datos no trae un CSV por HTTPS.")
        return {
            "url": elegido["url"],
            "actualizado": elegido.get("last_modified") or paquete.get("metadata_modified"),
        }

    def descargar(self):
        """Devuelve ``(contenido, recurso)``: los bytes del CSV y de dónde y cuándo es."""
        recurso = self.recurso_vigente()
        return self._leer(recurso["url"]), recurso
