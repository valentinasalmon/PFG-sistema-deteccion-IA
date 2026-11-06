"""Obtención del modelo ONNX de la capa 4 (funcionalidad 012).

Adaptador entre el análisis y el registro de modelos de la funcionalidad 010:
baja la **versión fija** configurada, verifica su huella SHA-256 contra
``huellas.json`` antes de usarla (ADR-0014) y deja el predictor en una caché
del proceso, para que cada trabajador cargue el modelo una sola vez
(RF42 CA3).

El origen del modelo es intercambiable (Strategy): un repositorio privado de
Hugging Face (``hugging_face:<usuario/repositorio>``) en producción o una
carpeta (``local:<ruta>``) en desarrollo y en las pruebas. Sin configuración,
o ante cualquier falla, se lanza ``ModeloNoDisponible`` con un motivo legible:
la capa queda "No disponible" y el resto del análisis sigue (RN26).

Realiza: RF42 (CA3), RNF24 (CA1), RN26, RN29; ADR-0014, ADR-0015.
"""
import logging
import threading
from pathlib import Path

from clasificador.datos.manifiesto import huella_archivo
from clasificador.inferencia.predictor import ErrorModelo, PredictorOnnx
from clasificador.registro.registro_modelos import (
    ARCHIVO_HUELLAS,
    ARCHIVO_MODELO,
    ErrorRegistro,
    RegistroHuggingFace,
    RegistroLocal,
    verificar_modelo,
)

registro_eventos = logging.getLogger(__name__)

_CACHE = {}
_CERROJO = threading.Lock()


class ModeloNoDisponible(Exception):
    """No se pudo obtener o cargar el modelo; el mensaje se muestra al usuario."""


class ModeloCargado:
    """Predictor listo para usar, con los datos que registra cada resultado (RN29)."""

    def __init__(self, predictor, huella):
        self.predictor = predictor
        self.huella = huella

    @property
    def version(self):
        """Versión del modelo (MAJOR.MINOR.PATCH), leída del propio ONNX."""
        return self.predictor.version

    @property
    def metadatos(self):
        """Metadatos del ONNX: huella del manifiesto de entrenamiento, commit, etc."""
        return self.predictor.metadatos


def _crear_registro(especificacion):
    """Registro de modelos a partir de ``hugging_face:<repo>`` o ``local:<carpeta>``."""
    tipo, _, destino = especificacion.partition(":")
    if tipo == "hugging_face" and destino:
        return RegistroHuggingFace(destino)
    if tipo == "local" and destino:
        return RegistroLocal(Path(destino))
    raise ModeloNoDisponible(
        "La configuración del registro de modelos no es válida: se espera "
        "'hugging_face:<repositorio>' o 'local:<carpeta>'."
    )


def _ruta_verificada(configuracion, version):
    """Ruta del ONNX verificado: lo reutiliza si ya está bajado; si no, lo pide al registro."""
    carpeta = Path(configuracion["CARPETA_MODELOS_ONNX"])
    modelo = carpeta / f"v{version}" / ARCHIVO_MODELO
    huellas = modelo.with_name(ARCHIVO_HUELLAS)
    if modelo.is_file() and huellas.is_file():
        return verificar_modelo(modelo, huellas)
    registro = _crear_registro(configuracion["MODELO_RED_NEURONAL_REGISTRO"])
    # El registro local copia en la carpeta que recibe; el de Hugging Face agrega v<versión>.
    destino = carpeta / f"v{version}" if isinstance(registro, RegistroLocal) else carpeta
    return registro.obtener(version, destino)


def obtener_modelo(configuracion):
    """Devuelve el modelo configurado, cargado una sola vez por proceso.

    Raises:
        ModeloNoDisponible: sin configuración, si la versión no existe, si la
            descarga falla, si la huella no coincide o si el archivo no es un
            modelo válido.
    """
    especificacion = configuracion.get("MODELO_RED_NEURONAL_REGISTRO", "")
    version = configuracion.get("MODELO_RED_NEURONAL_VERSION", "")
    if not especificacion or not version:
        raise ModeloNoDisponible(
            "El modelo de la red neuronal todavía no está configurado en el servidor."
        )
    clave = (especificacion, version)
    with _CERROJO:
        if clave in _CACHE:
            return _CACHE[clave]
        try:
            ruta = _ruta_verificada(configuracion, version)
            modelo = ModeloCargado(PredictorOnnx(ruta), huella_archivo(ruta))
        except ModeloNoDisponible:
            raise
        except ErrorRegistro as error:
            registro_eventos.warning("Modelo de la capa 4 no disponible: %s", error)
            raise ModeloNoDisponible(
                f"No se pudo verificar la versión {version} del modelo: {error}."
            ) from error
        except ErrorModelo as error:
            registro_eventos.warning("Modelo de la capa 4 inválido: %s", error)
            raise ModeloNoDisponible("El archivo del modelo no es válido.") from error
        except Exception as error:  # pylint: disable=broad-exception-caught
            # Red, permisos o un registro inaccesible: nunca detiene el análisis (RN26).
            registro_eventos.warning("No se pudo obtener el modelo de la capa 4: %s", error)
            raise ModeloNoDisponible(
                f"No se pudo obtener la versión {version} del modelo del registro."
            ) from error
        _CACHE[clave] = modelo
        return modelo


def vaciar_cache():
    """Olvida los modelos cargados (solo para las pruebas)."""
    with _CERROJO:
        _CACHE.clear()
