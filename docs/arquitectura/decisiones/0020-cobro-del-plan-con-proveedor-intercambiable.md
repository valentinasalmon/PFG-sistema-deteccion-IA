# ADR-0020: Cobro del plan por transferencia, con un proveedor de pagos intercambiable

- **Estado**: Aceptada (decisión de la autora, 2026-10-29)
- **Fecha**: 2026-10-29
- **Requisitos relacionados**: RF10, RF20; CP-01, CP-34

## Contexto

La autora decidió que el plan de un estudio jurídico o de una aseguradora se pague **al registrarse**, y que el cobro sea con **Cresium**, una *fintech* argentina con cuenta empresa que cobra por transferencia a un CVU y concilia los pagos de forma automática.

No se encontró documentación pública de su API ni un entorno de pruebas, y los precios de los planes todavía no están definidos.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Esperar la API de Cresium para implementar el pago | Cobro real desde el primer día | Bloquea el registro nuevo, que se quiere mostrar antes de la entrega |
| Mantener el pago simulado de la 014 (aplicar el plan al instante) | Ya está hecho | No muestra cómo se paga ni el orden pago → aprobación que pidió la autora |
| **Modelar el cobro real (CVU, alias, referencia, estado) y simular solo la acreditación, detrás de una interfaz de proveedor** | Las pantallas, los estados y la auditoría son los definitivos; cambiar al cobro real toca solo el proveedor | Hay que mantener un botón de simulación hasta tener la API |

## Decisión

1. **Cada pago es un `Cobro`** con referencia legible (`EVD-XXXXXX`), CVU, alias, plan, motivo (alta o cambio de plan) y estado (pendiente, acreditado o devuelto). Del enlace de la página de pago se guarda solo la huella SHA-256 del token.
2. **La organización espera el pago** en el estado `pago_pendiente`. Al acreditarse, el estudio pasa a activo y la aseguradora a pendiente de aprobación; si se rechaza, el cobro se devuelve.
3. **El proveedor es intercambiable** (`integraciones/pagos.py`, variable `PROVEEDOR_PAGOS`), como el sello de tiempo (ADR-0018). Hoy, `ProveedorPagosSimulado` arma datos de ejemplo y permite «Simular la transferencia». El de Cresium recibirá su aviso de acreditación (*webhook*) y no permitirá simular.
4. **No se revela si un correo existe**: con un correo ya registrado se crea un cobro sin organización, y la respuesta y la pantalla de pago son iguales (RF01 CA3).

## Consecuencias

- El registro, la creación del estudio y el cambio de plan ya tienen su forma final.
- Para cobrar de verdad falta implementar el proveedor de Cresium, su *webhook* con verificación de firma y los precios.
- La auditoría distingue los pagos simulados (`"simulado": true`).
