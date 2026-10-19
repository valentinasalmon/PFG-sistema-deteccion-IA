"""Salida JSON de las imágenes de los casos.

Realiza: RF35 (CA1).
"""


def imagen_a_dict(imagen, enlace_miniatura):
    """Imagen con sus datos técnicos y el enlace firmado de su vista previa."""
    usuario = imagen.usuario
    return {
        "id": imagen.id,
        "nombre": imagen.nombre_original,
        "formato": imagen.formato.upper(),
        "tamanio": imagen.tamanio,
        "ancho": imagen.ancho,
        "alto": imagen.alto,
        "huella": imagen.huella,
        "cargada_en": imagen.cargada_en.isoformat(),
        "cargada_por": f"{usuario.nombre} {usuario.apellido}" if usuario else "Cuenta eliminada",
        "en_informe": imagen.en_informe,
        "miniatura": enlace_miniatura,
    }
