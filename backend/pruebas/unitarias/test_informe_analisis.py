"""Pruebas del contenido del informe PDF (funcionalidades 008, 025 y 026).

Se arma el informe con objetos simples en lugar de modelos de la base y se
revisa el HTML que se convierte a PDF; además se genera un PDF real.
"""
from datetime import date, datetime
from types import SimpleNamespace

import pytest

from app.analisis.base import TERMINOS_DE_VEREDICTO
from app.informes import informe_analisis
from app.informes.plantillas import entorno, formatear_hora_argentina

GENERADO = datetime(2026, 10, 19, 18, 30)


def _resultado(estado="completado"):
    return SimpleNamespace(
        capa="metadatos", estado=estado, nivel=90 if estado == "completado" else None,
        conclusion="Los metadatos presentan indicios fuertes. Se recomienda consultar a un perito.",
        motivo=None if estado == "completado" else "ExifTool no está instalado.",
        version="1.0 (ExifTool 12.76)",
        detalle={"tabla": [{"campo": "Software", "valor": "Adobe Photoshop 25.0"}]},
        anomalias=[SimpleNamespace(
            severidad="directo", descripcion="El archivo declara procesamiento con Photoshop.",
        )],
    )


def _analisis(integridad="verificada", estado="completado", colegio="CPACF"):
    caso = SimpleNamespace(
        numero="CASO-2026-000007", expediente="EXP-12/2026", tipo="automovilistico",
        fecha_hecho=date(2026, 9, 1), lugar="Av. Corrientes 1234", es_personal=True,
        organizacion=None,
    )
    solicitante = SimpleNamespace(
        nombre="Ana", apellido="López", perfil="abogado", colegio=colegio, empresa=None,
    )
    incluida = SimpleNamespace(
        id=1, nombre="frente.jpg", huella="a" * 64, integridad=integridad,
        resultados=[_resultado(estado)] if integridad == "verificada" else [],
    )
    return SimpleNamespace(
        id=5, caso=caso, solicitante=solicitante, creado_en=datetime(2026, 10, 19, 18, 0),
        iniciado_en=datetime(2026, 10, 19, 18, 0), imagenes=[incluida],
        versiones={"metadatos": "1.0 (ExifTool 12.76)"},
    )


def _html(analisis, miniaturas=None):
    datos = informe_analisis.armar_datos(analisis, miniaturas or {}, "0.2.0")
    return entorno.get_template("informe_analisis.html").render(informe=datos, generado_en=GENERADO)


def _con_original(analisis):
    analisis.imagenes[0].imagen = SimpleNamespace(
        formato="jpeg", ancho=1600, alto=1200, tamanio=162_816,
        cargada_en=datetime(2026, 10, 19, 17, 0),
        usuario=SimpleNamespace(nombre="Ana", apellido="López"),
        sello_estado="sellado", sello_fecha=datetime(2026, 10, 19, 17, 1), sello_simulado=False,
        sello_referencia="Hedera testnet · tema 0.0.2002 · mensaje 7",
    )
    return analisis


def test_el_informe_tiene_los_datos_del_caso_y_la_custodia():
    """RF44 CA1, RNF07 CA3, RN29: caso, solicitud, custodia, cronología y versiones."""
    html = _html(_con_original(_analisis()), {1: b"\xff\xd8\xffjpeg"})
    for texto in (
        "CASO-2026-000007", "EXP-12/2026", "Automovilístico", "01/09/2026", "Av. Corrientes 1234",
        "Ana López (Abogado)", "Colegio de abogados", "CPACF",
        "Evidencia y cadena de custodia", "a" * 64, "Coincide", "Hedera, 19/10/2026 17:01 UTC",
        "Cronología:", "primera carga 19/10/2026 14:00", "análisis pedido 19/10/2026 15:00",
        "data:image/jpeg;base64,", "Indicios moderados · 45 % a 69 %",
        "Este informe no constituye un dictamen pericial. Consulte a un profesional especializado.",
    ):
        assert texto in html, texto
    for texto in ("Resumen", "Glosario", "Limitaciones", "Uso previsto", "class=\"numero\"",
                  "Versiones:", "WeasyPrint", "Qué hacer ahora",
                  "Resultados deterministas y probabilísticos"):
        assert texto not in html, texto


