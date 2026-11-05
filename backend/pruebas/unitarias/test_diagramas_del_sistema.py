"""Pruebas del generador de diagramas desde el código (funcionalidad 039)."""
from herramientas import diagramas_del_sistema as diagramas

MODELO = '''
from app.extensiones import db


class Padre(db.Model):
    __tablename__ = "padres"
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(254), nullable=False, unique=True)


class Hijo(db.Model):
    __tablename__ = "hijos"
    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    id_padre = db.Column(db.Integer, db.ForeignKey("padres.id"), nullable=False)
    id_opcional = db.Column(db.Integer, db.ForeignKey("padres.id"), nullable=True)
'''


def test_lee_tablas_columnas_y_claves(tmp_path):
    """El analizador sintáctico obtiene tablas, tipos, claves y nulabilidad."""
    (tmp_path / "modelos.py").write_text(MODELO, encoding="utf-8")
    padres, hijos = diagramas.leer_modelos(tmp_path)
    assert padres.nombre == "padres" and padres.columnas[1].tipo == "String(254)"
    assert padres.columnas[1].unica and not padres.columnas[1].nula
    assert hijos.columnas[0].tipo == "BigInteger" and hijos.columnas[0].primaria
    assert hijos.columnas[1].foranea == "padres" and not hijos.columnas[1].nula


def test_el_er_usa_la_cardinalidad_de_la_clave_foranea(tmp_path):
    """Una clave obligatoria es «uno», una opcional es «cero o uno»."""
    (tmp_path / "modelos.py").write_text(MODELO, encoding="utf-8")
    texto = diagramas.generar_er(diagramas.leer_modelos(tmp_path))
    assert "padres ||--o{ hijos" in texto
    assert "padres |o--o{ hijos" in texto
    assert texto.startswith("@startuml modelo-de-datos-completo")


def test_los_modelos_reales_incluyen_las_tablas_nuevas():
    """El diagrama del sistema real contiene los cobros y la verificación de identidad."""
    nombres = {t.nombre for t in diagramas.leer_modelos()}
    assert {"usuarios", "casos", "imagenes", "cobros", "verificaciones_identidad"} <= nombres


def test_las_estrategias_salen_del_codigo():
    """Las implementaciones intercambiables se leen de integraciones y análisis."""
    estrategias = diagramas.leer_estrategias()
    assert "SelladorHedera" in estrategias["Sellador"]
    assert "CapaMetadatos" in estrategias["CapaAnalisis"]
    assert "ProveedorPagosSimulado" in estrategias["ProveedorPagos"]


def test_casos_de_uso_con_actores_y_relaciones():
    """Los casos de uso y sus relaciones salen de la especificación."""
    casos, relaciones = diagramas.leer_casos_de_uso()
    assert len(casos) >= 38
    assert ("CU01", "CU11", "extend") in relaciones
    assert "usuario <|-- referente" in diagramas.generar_actores(casos)
    cuentas = diagramas.generar_casos_de_uso(casos, relaciones, diagramas.GRUPOS_CU[0])
    assert "(CU01)" in cuentas and "(CU18)" not in cuentas
    assert "CU01 .> CU11" not in cuentas      # va en el diagrama de relaciones
    assert "CU01 ..> CU11 : <<extend>>" in diagramas.generar_relaciones(casos, relaciones)
    assert len(diagramas.diagramas_de_casos_de_uso()) == len(diagramas.GRUPOS_CU) + 2
    assert ("CU36", "CU08", "extend") in relaciones


def test_la_infraestructura_se_lee_de_los_archivos():
    """Los datos que verifica el despliegue salen de Terraform, systemd y Nginx."""
    datos = diagramas.datos_de_infraestructura()
    assert datos["tipo de instancia"] == "t3.small"
    assert datos["puerto de Gunicorn"] == "8000"
    assert datos["puerto HTTPS"] == "443"


def test_verificar_detecta_un_diagrama_desactualizado(tmp_path):
    """Un diagrama de despliegue sin los datos reales se informa."""
    (tmp_path / "07-despliegue-uml.puml").write_text("@startuml x\n@enduml\n", encoding="utf-8")
    problemas = diagramas.verificar(tmp_path)
    assert any("t3.small" in p for p in problemas)
    assert any("04-modelo-de-datos.puml" in p for p in problemas)


def test_revisar_calidad_detecta_notacion_y_ortografia(tmp_path):
    """Nodo sin estereotipo, ruta sin protocolo, flecha en una asociación y tilde faltante."""
    (tmp_path / "07-despliegue-uml.puml").write_text(
        '@startuml d\nnode "Servidor de imagenes" as a\nnode "B" <<device>> as b\n'
        "a --> b\n@enduml\n", encoding="utf-8")
    (tmp_path / "09a-casos-de-uso.puml").write_text(
        "@startuml c\nusuario --> CU01\nCU01 .> CU02\n@enduml\n", encoding="utf-8")
    problemas = " ".join(diagramas.revisar_calidad(tmp_path))
    assert "sin estereotipo" in problemas and "sin protocolo" in problemas
    assert "imágenes" in problemas
    assert "no lleva flecha" in problemas and "include" in problemas
