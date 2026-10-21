"""Pruebas del sello de tiempo en Blockchain Federal Argentina (funcionalidad 016).

El cliente de BFA se prueba con un servidor simulado (``urlopen`` reemplazado);
nunca se llama al servicio real desde las pruebas.
"""
import io
import json
from types import SimpleNamespace

import pytest

from app.integraciones import sello_tiempo
from app.integraciones.sello_tiempo import (
    SelladorBFA,
    SelladorSimulado,
    SelloNoDisponible,
    crear_sellador,
)
from app.servicios.servicio_sellos import MAXIMO_INTENTOS, ServicioSellos

HUELLA = "a" * 64


class Respuesta(io.BytesIO):
    """Respuesta HTTP mínima para ``urlopen``."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _servidor(monkeypatch, respuestas):
    pedidos = []

    def urlopen(solicitud, timeout):  # pylint: disable=unused-argument
        pedidos.append((solicitud.full_url, json.loads(solicitud.data) if solicitud.data else None))
        respuesta = respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return Respuesta(json.dumps(respuesta).encode())

    monkeypatch.setattr(sello_tiempo.request, "urlopen", urlopen)
    return pedidos


def test_bfa_envia_solo_la_huella_y_confirma(monkeypatch):
    """RF37: solo viaja la huella; el recibo se verifica y devuelve bloque y fecha."""
    pedidos = _servidor(monkeypatch, [
        {"ok": True},
        {"stamped": True, "stamps": [{"blocknumber": 123456, "blocktimestamp": 1792560000}]},
    ])
    sellador = SelladorBFA("https://tsa.prueba")

    recibo = sellador.sellar(HUELLA)
    confirmacion = sellador.verificar(HUELLA, recibo)

    assert pedidos[0] == ("https://tsa.prueba/stamp", {"hashes": [HUELLA]})
    assert pedidos[1] == (f"https://tsa.prueba/verify/{HUELLA}", None)
    assert recibo == HUELLA
    assert confirmacion.referencia == "BFA bloque 123456"
    assert confirmacion.fecha.year == 2026


def test_bfa_pendiente_y_caido(monkeypatch):
    """Sin bloque todavía devuelve None; un error de red es SelloNoDisponible."""
    _servidor(monkeypatch, [
        {"stamped": False, "stamps": []}, sello_tiempo.error.URLError("sin red"),
    ])
    sellador = SelladorBFA()
    assert sellador.verificar(HUELLA, "r") is None
    with pytest.raises(SelloNoDisponible):
        sellador.sellar(HUELLA)


def test_crear_sellador():
    """RF37 CA4: la implementación sale de la configuración."""
    assert isinstance(crear_sellador({"SELLO_TIEMPO": "bfa"}), SelladorBFA)
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
