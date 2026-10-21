"""Sello de tiempo de las huellas en Blockchain Federal Argentina (patrón Strategy).

Implementaciones intercambiables con la misma interfaz (RF37 CA4):

- ``SelladorBFA``: el servicio público Sello de Tiempo 2.0 de BFA
  (https://tsa2.buenosaires.gob.ar, el que usa https://bfa.ar/sello2). Solo
  envía la huella SHA-256, nunca el archivo (RF37). El sello se pide con
  ``sellar`` y, cuando BFA lo incluye en un bloque, se confirma con
  ``verificar``. El formato sigue la API pública del proyecto ``tsa2`` de BFA:
  ``POST /stamp`` con ``{"hashes": [...]}`` y ``GET /verify/<huella>``, que
  responde ``{"stamped": bool, "stamps": [...]}``.
- ``SelladorSimulado``: desarrollo y pruebas. Responde al instante y marca
  todo como simulado, para que nunca se confunda con un sello real.

Cualquier error de red se informa con ``SelloNoDisponible``: el servicio lo
reintenta después y la carga o el análisis siguen (RF37 CA3, RNF20 CA1).

Realiza: RF37 (CA3, CA4).
"""
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib import error, request

URL_BFA = "https://tsa2.buenosaires.gob.ar"
TIEMPO_ESPERA = 10  # segundos por solicitud


class SelloNoDisponible(Exception):
    """El servicio de sello no respondió o respondió con un error."""


@dataclass
class Confirmacion:
    """Sello confirmado: la referencia de la transacción o bloque y su fecha (RF37 CA2)."""

    referencia: str
    fecha: datetime


class SelladorBFA:
    """Cliente del servicio de sello de tiempo de Blockchain Federal Argentina."""

    simulado = False

    def __init__(self, url=URL_BFA, tiempo_espera=TIEMPO_ESPERA):
        self.url = url.rstrip("/")
        self.tiempo_espera = tiempo_espera

    def _enviar(self, ruta, datos=None):
        """POST con ``datos`` en JSON, o GET si no hay datos; devuelve el JSON de la respuesta."""
        cuerpo = json.dumps(datos).encode() if datos is not None else None
        solicitud = request.Request(
            f"{self.url}{ruta}", data=cuerpo, method="POST" if cuerpo else "GET",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with request.urlopen(solicitud, timeout=self.tiempo_espera) as respuesta:
                return json.loads(respuesta.read() or b"{}")
        except (error.URLError, TimeoutError, ValueError) as falla:
            raise SelloNoDisponible(f"BFA no respondió: {falla}") from falla

    def sellar(self, huella):
        """Pide el sello de la huella. BFA no entrega recibo: la huella misma lo identifica."""
        self._enviar("/stamp", {"hashes": [huella]})
        return huella

    def verificar(self, huella, recibo):
        """La ``Confirmacion`` si el sello ya está en un bloque; None si sigue pendiente."""
        del recibo
        respuesta = self._enviar(f"/verify/{huella}")
        sellos = respuesta.get("stamps") or []
        if not respuesta.get("stamped") or not sellos:
            return None
        sello = sellos[0]
        bloque = sello.get("blocknumber") or sello.get("blockNumber") or sello.get("block")
        momento = sello.get("blocktimestamp") or sello.get("timestamp")
        fecha = (
            datetime.fromtimestamp(int(momento), tz=timezone.utc).replace(tzinfo=None)
            if str(momento or "").isdigit() else datetime.now(timezone.utc).replace(tzinfo=None)
        )
        referencia = f"BFA bloque {bloque}" if bloque else "BFA"
        return Confirmacion(referencia=referencia, fecha=fecha)


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
