"""Diagramas del sistema generados desde el código real (funcionalidad 037).

Un diagrama del informe vale si coincide con el sistema. Esta herramienta lo
garantiza de tres formas:

* ``er``: genera el diagrama entidad-relación en PlantUML leyendo los modelos
  de ``app/modelos`` con el analizador sintáctico de Python (sin importar la
  aplicación ni instalar sus dependencias). Cada tabla, columna, clave y
  relación sale del código.
* ``componentes``: genera el diagrama de componentes UML a partir de las capas
  del backend y de las implementaciones intercambiables de ``app/integraciones``
  y ``app/analisis`` (patrón Strategy).
* ``verificar``: comprueba que el diagrama de despliegue mencione los datos
  reales de la infraestructura (tipo de instancia, región, sistema operativo,
  puertos y servicios de systemd), y que los diagramas generados estén al día.
* ``renderizar``: exporta a PNG todos los ``.puml`` de la carpeta de diagramas
  (necesita Java y Graphviz; descarga PlantUML la primera vez).

Uso, desde ``backend/``::

    python herramientas/diagramas_del_sistema.py er --compacto > \
        ../docs/arquitectura/diagramas/04-modelo-de-datos.puml
    python herramientas/diagramas_del_sistema.py componentes > \
        ../docs/arquitectura/diagramas/08-componentes-uml.puml
    python herramientas/diagramas_del_sistema.py verificar
    python herramientas/diagramas_del_sistema.py renderizar

Realiza: RNF19 (documentación fiel al sistema); funcionalidad 037.
"""
import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "backend" / "app"
DIAGRAMAS = RAIZ / "docs" / "arquitectura" / "diagramas"
VERSION_PLANTUML = "1.2024.7"
URL_PLANTUML = ("https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/"
                f"{VERSION_PLANTUML}/plantuml-{VERSION_PLANTUML}.jar")

ESTILO = """skinparam defaultFontName Arial
skinparam defaultFontSize 13
skinparam shadowing false
skinparam ArrowColor #4E5B54
skinparam nodesep 40
skinparam ranksep 55"""

# Interfaz común (patrón Strategy) que implementa cada módulo de integraciones.
INTERFACES = {
    "almacenamiento": "Almacenamiento",
    "cola": "Cola",
    "correo": "Enviador de correo",
    "sello_tiempo": "Sellador",
    "pagos": "ProveedorPagos",
    "identidad": "ProveedorIdentidad",
}

# Proveedor real previsto para las interfaces que hoy solo tienen una versión simulada.
PREVISTOS = {"ProveedorPagos": "Cresium", "ProveedorIdentidad": "Identik"}

# Servicio externo con el que habla cada implementación real.
EXTERNOS = {
    "S3": "Amazon S3",
    "RQ": "Redis",
    "Hedera": "Hedera",
    "SMTP": "Amazon SES",
    "Google": "Google",
    "Cresium": "Cresium",
    "Identik": "Identik",
}


@dataclass
class Columna:
    """Una columna de una tabla, como la declara el modelo."""

    nombre: str
    tipo: str
    primaria: bool = False
    foranea: str = ""
    nula: bool = True
    unica: bool = False


@dataclass
class Tabla:
    """Una tabla de la base, con su clase de modelo y sus columnas."""

    nombre: str
    clase: str
    columnas: list = field(default_factory=list)


def _nombre_de_tipo(nodo):
    """Extrae el tipo SQLAlchemy de la expresión del primer argumento."""
    if isinstance(nodo, ast.Call):
        argumentos = [a.value for a in nodo.args if isinstance(a, ast.Constant)]
        base = _nombre_de_tipo(nodo.func)
        if base == "with_variant":
            return _nombre_de_tipo(nodo.func.value)
        return f"{base}({argumentos[0]})" if argumentos and base else base
    if isinstance(nodo, ast.Attribute):
        return nodo.attr
    if isinstance(nodo, ast.Name):
        return nodo.id
    return "?"


