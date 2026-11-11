"""Diagrama de despliegue UML dibujado con posiciones fijas (funcionalidad 039).

El diagrama de despliegue tiene nodos anidados (nube, servidor, sistema
operativo, entornos de ejecución) y muchas rutas de comunicación hacia
servicios externos. Con disposición automática (PlantUML y Graphviz) las
rutas salen en abanico y cruzan los rótulos de los marcos. Por eso este
diagrama se dibuja como lo haría una persona en una herramienta de
diagramas: cada nodo tiene su lugar en una grilla, las rutas son
ortogonales y ninguna se cruza con otra ni con un rótulo.

Los datos de la infraestructura (tipo de instancia, región, sistema
operativo, puertos y servicios de systemd) se leen de los archivos de
``infraestructura/`` con ``datos_de_infraestructura`` y se escriben en el
dibujo; ``diagramas_del_sistema.py verificar`` comprueba que estén.

Uso, desde ``backend/``::

    python herramientas/diagrama_despliegue.py

Escribe ``docs/arquitectura/diagramas/07-despliegue-uml.svg``.

Realiza: RNF19 (trazabilidad del diseño); funcionalidad 039.
"""
import sys
from html import escape

try:  # importado como paquete (pruebas) o ejecutado como guion desde backend/
    from herramientas.diagramas_del_sistema import DIAGRAMAS, datos_de_infraestructura
except ImportError:
    from diagramas_del_sistema import DIAGRAMAS, datos_de_infraestructura

FUENTE = "Arial, Helvetica, sans-serif"
TRAZO = "#333333"
PROFUNDIDAD = 12
ANCHO, ALTO = 1990, 1070


