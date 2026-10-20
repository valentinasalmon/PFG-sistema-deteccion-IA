"""Orquestación de las etapas del pipeline sobre un directorio de trabajo.

Cada etapa lee lo que dejó la anterior y escribe sus resultados en una
subcarpeta fija del directorio de trabajo. Así una etapa se puede repetir o
retomar sin rehacer las anteriores (por ejemplo, si Kaggle corta la sesión
durante el entrenamiento).

::

    <directorio_trabajo>/
      crudo/  manifiesto_crudo.csv  validacion.json       obtener, validar
      preparado/  manifiesto.csv                          preparar
      entrenamiento/  mejor.pt  ultimo.pt  resultado.json entrenar
      mlruns/                                             entrenar (MLflow)
      exportacion/  modelo.onnx  exportacion.json         exportar
      evaluacion/  prueba/  no_visto/  condiciones_reales/ evaluar
      paquete/                                            publicar

Realiza: CA1 a CA17 de la funcionalidad 010 (orquestación). Ver ADR-0014.
"""

import json
import random
import shutil
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path

import numpy as np
import torch
import yaml
from PIL import Image
from torch.utils.data import DataLoader

from clasificador.configuracion import Configuracion, ConfiguracionFuente
from clasificador.datos.aumentacion import AumentacionEntrenamiento, TransformacionEvaluacion
from clasificador.datos.conjunto import ConjuntoImagenes, filtrar_particion
from clasificador.datos.fuentes import FuenteCarpetaLocal
from clasificador.datos.manifiesto import (
    RegistroImagen,
    escribir_manifiesto,
    huella_archivo,
    huella_manifiesto,
    leer_manifiesto,
)
from clasificador.datos.obtencion import obtener, obtener_de_fuente
from clasificador.datos.preparacion import preparar
from clasificador.datos.validacion import ResultadoValidacion, exigir_valido, validar
from clasificador.entrenamiento.calibracion import (
    ajustar_temperatura,
    error_calibracion_esperado,
    sigmoide,
)
from clasificador.entrenamiento.entrenador import (
    Entrenador,
    OpcionesEjecucion,
    fijar_semillas,
    predecir_logits,
)
from clasificador.evaluacion.evaluador import evaluar
from clasificador.exportacion.onnx import exportar_onnx
from clasificador.inferencia.predictor import MetadatosModelo, ParametrosEntrada, PredictorOnnx
from clasificador.inferencia.preprocesamiento import preprocesar
from clasificador.modelo.arquitecturas import crear_modelo
from clasificador.registro.compuerta import (
    CandidatoPublicacion,
    evaluar_compuerta,
    exigir_aprobacion,
)
from clasificador.registro.ficha import DatosFicha, generar_ficha
from clasificador.registro.registro_modelos import (
    ARCHIVO_FICHA,
    ARCHIVO_MODELO,
    RegistroModelos,
    validar_version,
)
from clasificador.seguimiento.experimentos import (
    RegistradorExperimentos,
    RegistradorMlflow,
    commit_actual,
    describir_entorno,
)

CANTIDAD_IMAGENES_MUESTRA = 8


class Rutas:
    """Rutas fijas dentro del directorio de trabajo de una ejecución."""

    def __init__(self, directorio_trabajo: Path) -> None:
        self.raiz = Path(directorio_trabajo)

    def __getattr__(self, nombre: str) -> Path:
        relativas = {
            "manifiesto_crudo": "manifiesto_crudo.csv",
            "validacion": "validacion.json",
            "preparado": "preparado",
            "manifiesto": "preparado/manifiesto.csv",
            "entrenamiento": "entrenamiento",
            "resultado_entrenamiento": "entrenamiento/resultado.json",
            "mlruns": "mlruns",
            "exportacion": "exportacion",
            "modelo": "exportacion/modelo.onnx",
            "resultado_exportacion": "exportacion/exportacion.json",
            "evaluacion": "evaluacion",
            "propio": "propio",
            "paquete": "paquete",
        }
        if nombre not in relativas:
            raise AttributeError(nombre)
        return self.raiz / relativas[nombre]