def _es_llamada(nodo, nombre):
    """Indica si el nodo es una llamada a ``algo.nombre(...)`` o ``nombre(...)``."""
    if not isinstance(nodo, ast.Call):
        return False
    funcion = nodo.func
    return (isinstance(funcion, ast.Attribute) and funcion.attr == nombre) or \
        (isinstance(funcion, ast.Name) and funcion.id == nombre)


def leer_modelos(carpeta=APP / "modelos"):
    """Lee las tablas y columnas declaradas en los modelos de SQLAlchemy."""
    tablas = []
    for archivo in sorted(carpeta.glob("*.py")):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for clase in [n for n in arbol.body if isinstance(n, ast.ClassDef)]:
            tabla = Tabla(nombre="", clase=clase.name)
            for sentencia in clase.body:
                if not isinstance(sentencia, ast.Assign) or len(sentencia.targets) != 1:
                    continue
                destino = sentencia.targets[0]
                if not isinstance(destino, ast.Name):
                    continue
                if destino.id == "__tablename__" and isinstance(sentencia.value, ast.Constant):
                    tabla.nombre = sentencia.value.value
                elif _es_llamada(sentencia.value, "Column"):
                    tabla.columnas.append(_leer_columna(destino.id, sentencia.value))
            if tabla.nombre:
                tablas.append(tabla)
    return tablas


def _leer_columna(nombre, llamada):
    """Arma una Columna a partir de la llamada ``db.Column(...)``."""
    columna = Columna(nombre=nombre, tipo=_nombre_de_tipo(llamada.args[0]) if llamada.args
                      else "?")
    for argumento in llamada.args[1:]:
        if _es_llamada(argumento, "ForeignKey") and argumento.args:
            columna.foranea = argumento.args[0].value.split(".")[0]
    for clave in llamada.keywords:
        valor = clave.value.value if isinstance(clave.value, ast.Constant) else None
        if clave.arg == "primary_key" and valor:
            columna.primaria = True
            columna.nula = False
        elif clave.arg == "nullable":
            columna.nula = bool(valor)
        elif clave.arg == "unique" and valor:
            columna.unica = True
    return columna


def generar_er(tablas, compacto=False):
    """Diagrama entidad-relación en PlantUML (notación de pata de gallo)."""
    nombre = "modelo-de-datos" if compacto else "modelo-de-datos-completo"
    lineas = [f"@startuml {nombre}", ESTILO, "hide circle", "skinparam linetype ortho",
              "skinparam classBackgroundColor #F7F9FC", "skinparam classBorderColor #2F5DA8",
              ""]
    for tabla in tablas:
        lineas.append(f'entity "{tabla.nombre}" as {tabla.nombre} {{')
        claves = [c for c in tabla.columnas if c.primaria]
        resto = [c for c in tabla.columnas if not c.primaria]
        if compacto:
            resto = [c for c in resto if c.foranea or c.unica]
        for columna in claves:
            lineas.append(f"  * {columna.nombre} : {columna.tipo} <<PK>>")
        lineas.append("  --")
        for columna in resto:
            marcas = [m for m, si in (("FK", columna.foranea), ("UK", columna.unica)) if si]
            obligatoria = "* " if not columna.nula else ""
            sufijo = f" <<{', '.join(marcas)}>>" if marcas else ""
            lineas.append(f"  {obligatoria}{columna.nombre} : {columna.tipo}{sufijo}")
        lineas.append("}")
    lineas.append("")
    for tabla in tablas:
        for columna in tabla.columnas:
            if not columna.foranea:
                continue
            padre = "||" if not columna.nula else "|o"
            hijo = "o|" if columna.unica else "o{"
            lineas.append(f"{columna.foranea} {padre}--{hijo} {tabla.nombre}")
    lineas.append("@enduml")
    return "\n".join(lineas) + "\n"


def _clases_utiles(archivo):
    """Clases de un módulo que no son excepciones ni estructuras de datos."""
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    clases = []
    for clase in [n for n in arbol.body if isinstance(n, ast.ClassDef)]:
        bases = [getattr(b, "id", getattr(b, "attr", "")) for b in clase.bases]
        decoradores = [getattr(d, "id", getattr(d, "attr", "")) for d in clase.decorator_list]
        if any(b.endswith(("Exception", "Error")) for b in bases) or "dataclass" in decoradores:
            continue
        clases.append((clase.name, bases))
    return clases


