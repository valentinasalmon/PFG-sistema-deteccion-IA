"""Salida JSON de la verificación pública de un informe (funcionalidad 026).

Solo datos para comprobar el documento: nunca datos del caso.

Realiza: RF55 (CA3).
"""
from app.integraciones.sello_tiempo import enlace_explorador


def informe_verificado_a_dict(informe):
    """Fecha, huella del PDF y sello en Hedera de un informe."""
    sellado = informe.sello_estado == "sellado"
    return {
        "generado_en": informe.generado_en.isoformat(timespec="seconds"),
        "huella": informe.huella,
        "sello": {
            "estado": informe.sello_estado,
            "referencia": informe.sello_referencia if sellado else None,
            "fecha": informe.sello_fecha.isoformat(timespec="seconds")
            if sellado and informe.sello_fecha else None,
            "simulado": informe.sello_simulado,
            "enlace": enlace_explorador(informe.sello_recibo) if sellado else None,
        },
    }