def _escribir_json(ruta: Path, contenido: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")


def _leer_json(ruta: Path) -> dict:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


# --- obtener y validar -----------------------------------------------------------


def etapa_obtener(configuracion: Configuracion) -> list[RegistroImagen]:
    """Descarga la muestra de cada fuente y escribe el manifiesto crudo."""
    rutas = Rutas(configuracion.directorio_trabajo)
    registros = obtener(configuracion.datos, rutas.raiz, configuracion.semilla)
    escribir_manifiesto(registros, rutas.manifiesto_crudo)
    return registros


def etapa_validar(configuracion: Configuracion) -> ResultadoValidacion:
    """Valida el manifiesto crudo y detiene el pipeline si hay errores."""
    rutas = Rutas(configuracion.directorio_trabajo)
    resultado = validar(
        leer_manifiesto(rutas.manifiesto_crudo),
        rutas.raiz,
        desbalance_tolerado=1.0,  # el balance se exige después de particionar
    )
    _escribir_json(rutas.validacion, {"errores": resultado.errores, "resumen": resultado.resumen})
    exigir_valido(resultado)
    return resultado


# --- preparar --------------------------------------------------------------------


def etapa_preparar(configuracion: Configuracion) -> list[RegistroImagen]:
    """Normaliza y particiona; valida el resultado con todas las reglas."""
    rutas = Rutas(configuracion.directorio_trabajo)
    datos = configuracion.datos
    registros = preparar(
        leer_manifiesto(rutas.manifiesto_crudo), rutas.raiz, rutas.preparado, datos,
        configuracion.semilla,
    )
    exigir_valido(
        validar(registros, rutas.preparado, datos.generadores_reservados, datos.desbalance_tolerado)
    )
    escribir_manifiesto(registros, rutas.manifiesto)
    return registros


# --- entrenar --------------------------------------------------------------------


def _iniciar_proceso_de_carga(_: int) -> None:
    """Semillas de numpy y random distintas y reproducibles en cada proceso."""
    semilla = torch.initial_seed() % 2**32
    np.random.seed(semilla)
    random.seed(semilla)


def _cargadores(
    configuracion: Configuracion, registros: list[RegistroImagen], raiz: Path
) -> tuple[DataLoader, DataLoader]:
    """Cargadores de entrenamiento (con aumentaciones) y de validación."""
    entrenamiento = configuracion.entrenamiento
    generador = torch.Generator().manual_seed(configuracion.semilla)
    comunes = {
        "batch_size": entrenamiento.tamanio_lote,
        "num_workers": entrenamiento.trabajadores_carga,
        "worker_init_fn": _iniciar_proceso_de_carga,
        "pin_memory": torch.cuda.is_available(),
    }
    return (
        DataLoader(
            ConjuntoImagenes(
                filtrar_particion(registros, "entrenamiento"), raiz,
                AumentacionEntrenamiento(entrenamiento.tamanio_recorte),
            ),
            shuffle=True, generator=generador, **comunes,
        ),
        DataLoader(
            ConjuntoImagenes(
                filtrar_particion(registros, "validacion"), raiz,
                TransformacionEvaluacion(entrenamiento.tamanio_recorte),
            ),
            shuffle=False, **comunes,
        ),
    )


def _calibrar(modelo: torch.nn.Module, cargador: DataLoader, dispositivo: torch.device) -> dict:
    """Ajusta la temperatura con la validación e informa el ECE antes y después."""
    logits, etiquetas = predecir_logits(modelo, cargador, dispositivo)
    temperatura = ajustar_temperatura(logits, etiquetas)
    return {
        "temperatura": temperatura,
        "ece_antes": error_calibracion_esperado(sigmoide(logits), etiquetas),
        "ece_despues": error_calibracion_esperado(sigmoide(logits / temperatura), etiquetas),
    }


def etapa_entrenar(
    configuracion: Configuracion,
    registrador: RegistradorExperimentos | None = None,
    opciones: OpcionesEjecucion | None = None,
) -> dict:
    """Entrena, calibra y registra el experimento. Se reanuda si fue cortado."""
    rutas = Rutas(configuracion.directorio_trabajo)
    fijar_semillas(configuracion.semilla)
    registros = leer_manifiesto(rutas.manifiesto)
    huella = huella_manifiesto(registros)
    registrador = registrador or RegistradorMlflow(rutas.mlruns)
    id_ejecucion = registrador.iniciar(
        configuracion.nombre,
        {
            **configuracion.model_dump(mode="json"),
            "huella_manifiesto": huella,
            "commit": commit_actual(),
            "entorno": describir_entorno(),
        },
    )
    exitosa = False
    try:
        modelo = crear_modelo(
            configuracion.entrenamiento.arquitectura, configuracion.entrenamiento.preentrenado
        )
        entrenador = Entrenador(
            modelo, configuracion.entrenamiento, rutas.entrenamiento, registrador, opciones
        )
        entrenador.reanudar()
        cargador_entrenamiento, cargador_validacion = _cargadores(
            configuracion, registros, rutas.preparado
        )
        resultado = entrenador.entrenar(cargador_entrenamiento, cargador_validacion)
        modelo.load_state_dict(
            torch.load(resultado.ruta_mejor, map_location=entrenador.opciones.dispositivo)
        )
        calibracion = _calibrar(modelo, cargador_validacion, entrenador.opciones.dispositivo)
        registrador.registrar_metricas(
            {"ece_antes": calibracion["ece_antes"], "ece_despues": calibracion["ece_despues"]}
        )
        resumen = {
            "mejor_auc": resultado.mejor_auc,
            "epoca_mejor": resultado.epoca_mejor,
            "historial": resultado.historial,
            "id_ejecucion": id_ejecucion,
            "huella_manifiesto": huella,
            **calibracion,
        }
        _escribir_json(rutas.resultado_entrenamiento, resumen)
        registrador.registrar_artefacto(rutas.resultado_entrenamiento)
        exitosa = True
        return resumen
    finally:
        registrador.finalizar(exitosa)


# --- exportar --------------------------------------------------------------------


def _muestra_prueba(
    registros: list[RegistroImagen], raiz: Path, tamanio_recorte: int
) -> np.ndarray:
    """Recortes de algunas imágenes de prueba para verificar la exportación."""
    seleccion = filtrar_particion(registros, "prueba")[:CANTIDAD_IMAGENES_MUESTRA]
    seleccion = seleccion or registros[:CANTIDAD_IMAGENES_MUESTRA]
    recortes = []
    for registro in seleccion:
        with Image.open(raiz / registro.ruta_relativa) as imagen:
            recortes.append(preprocesar(imagen, tamanio_recorte=tamanio_recorte))
    return np.concatenate(recortes)


def etapa_exportar(configuracion: Configuracion, version: str) -> dict:
    """Exporta el mejor modelo calibrado a ONNX y verifica la coincidencia."""
    validar_version(version)
    rutas = Rutas(configuracion.directorio_trabajo)
    entrenamiento = _leer_json(rutas.resultado_entrenamiento)
    registros = leer_manifiesto(rutas.manifiesto)
    arquitectura = configuracion.entrenamiento.arquitectura
    modelo = crear_modelo(arquitectura, preentrenado=False)
    modelo.load_state_dict(torch.load(rutas.entrenamiento / "mejor.pt", map_location="cpu"))
    tamanio = configuracion.entrenamiento.tamanio_recorte
    metadatos = MetadatosModelo(
        version=version,
        arquitectura=arquitectura,
        temperatura=entrenamiento["temperatura"],
        entrada=ParametrosEntrada(tamanio_recorte=tamanio),
        huella_manifiesto=huella_manifiesto(registros),
        commit=commit_actual(),
    )
    resultado = exportar_onnx(
        modelo.eval(), metadatos, rutas.modelo,
        _muestra_prueba(registros, rutas.preparado, tamanio), configuracion.exportacion,
    )
    resumen = {
        "version": version,
        "diferencia_maxima": resultado.diferencia_maxima,
        "latencia_ms_por_imagen": resultado.latencia_ms_por_imagen,
        "commit": metadatos.commit,
        "huella_manifiesto": metadatos.huella_manifiesto,
    }
    _escribir_json(rutas.resultado_exportacion, resumen)
    return resumen


# --- evaluar ---------------------------------------------------------------------


def _registros_conjunto_propio(ruta: Path, destino: Path) -> list[RegistroImagen]:
    """Copia el conjunto propio completo **sin normalizar**.

    Se evalúa tal como llega (original, WhatsApp, captura): normalizarlo
    borraría justamente las condiciones reales que se quieren medir (CA12).
    """
    fuente = FuenteCarpetaLocal(
        ConfiguracionFuente(
            nombre="propio", tipo="carpeta_local", ruta=ruta, cantidad_reales=1,
            licencia="propia",
        )
    )
    return [
        replace(registro, particion="prueba")
        for registro in obtener_de_fuente(fuente, destino, cantidades=None)
    ]


def etapa_evaluar(configuracion: Configuracion, conjunto_propio: Path | None = None) -> dict:
    """Evalúa el ONNX en prueba, en no vistos y, si se indica, en el conjunto propio."""
    rutas = Rutas(configuracion.directorio_trabajo)
    predictor = PredictorOnnx(rutas.modelo)
    registros = leer_manifiesto(rutas.manifiesto)
    informes = {}
    for particion in ("prueba", "no_visto"):
        seleccion = filtrar_particion(registros, particion)
        if seleccion:
            informes[particion] = evaluar(
                predictor, seleccion, rutas.preparado, rutas.evaluacion / particion
            ).a_diccionario()
    if conjunto_propio is not None:
        propios = _registros_conjunto_propio(Path(conjunto_propio), rutas.propio)
        informes["condiciones_reales"] = evaluar(
            predictor, propios, rutas.propio, rutas.evaluacion / "condiciones_reales"
        ).a_diccionario()
    return informes


# --- publicar --------------------------------------------------------------------


def _metricas_si_existen(rutas: Rutas, nombre: str) -> dict | None:
    ruta = rutas.evaluacion / nombre / "metricas.json"
    return _leer_json(ruta) if ruta.is_file() else None


def _armar_paquete(rutas: Rutas, configuracion: Configuracion, texto_ficha: str) -> Path:
    """Reúne en una carpeta todo lo que se publica de una versión."""
    paquete = rutas.paquete
    if paquete.exists():
        shutil.rmtree(paquete)
    paquete.mkdir(parents=True)
    shutil.copy2(rutas.modelo, paquete / ARCHIVO_MODELO)
    (paquete / ARCHIVO_FICHA).write_text(texto_ficha, encoding="utf-8")
    (paquete / "configuracion.yaml").write_text(
        yaml.safe_dump(configuracion.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    shutil.copy2(rutas.manifiesto, paquete / "manifiesto.csv")
    shutil.copy2(rutas.resultado_entrenamiento, paquete / "entrenamiento.json")
    shutil.copy2(rutas.resultado_exportacion, paquete / "exportacion.json")
    for evaluacion in sorted(rutas.evaluacion.iterdir()):
        shutil.copytree(evaluacion, paquete / "evaluacion" / evaluacion.name)
    if rutas.mlruns.is_dir():
        shutil.make_archive(str(paquete / "mlruns"), "zip", rutas.mlruns)
    return paquete


def etapa_publicar(
    configuracion: Configuracion, version: str, registro: RegistroModelos
) -> dict:
    """Genera la ficha, aplica la compuerta y, si aprueba, publica la versión."""
    rutas = Rutas(configuracion.directorio_trabajo)
    entrenamiento = _leer_json(rutas.resultado_entrenamiento)
    exportacion = _leer_json(rutas.resultado_exportacion)
    if exportacion["version"] != version:
        raise ValueError(
            f"el modelo se exportó como {exportacion['version']} y se quiere publicar como "
            f"{version}: volver a exportar con la versión correcta"
        )
    registros = leer_manifiesto(rutas.manifiesto)
    huella_real = huella_manifiesto(registros)
    metricas_prueba = _metricas_si_existen(rutas, "prueba") or {}
    ficha = generar_ficha(
        DatosFicha(
            version=version,
            fecha=date.today().isoformat(),
            configuracion=configuracion,
            huella_manifiesto=huella_real,
            huella_modelo=huella_archivo(rutas.modelo),
            resumen_datos=validar(registros, rutas.preparado, verificar_archivos=False).resumen,
            entrenamiento=entrenamiento,
            temperatura=entrenamiento["temperatura"],
            entorno=describir_entorno(),
            metricas_prueba=metricas_prueba,
            exportacion=exportacion,
            commit=exportacion["commit"],
            id_ejecucion=entrenamiento["id_ejecucion"],
            metricas_no_visto=_metricas_si_existen(rutas, "no_visto"),
            metricas_condiciones_reales=_metricas_si_existen(rutas, "condiciones_reales"),
        )
    )
    decision = evaluar_compuerta(
        CandidatoPublicacion(
            auc_prueba=metricas_prueba.get("total", {}).get("auc"),
            diferencia_onnx=exportacion["diferencia_maxima"],
            texto_ficha=ficha,
            huella_manifiesto_declarada=exportacion["huella_manifiesto"],
            huella_manifiesto_real=huella_real,
            commit=exportacion["commit"],
        ),
        configuracion.compuerta.auc_minimo,
        configuracion.exportacion.tolerancia,
    )
    _escribir_json(rutas.raiz / "compuerta.json", asdict(decision))
    exigir_aprobacion(decision)
    referencia = registro.publicar(version, _armar_paquete(rutas, configuracion, ficha))
    return {"version": version, "referencia": referencia, "ficha": ficha}
