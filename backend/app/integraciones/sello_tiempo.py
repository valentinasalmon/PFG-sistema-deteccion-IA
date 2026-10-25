"""Sello de tiempo de las huellas en Hedera (patrón Strategy, ADR-0018).

Implementaciones intercambiables con la misma interfaz (RF37 CA4):

- ``SelladorHedera``: Hedera Consensus Service. ``sellar`` publica en el tema
  de la plataforma un mensaje con la huella SHA-256 (nunca el archivo ni
  datos personales, RF37 CA5) y devuelve el recibo ``<red>:<tema>/<secuencia>``.
  ``verificar`` consulta ese mensaje en el *mirror node* público, comprueba
  que contiene la huella y devuelve la fecha de consenso.
- ``SelladorSimulado``: desarrollo y pruebas. Responde al instante y marca
  todo como simulado, para que nunca se confunda con un sello real.

Reemplaza al sellador de Blockchain Federal Argentina (funcionalidad 016),
que rechazaba las conexiones desde fuera de Argentina. Cualquier error de red
se informa con ``SelloNoDisponible``: el servicio lo reintenta después y la
carga o el análisis siguen (RF37 CA3, RNF20 CA1).

Realiza: RF37 (CA3 a CA5).
"""
import base64
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib import error, request

TIEMPO_ESPERA = 10  # segundos por solicitud
REDES_HEDERA = ("testnet", "mainnet", "previewnet")
URL_MIRROR = {
    "testnet": "https://testnet.mirrornode.hedera.com",
    "mainnet": "https://mainnet-public.mirrornode.hedera.com",
    "previewnet": "https://previewnet.mirrornode.hedera.com",
}
# Recibo de un sello de Hedera: red, tema y número de secuencia del mensaje.
PATRON_RECIBO = re.compile(r"^(testnet|mainnet|previewnet):(\d+\.\d+\.\d+)/(\d+)$")

registro_log = logging.getLogger(__name__)


class SelloNoDisponible(Exception):
    """El servicio de sello no respondió o respondió con un error."""


@dataclass
class Confirmacion:
    """Sello confirmado: la referencia del registro y su fecha (RF37 CA2)."""

    referencia: str
    fecha: datetime
    recibo: str | None = None  # recibo definitivo, si el servicio entrega uno nuevo


def mensaje_de_sello(huella, tipo="imagen"):
    """Contenido publicado en Hedera: solo la versión, el tipo y la huella (RF37 CA5)."""
    return json.dumps({"v": 1, "tipo": tipo, "sha256": huella}, separators=(",", ":"))


def enlace_explorador(recibo):
    """Enlace al mensaje en HashScan, el explorador público de Hedera; None si no aplica."""
    coincidencia = PATRON_RECIBO.match(recibo or "")
    if not coincidencia:
        return None
    red, tema, secuencia = coincidencia.groups()
    return f"https://hashscan.io/{red}/topic/{tema}/message/{secuencia}"


class SelladorHedera:
    """Cliente de Hedera Consensus Service para sellar huellas (ADR-0018).

    La cuenta paga cada mensaje (alrededor de US$ 0,0008) y es la única que
    puede publicar en el tema. Su clave privada llega por la configuración
    (parámetro cifrado en SSM); nunca se guarda en el repositorio.
    """

    simulado = False

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, red, cuenta, clave, tema, url_mirror=None, tiempo_espera=TIEMPO_ESPERA,
    ):
        self.red = red
        self.cuenta = cuenta
        self.clave = clave
        self.tema = tema
        self.url_mirror = (url_mirror or URL_MIRROR[red]).rstrip("/")
        self.tiempo_espera = tiempo_espera

    def _publicar(self, mensaje):
        """Publica el mensaje en el tema y devuelve su número de secuencia."""
        # Importación diferida: el SDK solo hace falta cuando el modo es "hedera".
        # pylint: disable=import-outside-toplevel
        from hiero_sdk_python import (
            AccountId,
            Client,
            Network,
            PrivateKey,
            ResponseCode,
            TopicId,
            TopicMessageSubmitTransaction,
        )

        cliente = Client(Network(self.red))
        try:
            cliente.set_operator(
                AccountId.from_string(self.cuenta), PrivateKey.from_string(self.clave)
            )
            transaccion = TopicMessageSubmitTransaction(
                topic_id=TopicId.from_string(self.tema), message=mensaje
            )
            recibo = transaccion.execute(cliente)
            if recibo.status != ResponseCode.SUCCESS:
                estado = ResponseCode(recibo.status).name
                raise SelloNoDisponible(f"Hedera rechazó el mensaje: {estado}")
            return recibo.topic_sequence_number
        finally:
            cliente.close()

    def sellar(self, huella, tipo="imagen"):
        """Publica la huella en Hedera y devuelve el recibo ``<red>:<tema>/<secuencia>``."""
        try:
            secuencia = self._publicar(mensaje_de_sello(huella, tipo))
        except SelloNoDisponible:
            raise
        except Exception as falla:  # pylint: disable=broad-exception-caught
            # El SDK lanza errores de gRPC, de red y de validación sin una base común.
            raise SelloNoDisponible(f"Hedera no respondió: {falla}") from falla
        return f"{self.red}:{self.tema}/{secuencia}"

    def verificar(self, huella, recibo):
        """La ``Confirmacion`` si el mensaje ya está en el *mirror node*; None si todavía no.

        Comprueba que el mensaje publicado contiene exactamente esta huella.
        """
        coincidencia = PATRON_RECIBO.match(recibo or "")
        if not coincidencia:
            raise SelloNoDisponible(f"Recibo de Hedera inválido: {recibo}")
        _, tema, secuencia = coincidencia.groups()
        url = f"{self.url_mirror}/api/v1/topics/{tema}/messages/{secuencia}"
        try:
            with request.urlopen(
                request.Request(url, headers={"Accept": "application/json"}),
                timeout=self.tiempo_espera,
            ) as respuesta:
                datos = json.loads(respuesta.read() or b"{}")
        except error.HTTPError as falla:
            if falla.code == 404:
                return None  # el mirror node tarda unos segundos en tener el mensaje
            raise SelloNoDisponible(f"El mirror node de Hedera respondió {falla.code}.") from falla
        except (error.URLError, TimeoutError, ValueError) as falla:
            raise SelloNoDisponible(f"El mirror node de Hedera no respondió: {falla}") from falla

        try:
            publicado = json.loads(base64.b64decode(datos.get("message") or ""))
        except ValueError as falla:
            raise SelloNoDisponible("El mensaje de Hedera no es un sello de evidentIA.") from falla
        if publicado.get("sha256") != huella:
            raise SelloNoDisponible("El mensaje de Hedera no contiene la huella de esta imagen.")
        return Confirmacion(
            referencia=f"Hedera {self.red} · tema {tema} · mensaje {secuencia}",
            fecha=fecha_de_consenso(datos.get("consensus_timestamp")),
        )