def leer_estrategias():
    """Interfaces intercambiables y sus implementaciones, leídas del código."""
    estrategias = {}
    for modulo, interfaz in INTERFACES.items():
        archivo = APP / "integraciones" / f"{modulo}.py"
        if archivo.exists():
            estrategias[interfaz] = [n for n, _ in _clases_utiles(archivo)]
    capas = []
    for archivo in sorted((APP / "analisis").glob("*.py")):
        capas += [n for n, bases in _clases_utiles(archivo) if "CapaAnalisis" in bases]
    estrategias["CapaAnalisis"] = capas
    return estrategias


def _alias(nombre):
    """Identificador de PlantUML a partir de un nombre visible."""
    return re.sub(r"\W", "", nombre.lower())


def _contar_modulos(carpeta):
    """Cantidad de módulos de una capa del backend (sin __init__)."""
    return len([p for p in (APP / carpeta).glob("*.py") if p.name != "__init__.py"])


def generar_componentes(estrategias):
    """Diagrama de componentes UML con interfaces provistas y requeridas.

    Las capas del backend van en una columna; cada interfaz intercambiable
    (patrón Strategy) va en su propio marco con sus implementaciones, y los
    servicios externos se agrupan aparte. Los colores distinguen las capas
    (azul), las implementaciones reales (verde), las simuladas o de prueba
    (gris) y los sistemas externos (ámbar).
    """
    lineas = ["@startuml componentes", ESTILO, "left to right direction",
              "skinparam componentStyle uml2", "skinparam componentBorderColor #2F5DA8",
              "skinparam componentBackgroundColor #EAF0F9",
              "skinparam interfaceBorderColor #2F5DA8",
              "skinparam interfaceBackgroundColor #FFFFFF",
              "skinparam databaseBackgroundColor #EAF0F9", "skinparam rectangleBorderColor #9AA5A0",
              "skinparam packageBorderColor #4E5B54", "skinparam packageStyle rectangle",
              "skinparam legendBackgroundColor #FFFFFF", "",
              'component "Interfaz React\\n(navegador)" as spa',
              'package "Backend (Flask)" {',
              '  interface "API REST\\n/api (JSON)" as iapi',
              f'  component "Rutas\\n({_contar_modulos("rutas")} módulos)" as rutas',
              f'  component "Servicios\\n({_contar_modulos("servicios")} módulos)" as servicios',
              f'  component "Repositorios\\n({_contar_modulos("repositorios")} módulos)" as repos',
              f'  component "Modelos\\n({_contar_modulos("modelos")} módulos)" as modelos',
              '  component "Motor de análisis\\n(orquestador y reglas)" as motor']
    relaciones = ["spa ..> iapi : usa", "rutas -up- iapi", "rutas ..> servicios : llama",
                  "servicios ..> repos : consulta", "repos ..> modelos : mapea",
                  "modelos ..> pg : SQL", "servicios ..> motor : analiza",
                  "motor ..> i_capaanalisis : ejecuta"]
    for interfaz, implementaciones in estrategias.items():
        alias = "i_" + _alias(interfaz)
        lineas.append(f'  package "{interfaz}" as marco_{_alias(interfaz)} {{')
        lineas.append(f'    interface "{interfaz}" as {alias}')
        if interfaz != "CapaAnalisis":
            relaciones.append(f"servicios ..> {alias}")
        for implementacion in implementaciones:
            nombre = _alias(implementacion)
            simulada = re.search(r"Simulad|Memoria|Local|Sincronica|EnHilo", implementacion)
            destino = next((e for c, e in EXTERNOS.items() if c in implementacion), "")
            etiqueta = f"{implementacion}\\n{{usa: {destino}}}" if destino else implementacion
            color = "#F1F3F2" if simulada else "#E8F1D2"
            lineas.append(f'    component "{etiqueta}" as {nombre} {color}')
            relaciones.append(f"{alias} -- {nombre}")
        if interfaz in PREVISTOS:
            previsto = _alias(PREVISTOS[interfaz])
            lineas.append(f'    component "{PREVISTOS[interfaz]}\\n(previsto)" as {previsto} '
                          "#FFFFFF;line.dashed")
            relaciones.append(f"{alias} .. {previsto}")
        lineas.append("  }")
    lineas.append("}")
    lineas.append('database "PostgreSQL" as pg')
    leyenda = ["legend right", "<back:#EAF0F9>      </back> Capas del backend",
               "<back:#E8F1D2>      </back> Implementación real ({usa: servicio externo})",
               "<back:#F1F3F2>      </back> Implementación simulada o de prueba",
               "<back:#FFFFFF>      </back> Proveedor previsto (borde punteado)",
               "Las interfaces son contratos del código: CapaAnalisis es una clase base;",
               "las demás, un conjunto común de métodos que cada implementación cumple.",
               "endlegend"]
    return "\n".join(lineas + relaciones + leyenda + ["@enduml"]) + "\n"


