"""Pruebas del contenido del informe PDF (CA2 y CA3 de la funcionalidad 008).

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


def test_el_informe_tiene_todos_los_datos_pedidos():
    """CA2 (RF44 CA1, RNF07 CA3, RN29)."""
    html = _html(_analisis(), {1: b"\xff\xd8\xffjpeg"})
    for texto in (
        "CASO-2026-000007", "EXP-12/2026", "Automovilístico", "01/09/2026", "Av. Corrientes 1234",
        "Ana López", "Abogado", "Colegio de abogados", "CPACF",
        "19/10/2026 15:00",  # pedido a las 18:00 UTC, en la hora de Argentina
        "data:image/jpeg;base64,", "a" * 64, "Sello de tiempo en Blockchain Federal Argentina",
        "Nivel de indicio: 90 %", "Photoshop", "Adobe Photoshop 25.0",
        "Plataforma", "0.2.0", "Capa 1 · Metadatos", "1.0 (ExifTool 12.76)", "WeasyPrint",
        "Limitaciones y advertencia legal", "perito especializado",
    ):
        assert texto in html, texto


def test_que_significa_por_capa_y_sin_veredictos():
    """CA3 (RF44 CA2, RN27): recuadro explicativo y ningún término de veredicto."""
    html = _html(_analisis())
    assert "¿Qué significa?" in html
    assert "datos ocultos además de la imagen" in html
    datos = informe_analisis.armar_datos(_analisis(), {}, "0.2.0")
    textos = " ".join(
        [datos["escala"], *datos["limitaciones"], *informe_analisis.QUE_SIGNIFICA.values()]
    ).lower()
    palabras = set(textos.replace(".", " ").replace(",", " ").replace(":", " ").split())
    assert not palabras & set(TERMINOS_DE_VEREDICTO)


def test_capa_de_credenciales_con_su_titulo_y_su_explicacion():
    """009 CA7: la capa 2 aparece con su título, su tabla y su recuadro."""
    analisis = _analisis()
    credenciales = _resultado()
    credenciales.capa = "c2pa"
    credenciales.detalle = {"tabla": [{"campo": "Firmante", "valor": "OpenAI OpCo, LLC"}]}
    analisis.imagenes[0].resultados.append(credenciales)
    analisis.versiones["c2pa"] = "1.0 (c2pa-python 0.38.0, lista de confianza abc/def)"

    html = _html(analisis)

    for texto in (
        "Capa 2 · Credenciales de contenido (C2PA)", "OpenAI OpCo, LLC",
        "lista de confianza del consorcio C2PA", "1.0 (c2pa-python 0.38.0",
    ):
        assert texto in html, texto


def test_capa_no_disponible_e_imagen_alterada():
    """La capa no disponible muestra el motivo; la imagen alterada, la aclaración."""
    assert "ExifTool no está instalado." in _html(_analisis(estado="no_disponible"))
    alterada = _html(_analisis(integridad="alterada"))
    assert "se\n        excluyó del análisis" in alterada or "excluyó del análisis" in alterada
    assert "Nivel de indicio" not in alterada


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
