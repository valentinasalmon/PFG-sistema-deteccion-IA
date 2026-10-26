"""Códigos QR en SVG para los enlaces de carga desde el celular (funcionalidad 024).

Se generan en el servidor con ``segno`` (Python puro, sin dependencias) y se
entregan como ``data:`` URI, que la política de seguridad de contenido ya
admite para imágenes.

Realiza: RF53 (CA2).
"""
import segno


def qr_svg(texto):
    """``data:image/svg+xml`` con el QR de ``texto``, en tinta de la marca sobre blanco."""
    return segno.make(texto, error="m").svg_data_uri(scale=6, border=2, dark="#14201A")
