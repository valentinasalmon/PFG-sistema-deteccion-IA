"""Capa 3: análisis de niveles de error (ELA, *Error Level Analysis*).

Recomprime la imagen en JPEG con una calidad fija y mide, en bloques, cuánto
cambia cada zona. Cada bloque se compara con los bloques de textura parecida
de la misma imagen (los bordes y los detalles cambian más que las zonas
lisas), y se señalan las regiones que se apartan del comportamiento general.
Los umbrales y su justificación están en
``docs/funcionalidades/011-capa-ela/plan.md``.

ELA es una señal complementaria: la capa nunca informa indicios fuertes. Además
del resultado, devuelve el mapa ELA con las regiones recuadradas; el servicio de
análisis lo guarda en el almacenamiento. La capa no accede a la base de datos.

Realiza: RF41 (CA1 a CA3), RF43 (CA1, CA2); RN26, RN27, RN29.
"""
import io
from dataclasses import dataclass

import numpy as np
import PIL
from PIL import Image, ImageChops, ImageDraw, UnidentifiedImageError

from app.analisis.base import (
    RECOMENDACION,
    SEVERIDAD_DEBIL,
    SEVERIDAD_MODERADO,
    SEVERIDAD_NEUTRO,
    Anomalia,
    CapaAnalisis,
    CapaNoDisponible,
    ResultadoCapa,
    anomalias_principales,
    calcular_nivel,
    describir_intensidad,
)

VERSION_CAPA = "1.0"

# --- Parámetros documentados en el plan de la 011 ---
CALIDAD_RECOMPRESION = 90
TAMANIO_BLOQUE = 16
CLASES_DE_TEXTURA = 10
UMBRAL_DESVIO_BLOQUE = 4.0  # desvíos robustos (MAD) para marcar un bloque
MINIMO_BLOQUES_REGION = 6  # una región más chica se considera ruido
SEPARACION_MAXIMA = 2  # bloques marcados a esta distancia o menos forman una misma región
UMBRAL_DESVIO_MODERADO = 10.0  # desvío medio de la región para un indicio moderado
MAXIMO_REGIONES_INFORMADAS = 3
MINIMO_BLOQUES_POR_LADO = 8  # imágenes de menos de 128 píxeles por lado no se analizan
LADO_MAXIMO_MAPA = 900
PISO_DISPERSION = 0.25  # evita dividir por casi cero en imágenes muy uniformes

# Tabla estándar de cuantización de luminancia (JPEG, anexo K), para estimar
# la calidad con que se guardó el archivo.
TABLA_LUMINANCIA = np.array([
    16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99,
], dtype=np.float64)

ACLARACION_PNG = (
    "La imagen está en PNG, un formato sin pérdida: ELA tiene validez limitada en este caso "
    "y sus resultados se informan como indicios débiles."
)
ACLARACION_MAPA = (
    "El mapa ELA es una señal complementaria: las zonas claras cambiaron más al recomprimir. "
    "Los bordes, los textos y las zonas muy detalladas también se ven claros sin que haya "
    "edición."
)


@dataclass
class Region:
    """Región de bloques que se apartan del comportamiento general."""

    fila: int
    columna: int
    alto: int
    ancho: int
    bloques: int
    desvio: float


def estimar_calidad_jpeg(imagen):
    """Calidad JPEG aproximada (1 a 100) según la tabla de luminancia, o None."""
    tablas = getattr(imagen, "quantization", None) or {}
    if 0 not in tablas or len(tablas[0]) != 64:
        return None
    escala = float(np.mean(np.asarray(tablas[0], dtype=np.float64) / TABLA_LUMINANCIA)) * 100
    calidad = (200 - escala) / 2 if escala <= 100 else 5000 / escala
    return int(round(min(100, max(1, calidad))))


