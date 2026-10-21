"""Sello de tiempo de las huellas en Blockchain Federal Argentina (patrón Strategy).

Implementaciones intercambiables con la misma interfaz (RF37 CA4):

- ``SelladorBFA``: el servicio público Sello de Tiempo de BFA
  (https://tsaapi.bfa.ar, el que usa https://bfa.ar/sello). Solo envía la
  huella SHA-256, nunca el archivo (RF37). ``sellar`` hace
  ``POST /api/tsa/stamp/`` con el formulario ``file_hash`` y recibe el recibo
  temporal (``temporary_rd``); cuando BFA incluye la huella en un bloque,
  ``verificar`` (``POST /api/tsa/verify/`` con ``file_hash`` y ``rd``) devuelve
  la confirmación y, si BFA lo entrega, el recibo definitivo.
- ``SelladorSimulado``: desarrollo y pruebas. Responde al instante y marca
  todo como simulado, para que nunca se confunda con un sello real.

Cualquier error de red se informa con ``SelloNoDisponible``: el servicio lo
reintenta después y la carga o el análisis siguen (RF37 CA3, RNF20 CA1).

Realiza: RF37 (CA3, CA4).
"""
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib import error, parse, request

URL_BFA = "https://tsaapi.bfa.ar"
TIEMPO_ESPERA = 10  # segundos por solicitud
# BFA informa la fecha en hora argentina (UTC-3, sin horario de verano), "dd/mm/aaaa hh:mm:ss".
HORA_ARGENTINA = timezone(timedelta(hours=-3))
FORMATO_FECHA_BFA = "%d/%m/%Y %H:%M:%S"


class SelloNoDisponible(Exception):
    """El servicio de sello no respondió o respondió con un error."""


@dataclass
class Confirmacion:
    """Sello confirmado: la referencia de la transacción o bloque y su fecha (RF37 CA2)."""

    referencia: str
    fecha: datetime
    recibo: str | None = None  # recibo definitivo, si el servicio lo entrega


class SelladorBFA:
    """Cliente del servicio de sello de tiempo de Blockchain Federal Argentina."""

    simulado = False

    def __init__(self, url=URL_BFA, tiempo_espera=TIEMPO_ESPERA):
        self.url = url.rstrip("/")
        self.tiempo_espera = tiempo_espera

    def _enviar(self, ruta, datos):
        """POST de ``datos`` como formulario, como lo espera BFA; devuelve el JSON."""
        solicitud = request.Request(
            f"{self.url}{ruta}", data=parse.urlencode(datos).encode(), method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Accept": "application/json"},
        )
        try:
            with request.urlopen(solicitud, timeout=self.tiempo_espera) as respuesta:
                return json.loads(respuesta.read() or b"{}")
        except (error.URLError, TimeoutError, ValueError) as falla:
            raise SelloNoDisponible(f"BFA no respondió: {falla}") from falla

    def sellar(self, huella):
        """Pide el sello de la huella y devuelve el recibo temporal que entrega BFA."""
        respuesta = self._enviar("/api/tsa/stamp/", {"file_hash": huella})
        recibo = respuesta.get("temporary_rd")
        if respuesta.get("status") != "success" or not recibo:
            raise SelloNoDisponible(f"BFA no devolvió un recibo: {respuesta}")
        return recibo

    def verificar(self, huella, recibo):
        """La ``Confirmacion`` si el sello ya está en un bloque; None si sigue pendiente."""
        respuesta = self._enviar("/api/tsa/verify/", {"file_hash": huella, "rd": recibo})
        if respuesta.get("status") != "success":
            return None
        # Respuesta observada el 2026-10-22: {"status", "permanent_rd", "attestation_time":
        # "21/10/2026 18:05:27", "messages": "... fue ingresado en el bloque 50435901 el ..."}.
        datos = {**respuesta, **(respuesta.get("attestation") or {})}
        bloque = datos.get("block") or datos.get("block_number")
        if not bloque:
            encontrado = re.search(r"bloque (\d+)", str(datos.get("messages") or ""))
            bloque = encontrado.group(1) if encontrado else None
        referencia = f"BFA bloque {bloque}" if bloque else "BFA"
        fecha = _fecha_bfa(datos.get("attestation_time") or datos.get("time"))
        return Confirmacion(referencia=referencia, fecha=fecha, recibo=datos.get("permanent_rd"))


def _fecha_bfa(valor):
    """Fecha UTC (sin zona) del sello: acepta segundos Unix o "dd/mm/aaaa hh:mm:ss" de Argentina."""
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    texto = str(valor or "").strip()
    if texto.isdigit():
        return datetime.fromtimestamp(int(texto), tz=timezone.utc).replace(tzinfo=None)
    try:
        local = datetime.strptime(texto, FORMATO_FECHA_BFA).replace(tzinfo=HORA_ARGENTINA)
    except ValueError:
        return ahora
    return local.astimezone(timezone.utc).replace(tzinfo=None)


class SelladorSimulado:
    """Sello simulado para desarrollo y pruebas: nunca es un sello real."""

    simulado = True

    def sellar(self, huella):
        """Recibo simulado derivado de la huella."""
        return "SIMULADO-" + hashlib.sha256(f"simulado:{huella}".encode()).hexdigest()[:32]

    def verificar(self, huella, recibo):
        """Se confirma al instante, con una referencia que dice que es simulada."""
        del huella
        return Confirmacion(
            referencia=f"Sello simulado {recibo[-8:]}",
            fecha=datetime.now(timezone.utc).replace(tzinfo=None),
        )


def crear_sellador(configuracion):
    """El sellador de ``SELLO_TIEMPO``: ``bfa``, ``simulado`` o ``desactivado`` (None)."""
    modo = configuracion.get("SELLO_TIEMPO", "simulado")
    if modo == "bfa":
        return SelladorBFA(configuracion.get("URL_SELLO_BFA", URL_BFA))
    if modo == "simulado":
        return SelladorSimulado()
    return None
