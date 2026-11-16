# 043 · Uso con teclado y plan B del DNS

**Estado**: implementada (2026-11-16). **Rama**: `funcionalidad/043-teclado-y-dns`. **Pedido**: pendientes del agente mientras se propaga el dominio.

## Problema

- El sensor de accesibilidad de la 041 revisa la estructura de las pantallas, pero no si se pueden usar solo con el teclado (RNF11; WCAG 2.1.1, 2.1.2 y 2.4.7).
- La delegación de `evidentiaa.com.ar` a Route 53 no avanzaba en NIC Argentina; si se traba, hace falta poder cargar los registros a mano en DonWeb sin buscarlos en la consola de AWS.

## Alcance

- Sensor `frontend/e2e/teclado.cjs` en la integración continua.
- Salida de Terraform `registros_dns` con los cinco registros (A, tres DKIM y DMARC) y «Plan B» en la guía de despliegue.

## Criterios de aceptación

- [x] **CA1**: En 9 pantallas (públicas y con sesión), todo elemento con foco tiene indicador visible y el foco nunca queda atrapado.
- [x] **CA2**: Se puede iniciar sesión solo con el teclado.
- [x] **CA3**: El sensor falla si se quita el contorno de foco (comprobado).
- [x] **CA4**: `terraform output registros_dns` lista los registros para cargar a mano.
