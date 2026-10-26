"""Pruebas del sello de tiempo en Hedera (funcionalidades 016 y 023).

La publicación en Hedera se reemplaza por una función simulada y el mirror
node por un servidor simulado (``urlopen`` reemplazado): nunca se llama a la
red real desde las pruebas. Las cuentas y temas son ficticios.
"""
import base64
import io
import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from app.integraciones import sello_tiempo
from app.integraciones.sello_tiempo import (
    SelladorHedera,
    SelladorSimulado,
    SelloNoDisponible,
    crear_sellador,
    enlace_explorador,
    mensaje_de_sello,
)
from app.servicios.servicio_sellos import MAXIMO_INTENTOS, ServicioSellos

HUELLA = "a" * 64
CONFIGURACION = {
    "SELLO_TIEMPO": "hedera", "HEDERA_RED": "testnet", "HEDERA_CUENTA": "0.0.1001",
    "HEDERA_CLAVE": "clave-de-prueba", "HEDERA_TEMA": "0.0.2002",
}


class Respuesta(io.BytesIO):
    """Respuesta HTTP mínima para ``urlopen``."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _mirror(monkeypatch, respuestas):
    """Mirror node simulado: devuelve las respuestas en orden y anota las URL pedidas."""
    pedidos = []

    def urlopen(solicitud, timeout):  # pylint: disable=unused-argument
        pedidos.append(solicitud.full_url)
        respuesta = respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return Respuesta(json.dumps(respuesta).encode())

    monkeypatch.setattr(sello_tiempo.request, "urlopen", urlopen)
    return pedidos


def _mensaje(huella, segundos="1792560000.123456789"):
    contenido = base64.b64encode(mensaje_de_sello(huella).encode()).decode()
    return {"consensus_timestamp": segundos, "message": contenido, "sequence_number": 7}


def test_hedera_publica_solo_la_huella_y_confirma(monkeypatch):
    """RF37 CA5: el mensaje solo lleva la huella; la confirmación sale del mirror node."""
    publicados = []
    sellador = crear_sellador(CONFIGURACION)
    monkeypatch.setattr(sellador, "_publicar", lambda mensaje: publicados.append(mensaje) or 7)
    pedidos = _mirror(monkeypatch, [_mensaje(HUELLA)])

    recibo = sellador.sellar(HUELLA)
    confirmacion = sellador.verificar(HUELLA, recibo)

    assert json.loads(publicados[0]) == {"v": 1, "tipo": "imagen", "sha256": HUELLA}
    assert recibo == "testnet:0.0.2002/7"
    assert pedidos == ["https://testnet.mirrornode.hedera.com/api/v1/topics/0.0.2002/messages/7"]
    assert confirmacion.referencia == "Hedera testnet · tema 0.0.2002 · mensaje 7"
    assert confirmacion.fecha == datetime(2026, 10, 21, 5, 20)
    assert enlace_explorador(recibo) == "https://hashscan.io/testnet/topic/0.0.2002/message/7"


def test_hedera_pendiente_caido_o_ajeno(monkeypatch):
    """404 del mirror node es "todavía no"; otra huella o un error de red no confirman."""
    sellador = crear_sellador(CONFIGURACION)
    no_esta = sello_tiempo.error.HTTPError("u", 404, "No encontrado", {}, None)
    _mirror(monkeypatch, [no_esta, _mensaje("b" * 64), sello_tiempo.error.URLError("sin red")])
    recibo = "testnet:0.0.2002/7"
    assert sellador.verificar(HUELLA, recibo) is None
    with pytest.raises(SelloNoDisponible):
        sellador.verificar(HUELLA, recibo)
    with pytest.raises(SelloNoDisponible):
        sellador.verificar(HUELLA, recibo)
    with pytest.raises(SelloNoDisponible):
        sellador.verificar(HUELLA, "recibo-invalido")
    assert enlace_explorador("SIMULADO-123") is None


def test_hedera_falla_al_publicar(monkeypatch):
    """Cualquier error del SDK se informa como SelloNoDisponible (RF37 CA3)."""
    sellador = crear_sellador(CONFIGURACION)

    def falla(mensaje):
        raise RuntimeError(f"sin conexión con los nodos: {len(mensaje)}")

    monkeypatch.setattr(sellador, "_publicar", falla)
    with pytest.raises(SelloNoDisponible):
        sellador.sellar(HUELLA)


def test_crear_sellador():
    """RF37 CA4: la implementación sale de la configuración; sin datos, queda desactivado."""
    assert isinstance(crear_sellador(CONFIGURACION), SelladorHedera)
    assert crear_sellador({**CONFIGURACION, "HEDERA_CLAVE": ""}) is None
    assert crear_sellador({**CONFIGURACION, "HEDERA_RED": "otra"}) is None
    assert isinstance(crear_sellador({"SELLO_TIEMPO": "simulado"}), SelladorSimulado)
    assert crear_sellador({"SELLO_TIEMPO": "desactivado"}) is None


class Repositorio:  # pylint: disable=too-few-public-methods
    """Repositorio en memoria."""

    def __init__(self, imagenes=()):
        self.imagenes = list(imagenes)
        self.confirmaciones = 0

    def confirmar(self):
        """Cuenta las confirmaciones."""
        self.confirmaciones += 1

    def con_sello_en_curso(self, estados):
        """Imágenes en los estados pedidos."""
        return [i for i in self.imagenes if i.sello_estado in estados]


def _imagen(estado="pendiente"):
    return SimpleNamespace(id=1, id_caso=7, huella=HUELLA, sello_estado=estado, sello_recibo=None,
                           sello_referencia=None, sello_fecha=None, sello_simulado=False,
                           sello_intentos=0)


def test_servicio_sella_con_el_simulado():
    """Con el simulado se sella al instante y queda marcado como simulado."""
    registro = SimpleNamespace(entradas=[])
    registro.registrar = lambda *a, **k: registro.entradas.append((a, k))
    imagen = _imagen()
    servicio = ServicioSellos(Repositorio([imagen]), SelladorSimulado(), registro)

    assert servicio.procesar() == {"sellados": 1, "en_curso": 0}
    assert imagen.sello_estado == "sellado" and imagen.sello_simulado is True
    assert imagen.sello_referencia.startswith("Sello simulado")
    assert registro.entradas[0][0][0] == "imagen.sello"


def test_servicio_reintenta_y_marca_fallido():
    """RF37 CA3: una falla no lanza; después de muchos intentos queda fallido."""

    class Caido:  # pylint: disable=too-few-public-methods
        """Sellador que nunca responde."""

        simulado = False

        def sellar(self, huella):
            """Siempre falla."""
            raise SelloNoDisponible(huella)

    imagen = _imagen()
    servicio = ServicioSellos(Repositorio([imagen]), Caido(), SimpleNamespace(registrar=None))
    assert servicio.intentar(imagen) == "pendiente" and imagen.sello_intentos == 1
    imagen.sello_intentos = MAXIMO_INTENTOS - 1
    assert servicio.intentar(imagen) == "fallido"


def test_desactivado_no_hace_nada():
    """Sin sellador no se toca la imagen."""
    imagen = _imagen(None)
    servicio = ServicioSellos(Repositorio([imagen]), None, None)
    assert servicio.intentar(imagen) is None
    assert servicio.procesar() == {"sellados": 0, "en_curso": 0}


def test_fecha_de_consenso_invalida_usa_la_actual():
    """Si el mirror node no informa la marca de consenso, se usa la fecha actual."""
    assert sello_tiempo.fecha_de_consenso(None).year >= 2026


def test_comando_crear_tema(aplicacion, monkeypatch):
    """023: el comando pide la clave sin mostrarla y muestra el tema creado."""
    creados = []
    monkeypatch.setattr(
        "app.comandos.crear_tema_de_sellos",
        lambda red, cuenta, clave: creados.append((red, cuenta, clave)) or "0.0.2002",
    )
    resultado = aplicacion.test_cli_runner().invoke(
        args=["sellos", "crear-tema", "--cuenta", "0.0.1001"], input="clave-de-prueba\n"
    )
    assert "Tema creado en testnet: 0.0.2002" in resultado.output
    assert "clave-de-prueba" not in resultado.output
    assert creados == [("testnet", "0.0.1001", "clave-de-prueba")]

    monkeypatch.setattr(
        "app.comandos.crear_tema_de_sellos",
        lambda *_: (_ for _ in ()).throw(RuntimeError("sin saldo")),
    )
    resultado = aplicacion.test_cli_runner().invoke(
        args=["sellos", "crear-tema", "--cuenta", "0.0.1001"], input="x\n"
    )
    assert resultado.exit_code != 0 and "sin saldo" in resultado.output