def fecha_de_consenso(valor):
    """Fecha UTC (sin zona) de una marca de consenso de Hedera ("segundos.nanosegundos")."""
    try:
        segundos = int(str(valor).split(".", maxsplit=1)[0])
    except ValueError:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    return datetime.fromtimestamp(segundos, tz=timezone.utc).replace(tzinfo=None)


def crear_tema_hedera(red, cuenta, clave, memo="evidentIA · sellos de tiempo"):
    """Crea el tema de la plataforma y devuelve su identificador.

    Solo la cuenta de la plataforma puede publicar (submit key) y administrar
    (admin key) el tema. Se ejecuta una sola vez por red (``flask sellos crear-tema``).
    """
    # pylint: disable=import-outside-toplevel
    from hiero_sdk_python import (
        AccountId,
        Client,
        Network,
        PrivateKey,
        ResponseCode,
        TopicCreateTransaction,
    )

    cliente = Client(Network(red))
    try:
        clave_privada = PrivateKey.from_string(clave)
        cliente.set_operator(AccountId.from_string(cuenta), clave_privada)
        recibo = (
            TopicCreateTransaction()
            .set_memo(memo)
            .set_admin_key(clave_privada.public_key())
            .set_submit_key(clave_privada.public_key())
            .execute(cliente)
        )
        if recibo.status != ResponseCode.SUCCESS:
            estado = ResponseCode(recibo.status).name
            raise SelloNoDisponible(f"Hedera rechazó el tema: {estado}")
        return str(recibo.topic_id)
    finally:
        cliente.close()


class SelladorSimulado:
    """Sello simulado para desarrollo y pruebas: nunca es un sello real."""

    simulado = True

    def sellar(self, huella, tipo="imagen"):
        """Recibo simulado derivado de la huella."""
        del tipo
        return "SIMULADO-" + hashlib.sha256(f"simulado:{huella}".encode()).hexdigest()[:32]

    def verificar(self, huella, recibo):
        """Se confirma al instante, con una referencia que dice que es simulada."""
        del huella
        return Confirmacion(
            referencia=f"Sello simulado {recibo[-8:]}",
            fecha=datetime.now(timezone.utc).replace(tzinfo=None),
        )


def crear_sellador(configuracion):
    """El sellador de ``SELLO_TIEMPO``: ``hedera``, ``simulado`` o ``desactivado`` (None).

    Si el modo es ``hedera`` pero falta la cuenta, la clave o el tema, el sello
    queda desactivado y se avisa en el log: la plataforma sigue funcionando.
    """
    modo = configuracion.get("SELLO_TIEMPO", "simulado")
    if modo == "hedera":
        red = configuracion.get("HEDERA_RED", "testnet")
        datos = [
            configuracion.get(campo) for campo in ("HEDERA_CUENTA", "HEDERA_CLAVE", "HEDERA_TEMA")
        ]
        if red not in REDES_HEDERA or not all(datos):
            registro_log.warning("Sello en Hedera sin configurar (red, cuenta, clave o tema).")
            return None
        return SelladorHedera(red, *datos, url_mirror=configuracion.get("HEDERA_URL_MIRROR"))
    if modo == "simulado":
        return SelladorSimulado()
    return None