def test_orden_de_las_secciones():
    """025 y 037: aviso primero, después caso, custodia, escala y resultados; sin cortes."""
    html = _html(_con_original(_analisis()))
    titulos = ("Herramienta de apoyo", "Caso y solicitud", "Evidencia y cadena de custodia",
               "Resultados por imagen")
    posiciones = [html.index(titulo) for titulo in titulos]
    assert posiciones == sorted(posiciones)
    assert "page-break-before" not in html  # sin saltos forzados
    assert "break-inside: avoid" in html  # si un bloque no entra, pasa entero a la otra hoja


def test_resultado_detallado_con_su_tipo():
    """025: por técnica, qué revisó, qué encontró (sin la recomendación repetida), datos y tipo."""
    analisis = _analisis()
    ela = _resultado()
    ela.capa, ela.nivel = "ela", 45
    ela.conclusion = (
        "El análisis presenta indicios moderados. Detalle de la región. "
        "Este resultado es un indicio y no constituye una conclusión definitiva. "
        "Se recomienda consultar a un perito especializado en informática forense."
    )
    ela.anomalias = [SimpleNamespace(severidad="moderado", descripcion="Zona que se aparta.")]
    ela.detalle = {"tabla": [{"campo": "Dimensiones", "valor": "1 × 1"},
                             {"campo": "Calidad JPEG estimada", "valor": "90 %"}]}
    analisis.imagenes[0].resultados.append(ela)

    html = _html(analisis)

    # 037: el PDF es breve; qué revisó cada técnica y sus datos van en el análisis en línea.
    assert "Qué revisó:" not in html and "Calidad JPEG estimada" not in html
    assert "Detalle de la región." in html and "Zona que se aparta." in html
    assert "no constituye una conclusión definitiva" not in html
    assert "Adobe Photoshop 25.0" not in html  # los datos de cada capa van en el detalle en línea
    assert html.count("tipo tipo-determinista") >= 1 and "tipo tipo-probabilistico" in html


def test_los_hallazgos_mencionados_en_la_conclusion_no_se_repiten():
    """025: si la conclusión ya cuenta el hallazgo, no se lista otra vez."""
    analisis = _analisis()
    resultado = analisis.imagenes[0].resultados[0]
    resultado.conclusion = "Presenta indicios. El archivo declara procesamiento con Photoshop."
    html = _html(analisis)
    assert html.count("El archivo declara procesamiento con Photoshop.") == 1


@pytest.mark.parametrize("perfil, titulo, referencia, intro, objeto", [
    ("abogado", "Informe técnico de imágenes", "Expediente", "ofrecerlas como prueba", "Caso"),
    ("aseguradora", "Informe de verificación de fotos del siniestro", "N.° de siniestro",
     "se liquida o se deriva a verificación", "Siniestro"),
])
def test_lenguaje_segun_el_rubro(perfil, titulo, referencia, intro, objeto):
    """RF54 y 037: título, referencia, introducción y «caso» o «siniestro» según el perfil."""
    analisis = _analisis()
    analisis.solicitante.perfil = perfil
    html = _html(analisis)
    assert titulo in html and f"<td>{referencia}</td>" in html and intro in html
    assert f"<h2>{objeto} y solicitud</h2>" in html
    assert f"Número de {objeto.lower()}" in html


def test_sin_veredictos():
    """RN27: ningún texto fijo del informe usa términos de veredicto."""
    textos = " ".join([
        informe_analisis.DESCARGO, *informe_analisis.QUE_MIRA.values(),
        *(r["intro"] for r in informe_analisis.TEXTOS_RUBRO.values()),
    ]).lower()
    palabras = set(textos.replace(".", " ").replace(",", " ").replace(":", " ").split())
    assert not palabras & set(TERMINOS_DE_VEREDICTO)


def test_bloque_de_verificacion():
    """026 y 037: el PDF lleva el QR para verificarlo y el enlace al análisis detallado."""
    datos = informe_analisis.armar_datos(_analisis(), {}, "0.2.0")
    datos["verificacion"] = {"codigo": "ABCD-EFGH-JKMN", "url": "http://x/verificar/ABCDEFGHJKMN",
                             "qr": "data:image/svg+xml,qr", "pagina": "http://x/verificar"}
    datos["detalle"] = {"url": "http://x/casos/7?etapa=analisis", "qr": "data:image/svg+xml,det"}
    html = entorno.get_template("informe_analisis.html").render(informe=datos, generado_en=GENERADO)
    assert "Más detalle y verificación" in html and "ABCD-EFGH-JKMN" in html
    assert "http://x/casos/7?etapa=analisis" in html and "data:image/svg+xml,det" in html
    assert "data:image/svg+xml,qr" in html and "http://x/verificar" in html


