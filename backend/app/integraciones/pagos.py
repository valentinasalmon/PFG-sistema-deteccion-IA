"""Proveedores de pago del plan (funcionalidad 032, ADR-0020).

El cobro real será con Cresium: una transferencia a un CVU, con una
referencia que identifica el pago y un aviso (*webhook*) cuando se acredita.
Como todavía no hay acceso a su API ni a un entorno de pruebas, el proveedor
por defecto es ``ProveedorPagosSimulado``, que arma datos de cobro con la
misma forma y permite simular la acreditación desde la pantalla.

Cambiar de proveedor no toca los servicios ni las pantallas: alcanza con otra
clase con la misma interfaz y la variable ``PROVEEDOR_PAGOS``.

Realiza: RF20 (CA2); CP-01, CP-34.
"""
import hashlib

PROVEEDOR_SIMULADO = "cresium_simulado"


class ProveedorPagosSimulado:
    """Cobro por transferencia simulado, con la forma de los cobros de Cresium.

    El CVU y el alias son de ejemplo y se derivan de la referencia: no
    corresponden a ninguna cuenta real y nadie puede transferirles.
    """

    nombre = PROVEEDOR_SIMULADO
    nombre_visible = "Cresium (simulado)"
    permite_simular = True
    titular = "evidentIA (cuenta de cobro de prueba)"

    def datos_de_cobro(self, referencia):
        """CVU y alias de ejemplo para la referencia del cobro."""
        digitos = str(int(hashlib.sha256(referencia.encode()).hexdigest(), 16))[:14]
        return {
            "cvu": f"00000031{digitos}",
            "alias": f"EVIDENTIA.{referencia.replace('-', '.')}",
        }


def crear_proveedor_pagos(configuracion):
    """Proveedor de pagos según ``PROVEEDOR_PAGOS`` (hoy, solo el simulado)."""
    nombre = configuracion.get("PROVEEDOR_PAGOS", PROVEEDOR_SIMULADO)
    if nombre != PROVEEDOR_SIMULADO:
        raise ValueError(f"Proveedor de pagos desconocido: {nombre}")
    return ProveedorPagosSimulado()
