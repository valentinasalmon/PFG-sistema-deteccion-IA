"""Salida JSON de la verificación pública de un informe (funcionalidad 026).

Solo datos para comprobar el documento: nunca datos del caso.

Realiza: RF55 (CA3).
"""
from app.integraciones.sello_tiempo import enlace_explorador


def _sello(objeto):
    sellado = objeto.sello_estado == "sellado"
    return {
        "estado": objeto.sello_estado,
        "referencia": objeto.sello_referencia if sellado else None,
        "fecha": objeto.sello_fecha.isoformat(timespec="seconds")
        if sellado and objeto.sello_fecha else None,
        "simulado": objeto.sello_simulado,
        "enlace": enlace_explorador(objeto.sello_recibo) if sellado else None,
    }


def informe_verificado_a_dict(informe, version=None):
    """Fecha, huella del PDF y sello en Hedera de un informe, y la versión que lo analizó (029)."""
    return {
        "generado_en": informe.generado_en.isoformat(timespec="seconds"),
        "huella": informe.huella,
        "sello": _sello(informe),
        "version": {
            "numero": version.version, "commit": version.commit[:7],
            "huella": version.huella, "sello": _sello(version),
        } if version is not None else None,
    }