# Módulos de la especificación (casos de uso por número), uno por diagrama.
GRUPOS_CU = [
    ("Cuentas", [1, 2, 3, 4, 5, 6, 7]),
    ("Organizaciones, planes y aseguradoras", [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 36, 37, 38]),
    ("Casos", [18, 19, 20, 21, 22, 23, 24]),
    ("Imágenes, análisis e informes", [25, 26, 27, 28, 29, 30, 33, 34, 35]),
    ("Retención", [31, 32]),
]
# Nombre visible de los actores que la especificación nombra de forma abreviada.
NOMBRE_ACTOR = {"Sistema": "Sistema\\n(procesos automáticos)"}
ROLES_DE_USUARIO = ["Referente", "Miembro", "Responsable", "Colaborador", "Lector"]
COLOR_ACTOR = {"Visitante": "#DDE3E0", "Usuario": "#DCE6F5", "Administrador": "#F6E3C8",
               "Sistema": "#E4E7E5"}


def _actor(actor):
    """Declaración de un actor con el color de su tipo (los roles, en verde)."""
    color = COLOR_ACTOR.get(actor, "#E8F1D2")
    return f'actor "{NOMBRE_ACTOR.get(actor, actor)}" as {_alias(actor)} {color}'


def leer_casos_de_uso(archivo=RAIZ / "docs" / "especificacion" / "05-casos-de-uso.md"):
    """Casos de uso, actores y relaciones de la especificación."""
    texto = archivo.read_text(encoding="utf-8")
    casos = re.findall(r"^\| (CU\d{2}) \| ([^|]+?) \| ([^|]+?) \|", texto, re.M)
    relaciones = []
    for linea in texto.splitlines():
        origen = re.match(r"^- \*\*(CU\d{2})\*\*", linea)
        if not origen:
            continue
        base = origen.group(1)
        desde = re.search(r"se extiende desde \*\*(CU\d{2})\*\*", linea)
        if desde:
            relaciones.append((base, desde.group(1), "extend"))
        incluye = re.search(r"incluye (.*?)(?:, y se extiende|$)", linea)
        if incluye:
            for destino in re.findall(r"\*\*(CU\d{2})\*\*", incluye.group(1)):
                relaciones.append((base, destino, "include"))
        hacia = re.search(r"se extiende a \*\*(CU\d{2})\*\*", linea)
        if hacia:
            relaciones.append((hacia.group(1), base, "extend"))
        extiende = re.search(r"\*\* extiende (.*?)(?: cuando|$)", linea)
        if extiende:
            for destino in re.findall(r"\*\*(CU\d{2})\*\*", extiende.group(1)):
                relaciones.append((base, destino, "extend"))
    return casos, relaciones


def generar_actores(casos):
    """Diagrama de actores: los roles son especializaciones del usuario registrado."""
    actores = _actores(casos)
    lineas = ["@startuml casos-de-uso-actores", ESTILO, "left to right direction",
              "skinparam actorBorderColor #17291F", ""]
    for actor in sorted(actores):
        lineas.append(_actor(actor))
    for rol in ROLES_DE_USUARIO:
        if rol in actores and "Usuario" in actores:
            lineas.append(f"usuario <|-- {_alias(rol)}")
    lineas.append("@enduml")
    return "\n".join(lineas) + "\n"