def _por_bloques(matriz, funcion):
    """Aplica ``funcion`` (media o desvío) a cada bloque de TAMANIO_BLOQUE píxeles."""
    filas = matriz.shape[0] // TAMANIO_BLOQUE
    columnas = matriz.shape[1] // TAMANIO_BLOQUE
    recorte = matriz[: filas * TAMANIO_BLOQUE, : columnas * TAMANIO_BLOQUE]
    bloques = recorte.reshape(filas, TAMANIO_BLOQUE, columnas, TAMANIO_BLOQUE)
    return funcion(bloques, axis=(1, 3))


def desvios_por_bloque(error, textura):
    """Desvío robusto de cada bloque respecto de los bloques de textura parecida.

    El error esperado de un bloque depende de su textura: se agrupan los bloques
    en CLASES_DE_TEXTURA por cuantiles de textura, se resta la mediana de su clase
    y el residuo se expresa en desvíos absolutos medianos (MAD).
    """
    limites = np.quantile(textura, np.linspace(0, 1, CLASES_DE_TEXTURA + 1))
    clases = np.clip(np.searchsorted(limites, textura, side="right") - 1, 0, CLASES_DE_TEXTURA - 1)
    esperado = np.zeros_like(error)
    for clase in range(CLASES_DE_TEXTURA):
        elegidos = clases == clase
        if elegidos.any():
            esperado[elegidos] = np.median(error[elegidos])
    residuo = error - esperado
    centro = np.median(residuo)
    dispersion = np.median(np.abs(residuo - centro)) * 1.4826 + PISO_DISPERSION
    return (residuo - centro) / dispersion


def _ampliar(marcados):
    """Extiende cada bloque marcado SEPARACION_MAXIMA bloques en todas las direcciones.

    Así los bordes de una misma zona pegada, que ELA suele marcar por separado,
    quedan unidos en una sola región.
    """
    ampliados = marcados.copy()
    filas, columnas = marcados.shape
    for desplazamiento_fila in range(-SEPARACION_MAXIMA, SEPARACION_MAXIMA + 1):
        for desplazamiento_columna in range(-SEPARACION_MAXIMA, SEPARACION_MAXIMA + 1):
            origen = marcados[
                max(0, -desplazamiento_fila): filas - max(0, desplazamiento_fila),
                max(0, -desplazamiento_columna): columnas - max(0, desplazamiento_columna),
            ]
            ampliados[
                max(0, desplazamiento_fila): filas - max(0, -desplazamiento_fila),
                max(0, desplazamiento_columna): columnas - max(0, -desplazamiento_columna),
            ] |= origen
    return ampliados


def _componentes(mascara):
    """Grupos de celdas conectadas (vecinas en las cuatro direcciones) de una máscara."""
    visitados = np.zeros_like(mascara)
    filas, columnas = mascara.shape
    for inicio in zip(*np.nonzero(mascara)):
        if visitados[inicio]:
            continue
        visitados[inicio] = True
        pendientes, celdas = [inicio], []
        while pendientes:
            fila, columna = pendientes.pop()
            celdas.append((fila, columna))
            for vecina in ((fila + 1, columna), (fila - 1, columna),
                           (fila, columna + 1), (fila, columna - 1)):
                if (0 <= vecina[0] < filas and 0 <= vecina[1] < columnas
                        and mascara[vecina] and not visitados[vecina]):
                    visitados[vecina] = True
                    pendientes.append(vecina)
        yield celdas


def buscar_regiones(desvios):
    """Regiones de bloques marcados, de la más llamativa a la menos.

    Los bloques marcados cercanos (a SEPARACION_MAXIMA bloques o menos) forman
    una misma región; su tamaño, su ubicación y su desvío se calculan solo con
    los bloques marcados.
    """
    marcados = desvios > UMBRAL_DESVIO_BLOQUE
    regiones = []
    for grupo in _componentes(_ampliar(marcados)):
        celdas = [celda for celda in grupo if marcados[celda]]
        if len(celdas) < MINIMO_BLOQUES_REGION:
            continue
        indices = np.array(celdas)
        regiones.append(Region(
            fila=int(indices[:, 0].min()), columna=int(indices[:, 1].min()),
            alto=int(np.ptp(indices[:, 0]) + 1), ancho=int(np.ptp(indices[:, 1]) + 1),
            bloques=len(celdas), desvio=float(np.mean(desvios[indices[:, 0], indices[:, 1]])),
        ))
    return sorted(regiones, key=lambda r: (r.desvio * r.bloques ** 0.5), reverse=True)


