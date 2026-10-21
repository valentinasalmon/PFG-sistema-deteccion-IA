"""Salida JSON de las imágenes de los casos.

Realiza: RF35 (CA1).
"""


def imagen_a_dict(imagen, enlace_miniatura, analizada=False):
    """Imagen con sus datos técnicos, el enlace firmado de su vista previa y si ya se analizó."""
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
        "analizada": analizada,
        "miniatura": enlace_miniatura,
        "sello": {
            "estado": imagen.sello_estado,
            "referencia": imagen.sello_referencia,
            "fecha": imagen.sello_fecha.isoformat() if imagen.sello_fecha else None,
            "simulado": imagen.sello_simulado,
            # El navegador lo necesita para confirmar el sello en BFA (modo navegador).
            "recibo": imagen.sello_recibo if imagen.sello_estado == "enviado" else None,
        },
    }