def _actores(casos):
    """Conjunto de actores que nombra la especificación."""
    actores = set()
    for _, _, quien in casos:
        actores.update(a.strip() for a in quien.split("/"))
    return actores


def generar_casos_de_uso(casos, relaciones, grupo=None):
    """Diagrama de casos de uso UML de un módulo (o de todos), con actores y relaciones."""
    titulo, numeros = grupo or ("evidentIA", [int(c[0][2:]) for c in casos])
    elegidos = [c for c in casos if int(c[0][2:]) in numeros]
    codigos = {c[0] for c in elegidos}
    sufijo = f"-{_alias(titulo)}" if grupo else ""
    lineas = [f"@startuml casos-de-uso{sufijo}", ESTILO, "left to right direction",
              "skinparam usecaseBackgroundColor #F7F9FC", "skinparam usecaseBorderColor #2F5DA8",
              "skinparam actorBorderColor #17291F", "skinparam packageStyle rectangle", ""]
    for actor in sorted(_actores(elegidos)):
        lineas.append(_actor(actor))
    lineas.append(f'rectangle "evidentIA: {titulo.lower()}" {{' if grupo else
                  'rectangle "evidentIA" {')
    for codigo, nombre, _ in elegidos:
        lineas.append(f'  usecase "{nombre}\\n({codigo})" as {codigo}')
    lineas.append("}")
    for codigo, _, quien in elegidos:
        for actor in quien.split("/"):
            lineas.append(f"{_alias(actor.strip())} -- {codigo}")
    for origen, destino, tipo in relaciones:
        if origen in codigos and destino in codigos:
            lineas.append(f"{origen} .> {destino} : <<{tipo}>>")
    lineas.append("@enduml")
    return "\n".join(lineas) + "\n"


def generar_relaciones(casos, relaciones):
    """Relaciones «include» y «extend» entre casos de uso de distintos módulos."""
    nombres = {codigo: nombre for codigo, nombre, _ in casos}
    usados = sorted({c for o, d, _ in relaciones for c in (o, d)})
    lineas = ["@startuml casos-de-uso-relaciones", ESTILO, "top to bottom direction",
              "skinparam usecaseBackgroundColor #F7F9FC", "skinparam usecaseBorderColor #2F5DA8"]
    for codigo in usados:
        lineas.append(f'usecase "{nombres[codigo]}\\n({codigo})" as {codigo}')
    for origen, destino, tipo in relaciones:
        lineas.append(f"{origen} ..> {destino} : <<{tipo}>>")
    lineas.append("@enduml")
    return "\n".join(lineas) + "\n"


def diagramas_de_casos_de_uso():
    """Archivos de casos de uso: actores, uno por módulo y las relaciones entre módulos."""
    casos, relaciones = leer_casos_de_uso()
    archivos = {"09-casos-de-uso-actores.puml": generar_actores(casos),
                "09f-casos-de-uso-relaciones.puml": generar_relaciones(casos, relaciones)}
    for indice, grupo in enumerate(GRUPOS_CU, start=1):
        archivos[f"09{chr(96 + indice)}-casos-de-uso.puml"] = generar_casos_de_uso(
            casos, relaciones, grupo)
    return archivos


def datos_de_infraestructura():
    """Datos que el diagrama de despliegue tiene que mostrar, leídos de la infraestructura."""
    infra = RAIZ / "infraestructura"
    variables = (infra / "terraform" / "principal" / "variables.tf").read_text(encoding="utf-8")
    servidor = (infra / "terraform" / "principal" / "servidor.tf").read_text(encoding="utf-8")
    datos = {}
    tipo = re.search(r'variable "tipo_instancia".*?default\s*=\s*"([^"]+)"', variables, re.S)
    region = re.search(r'variable "region".*?default\s*=\s*"([^"]+)"', variables, re.S)
    ubuntu = re.search(r"ubuntu/server/([\d.]+)", servidor)
    if tipo:
        datos["tipo de instancia"] = tipo.group(1)
    if region:
        datos["región"] = region.group(1)
    if ubuntu:
        datos["sistema operativo"] = ubuntu.group(1)
    for unidad in sorted((infra / "systemd").glob("*.service")):
        texto = unidad.read_text(encoding="utf-8")
        puerto = re.search(r"--bind [\d.]+:(\d+)", texto)
        if puerto:
            datos["puerto de Gunicorn"] = puerto.group(1)
        descripcion = re.search(r"Description=.*? - (.+)", texto)
        if descripcion:
            clave = descripcion.group(1).split("(")[0].split()[-1]
            datos[f"servicio {unidad.stem}"] = clave
    nginx = (infra / "nginx" / "plataforma.conf").read_text(encoding="utf-8")
    if re.search(r"listen 443", nginx):
        datos["puerto HTTPS"] = "443"
    return datos