# Las primitivas de dibujo reciben posición, tamaño y rótulos: son muchos
# argumentos por naturaleza, igual que en cualquier biblioteca gráfica.
# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
class Lienzo:
    """Acumula los elementos SVG del diagrama, con primitivas de notación UML."""

    def __init__(self):
        """Crea un lienzo vacío."""
        self.elementos = []

    def texto(self, x, y, contenido, tamanio=14, negrita=False, ancla="middle", cursiva=False):
        """Escribe una línea de texto centrada (o alineada) en ``x``."""
        estilo = (' font-weight="bold"' if negrita else "") + (
            ' font-style="italic"' if cursiva else "")
        self.elementos.append(
            f'<text x="{x}" y="{y}" font-family="{FUENTE}" font-size="{tamanio}" '
            f'text-anchor="{ancla}" fill="#111111"{estilo}>{escape(contenido)}</text>')

    def nodo(self, x, y, ancho, alto, estereotipo, nombre, discontinuo=False, relleno="#FFFFFF"):
        """Nodo UML: una caja con volumen (cara superior y lateral) y su rótulo arriba."""
        d = PROFUNDIDAD
        guion = ' stroke-dasharray="7 5"' if discontinuo else ""
        trazo = f'stroke="{TRAZO}" stroke-width="1.3"{guion}'
        self.elementos += [
            f'<polygon points="{x},{y} {x + d},{y - d} {x + ancho + d},{y - d} {x + ancho},{y}" '
            f'fill="#F2F2F2" {trazo}/>',
            f'<polygon points="{x + ancho},{y} {x + ancho + d},{y - d} {x + ancho + d},'
            f'{y + alto - d} {x + ancho},{y + alto}" fill="#E6E6E6" {trazo}/>',
            f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" fill="{relleno}" {trazo}/>',
        ]
        centro = x + ancho / 2
        self.texto(centro, y + 20, f"«{estereotipo}»", 13)
        for i, linea in enumerate(nombre.split("\n")):
            self.texto(centro, y + 38 + 17 * i, linea, 14, negrita=True)

    def artefacto(self, x, y, ancho, alto, nombre):
        """Artefacto UML: rectángulo con el ícono de documento en la esquina."""
        self.elementos.append(f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" '
                              f'fill="#FFFFFF" stroke="#555555" stroke-width="1"/>')
        ix, iy = x + ancho - 20, y + 7
        self.elementos.append(
            f'<path d="M{ix},{iy} h8 l5,5 v12 h-13 z M{ix + 8},{iy} v5 h5" fill="none" '
            'stroke="#555555" stroke-width="1"/>')
        lineas = nombre.split("\n")
        inicio = y + alto / 2 - 8 * (len(lineas) - 1) + 5
        for i, linea in enumerate(lineas):
            self.texto(x + ancho / 2 - 8, inicio + 16 * i, linea, 13)

    def base_de_datos(self, x, y, ancho, alto, nombre):
        """Base de datos: cilindro con su nombre."""
        r = 9
        self.elementos += [
            f'<path d="M{x},{y + r} v{alto - 2 * r} a{ancho / 2},{r} 0 0 0 {ancho},0 '
            f'v-{alto - 2 * r}" fill="#FFFFFF" stroke="{TRAZO}" stroke-width="1.3"/>',
            f'<ellipse cx="{x + ancho / 2}" cy="{y + r}" rx="{ancho / 2}" ry="{r}" '
            f'fill="#FFFFFF" stroke="{TRAZO}" stroke-width="1.3"/>',
        ]
        self.texto(x + ancho / 2, y + alto / 2 + 10, nombre, 14)

    def ruta(self, puntos, rotulo="", donde=0, lado="arriba", discontinua=False):
        """Ruta de comunicación ortogonal con punta de flecha y rótulo con fondo blanco.

        ``donde`` es el índice del tramo que lleva el rótulo; ``lado`` lo
        ubica arriba del tramo (horizontal) o a su derecha (vertical).
        """
        guion = ' stroke-dasharray="7 5"' if discontinua else ""
        camino = " ".join(f"{px},{py}" for px, py in puntos)
        self.elementos.append(f'<polyline points="{camino}" fill="none" stroke="{TRAZO}" '
                              f'stroke-width="1.3"{guion} marker-end="url(#punta)"/>')
        if not rotulo:
            return
        (x1, y1), (x2, y2) = puntos[donde], puntos[donde + 1]
        lineas = rotulo.split("\n")
        if y1 == y2:
            cx, cy, ancla = (x1 + x2) / 2, y1 - 8 - 16 * (len(lineas) - 1), "middle"
        elif lado == "izquierda":
            cx, cy, ancla = x1 - 8, (y1 + y2) / 2 - 8 * (len(lineas) - 1) + 5, "end"
        else:
            cx, cy, ancla = x1 + 8, (y1 + y2) / 2 - 8 * (len(lineas) - 1) + 5, "start"
        largo = max(len(linea) for linea in lineas) * 7.2 + 8
        fx = {"middle": cx - largo / 2, "start": cx - 4, "end": cx - largo + 4}[ancla]
        self.elementos.append(f'<rect x="{fx}" y="{cy - 14}" width="{largo}" '
                              f'height="{16 * len(lineas) + 2}" fill="#FFFFFF"/>')
        for i, linea in enumerate(lineas):
            self.texto(cx, cy + 16 * i, linea, 13, ancla=ancla)

    def svg(self):
        """Documento SVG completo."""
        punta = ('<marker id="punta" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" '
                 'markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" '
                 f'fill="none" stroke="{TRAZO}" stroke-width="1.4"/></marker>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{ALTO}" '
                f'viewBox="0 0 {ANCHO} {ALTO}"><defs>{punta}</defs>'
                f'<rect width="{ANCHO}" height="{ALTO}" fill="#FFFFFF"/>'
                + "".join(self.elementos) + "</svg>\n")