def test_mapa_ela_solo_si_encontro_algo():
    """011: el mapa se incluye chico y solo si la capa encontró señales."""
    analisis = _analisis()
    ela = _resultado()
    ela.capa, ela.id, ela.nivel = "ela", 41, 30
    analisis.imagenes[0].resultados.append(ela)
    datos = informe_analisis.armar_datos(analisis, {}, "0.2.0", {41: b"\x89PNGmapa"})
    html = entorno.get_template("informe_analisis.html").render(informe=datos, generado_en=GENERADO)
    assert 'alt="Mapa de Niveles de error"' in html
    ela.nivel = 0
    datos = informe_analisis.armar_datos(analisis, {}, "0.2.0", {41: b"\x89PNGmapa"})
    html = entorno.get_template("informe_analisis.html").render(informe=datos, generado_en=GENERADO)
    assert 'alt="Mapa de Niveles de error"' not in html


def test_capa_no_disponible_e_imagen_alterada():
    """La capa no disponible muestra el motivo; la imagen alterada, la aclaración."""
    assert "ExifTool no está instalado." in _html(_analisis(estado="no_disponible"))
    alterada = _html(_analisis(integridad="alterada"))
    assert "por eso no se analizó" in alterada and "No coincide" in alterada


def test_solicitante_de_una_aseguradora_y_cuenta_eliminada():
    """Muestra la empresa en lugar del colegio; sin cuenta, "Cuenta eliminada"."""
    analisis = _analisis(colegio=None)
    analisis.solicitante.perfil, analisis.solicitante.empresa = "aseguradora", "Seguros Sur"
    html = _html(analisis)
    assert "Empresa" in html and "Seguros Sur" in html
    analisis.solicitante = None
    assert "Cuenta eliminada" in _html(analisis)


def test_genera_un_pdf_real():
    """WeasyPrint convierte el informe en un PDF."""
    datos = informe_analisis.armar_datos(_analisis(), {}, "0.2.0")
    assert informe_analisis.generar_pdf(datos, GENERADO).startswith(b"%PDF")


@pytest.mark.parametrize("valor, esperado", [
    (datetime(2026, 1, 1, 2, 30), "31/12/2025 23:30"),
    ("2026-10-19T18:00:00", "19/10/2026 15:00"),
    (None, "—"),
])
def test_hora_de_argentina(valor, esperado):
    """Las fechas UTC se muestran en la hora de Argentina (UTC−3)."""
    assert formatear_hora_argentina(valor) == esperado


@pytest.mark.parametrize("nivel, banda", [
    (0, "Sin indicios"), (1, "Indicios débiles"), (44, "Indicios débiles"),
    (45, "Indicios moderados"), (69, "Indicios moderados"), (70, "Indicios fuertes"),
    (100, "Indicios fuertes"),
])
def test_bandas_de_indicio(nivel, banda):
    """Las bandas coinciden con describir_intensidad() de las capas."""
    assert informe_analisis.banda_de_indicio(nivel)["nombre"] == banda


def test_capa_4_con_su_titulo_y_su_tabla():
    """012 CA8: la red neuronal aparece en el PDF como técnica probabilística con su conclusión.

    Desde la 037 el PDF es breve: la tabla de criterios va en el detalle en línea.
    """
    analisis = _analisis()
    red = _resultado()
    red.capa, red.nivel = "red_neuronal", 80
    red.conclusion = (
        "La red neuronal estima una probabilidad de 80 % de que la imagen haya sido generada "
        "íntegramente con inteligencia artificial. Se recomienda consultar a un perito."
    )
    red.anomalias = [SimpleNamespace(severidad="fuerte", descripcion="Probabilidad alta.")]
    red.detalle = {"tabla": [
        {"campo": "Probabilidad estimada de imagen generada con IA", "valor": "80 %"},
        {"campo": "Versión del modelo", "valor": "1.0.0"},
    ]}
    analisis.imagenes[0].resultados.append(red)
    analisis.versiones["red_neuronal"] = "1.0 (modelo 1.0.0, ONNX Runtime 1.31.1)"

    html = _html(analisis)

    assert "<strong>Red neuronal</strong> <span class=\"tipo tipo-probabilistico\">" in html
    assert "La red neuronal estima una probabilidad de 80 %" in html
    datos = informe_analisis.armar_datos(analisis, {}, "0.2.0")
    assert datos["versiones"]["Capa 4 · Red neuronal"].startswith("1.0 (modelo 1.0.0")