def verificar(carpeta=DIAGRAMAS):
    """Lista lo que falta o está desactualizado en los diagramas."""
    problemas = []
    despliegue = carpeta / "07-despliegue-uml.puml"
    if despliegue.exists():
        texto = despliegue.read_text(encoding="utf-8").lower()
        for nombre, valor in datos_de_infraestructura().items():
            if valor.lower() not in texto:
                problemas.append(f"Despliegue: falta {nombre} «{valor}».")
    else:
        problemas.append("No existe 07-despliegue-uml.puml.")
    for archivo, esperado in (("04-modelo-de-datos.puml", generar_er(leer_modelos(), True)),
                              ("08-componentes-uml.puml",
                               generar_componentes(leer_estrategias())),
                              *diagramas_de_casos_de_uso().items()):
        ruta = carpeta / archivo
        if not ruta.exists() or ruta.read_text(encoding="utf-8") != esperado:
            problemas.append(f"{archivo} no coincide con el código: volver a generarlo.")
    for fuente in carpeta.glob("*.puml"):
        imagen = fuente.with_suffix(".png")
        if not imagen.exists() or imagen.stat().st_mtime < fuente.stat().st_mtime:
            problemas.append(f"{imagen.name} es anterior a su fuente: volver a renderizar.")
    return problemas + revisar_calidad(carpeta)


# Palabras que suelen quedar sin tilde al escribir etiquetas de diagramas.
SIN_TILDE = {"analisis": "análisis", "imagenes": "imágenes", "informacion": "información",
             "organizacion": "organización", "verificacion": "verificación",
             "auditoria": "auditoría", "modulos": "módulos", "sesion": "sesión",
             "codigo": "código", "region": "región", "retencion": "retención",
             "aplicacion": "aplicación", "pagina": "página", "publico": "público",
             "periodo": "período", "metodo": "método", "telefono": "teléfono"}
LIMITE_PLANTUML = 12000


def revisar_calidad(carpeta=DIAGRAMAS):
    """Reglas de notación, ortografía y tamaño que todo diagrama del informe cumple."""
    problemas = []
    for fuente in sorted(carpeta.glob("*.puml")):
        texto = fuente.read_text(encoding="utf-8")
        nombre = fuente.name
        # El modelo de datos muestra identificadores de la base, que van sin tilde.
        etiquetas = [] if nombre.startswith("04") else re.findall(r'"([^"]+)"', texto)
        for etiqueta in etiquetas:
            for palabra in re.findall(r"(?<![\w.\-])([a-záéíóúñ]+)(?![\w.\-])", etiqueta.lower()):
                if palabra in SIN_TILDE:
                    problemas.append(f"{nombre}: «{palabra}» lleva tilde ({SIN_TILDE[palabra]}).")
        if nombre.startswith("07"):
            problemas += _revisar_despliegue(nombre, texto)
        if nombre.startswith(("07", "08")) and re.search(r"^\s*rectangle ", texto, re.M):
            problemas.append(f"{nombre}: «rectangle» no es notación UML; usar node o package.")
        if nombre.startswith("09"):
            for linea in texto.splitlines():
                if re.match(r"^\w+ -+> CU\d+", linea):
                    problemas.append(f"{nombre}: la asociación actor-caso no lleva flecha: {linea}")
                if re.match(r"^CU\d+ \.+> CU\d+", linea) and not re.search(
                        r"<<(include|extend)>>", linea):
                    problemas.append(f"{nombre}: relación entre casos sin «include» o «extend».")
        imagen = fuente.with_suffix(".png")
        if imagen.exists():
            problemas += _revisar_tamanio(imagen)
    return problemas


