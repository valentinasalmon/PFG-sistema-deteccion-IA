"""Proveedores de verificación de identidad (funcionalidad 035, CP-35).

La verificación real será con Identik: el Referente de la aseguradora entra a
una página del proveedor, valida su DNI (y, si corresponde, una selfie con
prueba de vida) y el proveedor avisa el resultado a la plataforma. Como
todavía no hay acceso a su API de verificación ni a un entorno de pruebas, el
proveedor disponible es ``ProveedorIdentidadSimulado``, que arma la misma
forma de datos con una página propia donde se simula el resultado.

Cambiar de proveedor no toca los servicios ni las pantallas: alcanza con otra
clase con la misma interfaz y la variable ``VERIFICACION_IDENTIDAD``. Igual
que el cobro (ADR-0020).

Ningún proveedor le entrega a la plataforma imágenes ni datos biométricos:
solo el resultado (RN41).

Realiza: RN41; RF12; CP-35.
"""
import hashlib

PROVEEDOR_SIMULADO = "identidad_simulada"


class ProveedorIdentidadSimulado:
    """Verificación simulada: la página de la propia plataforma permite elegir el resultado.

    No verifica nada: sirve para desarrollar y para mostrar el flujo
    completo. La interfaz lo aclara en la página de verificación.
    """

    nombre = PROVEEDOR_SIMULADO
    nombre_visible = "Verificación simulada"
    permite_simular = True

    def __init__(self, url_frontend):
        self.url_frontend = url_frontend.rstrip("/")

    def iniciar(self, token, referente):  # pylint: disable=unused-argument
        """Datos para empezar la verificación: dónde completarla y la referencia del proveedor.

        Args:
            token: token del enlace (la plataforma guarda solo su huella).
            referente: el ``Usuario`` que verifica su identidad.

        Returns:
            ``{"url": ..., "referencia": ...}``.
        """
        referencia = "SIM-" + hashlib.sha256(token.encode()).hexdigest()[:10].upper()
        return {"url": f"{self.url_frontend}/identidad/{token}", "referencia": referencia}


def crear_proveedor_identidad(configuracion):
    """Proveedor según ``VERIFICACION_IDENTIDAD``: ``simulado``, o None si está desactivada.

    ``identik`` se suma cuando Identik envíe la documentación de verificación
    de identidad y el entorno de pruebas (CP-35).
    """
    modo = configuracion.get("VERIFICACION_IDENTIDAD", "desactivado")
    if modo == "desactivado":
        return None
    if modo == "simulado":
        return ProveedorIdentidadSimulado(configuracion.get("URL_FRONTEND", ""))
    raise ValueError(f"Proveedor de verificación de identidad desconocido: {modo}")