def generar_despliegue(datos=None):
    """Dibuja el diagrama de despliegue con los datos reales de la infraestructura."""
    datos = datos or datos_de_infraestructura()
    tipo = datos.get("tipo de instancia", "t3.small")
    region = datos.get("región", "eu-west-1")
    ubuntu = datos.get("sistema operativo", "24.04")
    puerto = datos.get("puerto de Gunicorn", "8000")
    https = datos.get("puerto HTTPS", "443")
    li = Lienzo()

    # Dispositivo del usuario y Clarity, a la izquierda.
    li.nodo(40, 190, 320, 230, "device", "Computadora o celular\ndel usuario")
    li.nodo(62, 262, 266, 140, "executionEnvironment", "Navegador web")
    li.artefacto(84, 322, 222, 56, "Interfaz React\n(aplicación de una página)")
    li.nodo(60, 610, 270, 70, "external system", "Microsoft Clarity")

    # Nube de AWS con el servidor y sus servicios.
    li.nodo(420, 50, 1200, 990, "cloud", f"Amazon Web Services · región {region} (Irlanda)",
            relleno="#FAFAFA")
    li.nodo(450, 120, 790, 900, "device", f"Amazon EC2 {tipo}")
    li.nodo(472, 186, 740, 814, "executionEnvironment", f"Ubuntu Server {ubuntu}")

    li.nodo(500, 260, 220, 140, "executionEnvironment", f"Nginx (TLS, puerto {https})")
    li.artefacto(518, 318, 184, 56, "frontend/dist\n(archivos estáticos)")
    li.nodo(800, 260, 240, 140, "executionEnvironment",
            f"Gunicorn · Python 3.12\n(127.0.0.1:{puerto})")
    li.artefacto(830, 334, 180, 50, "API REST Flask\n(wsgi.py)")
    li.nodo(800, 480, 240, 120, "executionEnvironment", "Trabajador de análisis (RQ)")
    li.artefacto(840, 538, 160, 40, "trabajador.py")
    li.base_de_datos(1090, 405, 100, 70, "Redis")
    li.base_de_datos(870, 690, 100, 70, "PostgreSQL")
    li.nodo(500, 830, 690, 150, "executionEnvironment", "systemd (tareas programadas)")
    li.artefacto(518, 900, 212, 56, "plataforma-sellos.timer\n(sellos en Hedera)")
    li.artefacto(742, 900, 212, 56, "plataforma-retencion.timer\n(retención de los casos)")
    li.artefacto(966, 900, 212, 56, "plataforma-respaldo.timer\n(respaldo de PostgreSQL)")

    li.nodo(1360, 120, 220, 220, "cloud service", "Amazon S3")
    li.artefacto(1374, 186, 192, 56, "imágenes e informes\n(cifrados, versionados)")
    li.artefacto(1374, 258, 192, 56, "respaldos y artefactos\nde despliegue")
    li.nodo(1360, 400, 220, 70, "cloud service", "Amazon SES")
    li.nodo(1360, 530, 220, 86, "cloud service", "Parameter Store\n(AWS Systems Manager)")

    # Sistemas externos, debajo de los servicios de AWS y fuera de la nube.
    externos = [(680, "Google Identity", "HTTPS (OIDC + PKCE)", False),
                (780, "Hedera Consensus Service", "gRPC · HTTPS (mirror node)", False),
                (880, "Cresium", "«previsto» HTTPS", True),
                (980, "Identik", "«previsto» HTTPS", True)]
    for y, nombre, protocolo, previsto in externos:
        li.nodo(1710, y - 35, 250, 70, "external system", nombre, discontinuo=previsto)

    # Rutas de comunicación.
    li.ruta([(328, 300), (500, 300)], f"HTTPS (TLS · {https})")
    li.ruta([(195, 402), (195, 610)], "HTTPS\n(período de prueba)", lado="derecha",
            discontinua=True)
    li.ruta([(720, 300), (800, 300)], "HTTP local")
    li.ruta([(1040, 300), (1140, 300), (1140, 405)], "TCP 6379")
    li.ruta([(1040, 540), (1140, 540), (1140, 475)], "TCP 6379")
    li.ruta([(800, 380), (770, 380), (770, 725), (870, 725)], "TCP 5432", donde=1,
            lado="izquierda")
    li.ruta([(920, 600), (920, 690)], "TCP 5432")
    li.ruta([(920, 830), (920, 760)], "TCP 5432")
    li.ruta([(1252, 230), (1360, 230)], "HTTPS")
    li.ruta([(1252, 435), (1360, 435)], "SMTP +\nSTARTTLS")
    li.ruta([(1252, 573), (1360, 573)], "HTTPS")
    for y, _, protocolo, previsto in externos:
        li.ruta([(1252, y), (1710, y)], protocolo, discontinua=previsto)
    return li.svg()


def main():
    """Escribe el SVG en la carpeta de diagramas."""
    destino = DIAGRAMAS / "07-despliegue-uml.svg"
    destino.write_text(generar_despliegue(), encoding="utf-8")
    sys.stdout.write(f"{destino}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