def _revisar_despliegue(nombre, texto):
    """En UML, cada nodo lleva su estereotipo y cada ruta de comunicación, su protocolo."""
    problemas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if linea.startswith("node ") and "<<" not in linea:
            problemas.append(f"{nombre}: nodo sin estereotipo: {linea}")
        if re.match(r"^\w+ [-.]+(\w+[-.]+)?> \w+", linea) and ":" not in linea:
            problemas.append(f"{nombre}: ruta de comunicación sin protocolo: {linea}")
    return problemas


def _revisar_tamanio(imagen):
    """Una imagen en el límite de PlantUML está recortada; una muy alargada no se lee."""
    with imagen.open("rb") as archivo:
        cabecera = archivo.read(24)
    ancho = int.from_bytes(cabecera[16:20], "big")
    alto = int.from_bytes(cabecera[20:24], "big")
    problemas = []
    if max(ancho, alto) >= LIMITE_PLANTUML:
        problemas.append(f"{imagen.name}: {ancho}×{alto} px, recortada por el límite de PlantUML.")
    if ancho / alto > 4 or alto / ancho > 4:
        problemas.append(f"{imagen.name}: {ancho}×{alto} px, demasiado alargada para una página.")
    return problemas


def renderizar(carpeta=DIAGRAMAS):
    """Exporta a PNG cada .puml de la carpeta con PlantUML y Graphviz."""
    if not shutil.which("java") or not shutil.which("dot"):
        raise RuntimeError("Hacen falta Java y Graphviz (dot) para renderizar.")
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "plantuml"
    jar = cache / f"plantuml-{VERSION_PLANTUML}.jar"
    if not jar.exists():
        cache.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL_PLANTUML, jar)  # nosec: versión fija de Maven
    fuentes = sorted(str(p) for p in carpeta.glob("*.puml"))
    entorno = dict(os.environ, PLANTUML_LIMIT_SIZE="12000")
    subprocess.run(["java", "-jar", str(jar), "-tpng", "-Sdpi=170", *fuentes], check=True,
                   env=entorno)
    for fuente in carpeta.glob("*.puml"):
        nombre = re.search(r"@start\w+\s+(\S+)", fuente.read_text(encoding="utf-8"))
        generada = carpeta / f"{nombre.group(1)}.png" if nombre else None
        if generada and generada.exists() and generada != fuente.with_suffix(".png"):
            generada.replace(fuente.with_suffix(".png"))


def main(argumentos=None):
    """Punto de entrada por línea de comandos."""
    analizador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = analizador.add_subparsers(dest="accion", required=True)
    er = sub.add_parser("er", help="Diagrama entidad-relación desde los modelos")
    er.add_argument("--compacto", action="store_true", help="Solo claves y columnas únicas")
    sub.add_parser("componentes", help="Diagrama de componentes desde el código")
    sub.add_parser("casos-de-uso", help="Escribe los diagramas de casos de uso por módulo")
    sub.add_parser("verificar", help="Comprobar que los diagramas coincidan con el sistema")
    sub.add_parser("renderizar", help="Exportar los .puml a PNG")
    opciones = analizador.parse_args(argumentos)
    if opciones.accion == "er":
        sys.stdout.write(generar_er(leer_modelos(), opciones.compacto))
    elif opciones.accion == "componentes":
        sys.stdout.write(generar_componentes(leer_estrategias()))
    elif opciones.accion == "casos-de-uso":
        for nombre, contenido in diagramas_de_casos_de_uso().items():
            (DIAGRAMAS / nombre).write_text(contenido, encoding="utf-8")
            print(f"Escrito {nombre}")
    elif opciones.accion == "verificar":
        problemas = verificar()
        for problema in problemas:
            print(f"- {problema}")
        print("Los diagramas coinciden con el sistema." if not problemas else "")
        return 1 if problemas else 0
    else:
        renderizar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
