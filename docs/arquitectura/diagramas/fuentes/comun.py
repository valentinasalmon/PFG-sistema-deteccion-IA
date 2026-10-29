"""Ayudas para dibujar diagramas SVG con la identidad de evidentIA."""
TINTA, TINTA2, AZUL, BOSQUE, LIMA, FONDO = "#14201A", "#4E5B54", "#2F5DA8", "#17291F", "#A4CB3E", "#F3F5F4"
CELESTE, LIMA_CLARO, BLANCO = "#EAF0F9", "#F4F8E8", "#FFFFFF"
FUENTE = "Arial, Helvetica, sans-serif"

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inicio(w, h):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FUENTE}">',
            '<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{TINTA2}"/></marker></defs>',
            f'<rect width="{w}" height="{h}" fill="{BLANCO}"/>']

def panel(x, y, w, h, titulo, oscuro=False):
    banda = BOSQUE if oscuro else "#DDE3E0"
    color = BLANCO if oscuro else TINTA
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{FONDO}" stroke="#C9D1CD" stroke-width="1.5"/>'
            f'<path d="M{x},{y+14} a14,14 0 0 1 14,-14 h{w-28} a14,14 0 0 1 14,14 v32 h-{w} z" fill="{banda}"/>'
            f'<rect x="{x}" y="{y+44}" width="{w}" height="4" fill="{LIMA}"/>'
            f'<text x="{x+w/2}" y="{y+29}" text-anchor="middle" font-size="16" font-weight="700" letter-spacing="1.2" fill="{color}">{esc(titulo)}</text>')

def caja(x, y, w, h, titulo, lineas=(), relleno=BLANCO, borde=AZUL, tam=18, acento=True, dy=0):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{relleno}" stroke="{borde}" stroke-width="1.8"/>']
    if acento:
        s.append(f'<rect x="{x}" y="{y+10}" width="5" height="{h-20}" rx="2" fill="{borde}"/>')
    n = len(lineas)
    alto = tam + 6 + n * 21
    y0 = y + (h - alto) / 2 + tam + dy
    s.append(f'<text x="{x+w/2}" y="{y0}" text-anchor="middle" font-size="{tam}" font-weight="700" fill="{TINTA}">{esc(titulo)}</text>')
    for i, l in enumerate(lineas):
        s.append(f'<text x="{x+w/2}" y="{y0+8+21*(i+1)}" text-anchor="middle" font-size="15" fill="{TINTA2}">{esc(l)}</text>')
    return "".join(s)

def cilindro(x, y, w, h, titulo, lineas=()):
    e = 14
    s = [f'<path d="M{x},{y+e} a{w/2},{e} 0 0 1 {w},0 v{h-2*e} a{w/2},{e} 0 0 1 -{w},0 z" fill="{CELESTE}" stroke="{AZUL}" stroke-width="1.8"/>',
         f'<ellipse cx="{x+w/2}" cy="{y+e}" rx="{w/2}" ry="{e}" fill="#DCE6F5" stroke="{AZUL}" stroke-width="1.8"/>']
    n = len(lineas)
    y0 = y + e + (h - e - (24 + n * 21)) / 2 + 18
    s.append(f'<text x="{x+w/2}" y="{y0}" text-anchor="middle" font-size="18" font-weight="700" fill="{TINTA}">{esc(titulo)}</text>')
    for i, l in enumerate(lineas):
        s.append(f'<text x="{x+w/2}" y="{y0+6+21*(i+1)}" text-anchor="middle" font-size="15" fill="{TINTA2}">{esc(l)}</text>')
    return "".join(s)

def chip(x, y, w, h, texto, relleno=LIMA_CLARO, borde=LIMA):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{relleno}" stroke="{borde}" stroke-width="1.4"/>'
            f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-size="14.5" fill="{TINTA}">{esc(texto)}</text>')

def linea(puntos, flecha=True, punteada=False, color=TINTA2, ancho=2):
    d = "M" + " L".join(f"{a},{b}" for a, b in puntos)
    extra = ' marker-end="url(#f)"' if flecha else ""
    guion = ' stroke-dasharray="7 5"' if punteada else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}"{extra}{guion}/>'

def etiqueta(x, y, texto, ancla="middle"):
    w = len(texto) * 7.6 + 14
    x0 = x - w / 2 if ancla == "middle" else (x if ancla == "start" else x - w)
    return (f'<rect x="{x0}" y="{y-15}" width="{w}" height="22" rx="11" fill="{BLANCO}" stroke="#C9D1CD"/>'
            f'<text x="{x0+w/2}" y="{y+1}" text-anchor="middle" font-size="13.5" font-style="italic" fill="{TINTA2}">{esc(texto)}</text>')

def persona(cx, cy, color=AZUL):
    return (f'<circle cx="{cx}" cy="{cy-7}" r="7" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<path d="M{cx-12},{cy+13} a12,11 0 0 1 24,0" fill="none" stroke="{color}" stroke-width="2"/>')

def fin(s):
    return "\n".join(s + ["</svg>"])