def describir_ubicacion(region, filas, columnas):
    """Ubicación aproximada de la región en porcentajes de la imagen."""
    return (
        f"una zona de aproximadamente {round(100 * region.ancho / columnas)} % × "
        f"{round(100 * region.alto / filas)} % de la imagen, a "
        f"{round(100 * region.columna / columnas)} % del borde izquierdo y "
        f"{round(100 * region.fila / filas)} % del borde superior"
    )


def dibujar_mapa(diferencia, regiones):
    """Mapa ELA ampliado, en PNG, con las regiones recuadradas en rojo."""
    tope = max(float(np.percentile(diferencia, 99.5)), 1.0)
    brillo = np.clip(diferencia * (255.0 / tope), 0, 255).astype(np.uint8)
    mapa = Image.fromarray(brillo).convert("RGB")
    dibujo = ImageDraw.Draw(mapa)
    grosor = max(2, mapa.width // 300)
    for region in regiones:
        caja = (
            region.columna * TAMANIO_BLOQUE, region.fila * TAMANIO_BLOQUE,
            (region.columna + region.ancho) * TAMANIO_BLOQUE - 1,
            (region.fila + region.alto) * TAMANIO_BLOQUE - 1,
        )
        dibujo.rectangle(caja, outline=(230, 30, 30), width=grosor)
    mapa.thumbnail((LADO_MAXIMO_MAPA, LADO_MAXIMO_MAPA))
    salida = io.BytesIO()
    # Con una paleta de 64 colores el PNG pesa mucho menos (va embebido en el PDF).
    mapa.quantize(colors=64).save(salida, "PNG", optimize=True)
    return salida.getvalue()


class CapaELA(CapaAnalisis):
    """Señala las regiones con un nivel de error distinto al resto de la imagen."""

    nombre = "ela"
    titulo = "Niveles de error (ELA)"

    def version(self):
        """Versión de la capa, de sus bibliotecas y de la calidad de recompresión (RN29)."""
        return (
            f"{VERSION_CAPA} (Pillow {PIL.__version__}, NumPy {np.__version__}, "
            f"recompresión JPEG al {CALIDAD_RECOMPRESION} %)"
        )

    @staticmethod
    def calcular(contenido):
        """Diferencia por píxel, desvíos por bloque, regiones y calidad estimada.

        Raises:
            CapaNoDisponible: si la imagen no se puede leer.
        """
        try:
            original = Image.open(io.BytesIO(contenido))
            calidad = estimar_calidad_jpeg(original)
            imagen = original.convert("RGB")
        except (UnidentifiedImageError, OSError) as error:
            raise CapaNoDisponible("No se pudo leer la imagen para el análisis ELA.") from error
        recomprimida = io.BytesIO()
        imagen.save(recomprimida, "JPEG", quality=CALIDAD_RECOMPRESION)
        recomprimida.seek(0)
        diferencia = np.asarray(
            ImageChops.difference(imagen, Image.open(recomprimida).convert("RGB")),
            dtype=np.float32,
        ).max(axis=2)
        luminancia = np.asarray(imagen.convert("L"), dtype=np.float32)
        return {"diferencia": diferencia, "luminancia": luminancia, "calidad": calidad}

    @staticmethod
    def hallazgos(regiones, filas, columnas, es_png):
        """Una anomalía por región informada; moderada solo si el desvío es grande."""
        anomalias = []
        for region in regiones[:MAXIMO_REGIONES_INFORMADAS]:
            moderada = region.desvio >= UMBRAL_DESVIO_MODERADO and not es_png
            anomalias.append(Anomalia(
                "Región", f"{region.bloques} bloques, desvío {region.desvio:.1f}",
                f"El nivel de error de {describir_ubicacion(region, filas, columnas)} se aparta "
                f"del resto de la imagen ({region.desvio:.1f} desvíos). Puede corresponder a "
                "una zona pegada, retocada o guardada aparte, pero también a un borde o un "
                "detalle muy marcado.",
                SEVERIDAD_MODERADO if moderada else SEVERIDAD_DEBIL,
            ))
        return anomalias

    @staticmethod
    def redactar_conclusion(nivel, anomalias, es_png):
        """Conclusión como indicio, con las aclaraciones de ELA y la recomendación (RN27)."""
        if nivel == 0:
            texto = (
                "El nivel de error es homogéneo: no se encontraron regiones que se aparten del "
                "resto de la imagen. Esto no descarta ediciones, porque una imagen recomprimida "
                "varias veces o editada con cuidado puede no mostrar diferencias."
            )
        else:
            texto = (
                f"El análisis de niveles de error presenta {describir_intensidad(nivel)}. "
                + " ".join(a.descripcion for a in anomalias_principales(anomalias, 1))
            )
        if es_png:
            texto = f"{texto} {ACLARACION_PNG}"
        return f"{texto} {RECOMENDACION}"

    def analizar(self, contenido, contexto):
        """Calcula ELA, señala regiones y arma el resultado con el mapa (RF41, RF43)."""
        datos = self.calcular(contenido)
        diferencia = datos["diferencia"]
        es_png = contexto.formato == "png"
        filas = diferencia.shape[0] // TAMANIO_BLOQUE
        columnas = diferencia.shape[1] // TAMANIO_BLOQUE
        tabla = [
            {"campo": "Formato", "valor": "PNG (sin pérdida)" if es_png else "JPEG"},
            {"campo": "Calidad JPEG estimada",
             "valor": f"{datos['calidad']} %" if datos["calidad"] else "no corresponde"},
            {"campo": "Recompresión de referencia", "valor": f"JPEG al {CALIDAD_RECOMPRESION} %"},
        ]
        if min(filas, columnas) < MINIMO_BLOQUES_POR_LADO:
            motivo = (
                "La imagen es demasiado chica para dividirla en bloques y compararlos: "
                "ELA no aporta información en este caso."
            )
            return ResultadoCapa(
                nivel=0,
                anomalias=[Anomalia("Tamaño", f"{contexto.ancho} × {contexto.alto}", motivo,
                                    SEVERIDAD_NEUTRO)],
                conclusion=f"{motivo} {RECOMENDACION}",
                detalle={"tabla": tabla, "regiones": 0},
            )
        desvios = desvios_por_bloque(
            _por_bloques(diferencia, np.mean), _por_bloques(datos["luminancia"], np.std)
        )
        regiones = buscar_regiones(desvios)
        anomalias = self.hallazgos(regiones, filas, columnas, es_png)
        nivel = calcular_nivel(anomalias)
        tabla += [
            {"campo": "Bloques analizados",
             "valor": f"{filas * columnas} de {TAMANIO_BLOQUE} × {TAMANIO_BLOQUE} píxeles"},
            {"campo": "Regiones señaladas", "valor": str(len(regiones))},
        ]
        return ResultadoCapa(
            nivel=nivel,
            anomalias=anomalias,
            conclusion=self.redactar_conclusion(nivel, anomalias, es_png),
            detalle={
                "tabla": tabla, "regiones": len(regiones),
                # Valor obtenido que el informe compara con el umbral (entrevista del 02/10).
                "desvio_maximo": round(max((r.desvio for r in regiones), default=0.0), 1),
            },
            imagen=dibujar_mapa(diferencia, regiones[:MAXIMO_REGIONES_INFORMADAS]),
        )
