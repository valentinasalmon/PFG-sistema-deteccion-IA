# 049 · Cobro del plan con Mercado Pago

**Estado**: especificada (2026-11-23). **Rama**: `integraciones/mercado-pago`. **Pedido**: la autora: cambiar Cresium por Mercado Pago, y mantener el botón para simular el pago, «porque no voy a estar pagando cada vez que necesite mostrar».

## Problema

El cobro del plan (032) se diseñó para Cresium: una transferencia a un CVU con un aviso cuando se acredita. Como no hubo acceso a su API, siempre funcionó simulado. Mercado Pago es más conocido en Argentina, acepta tarjeta, dinero en cuenta y transferencia, y tiene un modo de prueba completo.

## Alcance

- **Nuevo proveedor `mercado_pago`** detrás de la misma interfaz intercambiable (ADR-0020): el cobro crea una orden de Checkout Pro con la **API de Orders** (Mercado Pago marcó Preferences como heredada), la persona paga en la pantalla de Mercado Pago y vuelve a la plataforma; el pago se acredita con el **aviso firmado** (*webhook*), nunca con la vuelta del navegador.
- **La interfaz del proveedor admite los dos estilos**: transferencia (datos para copiar, como Cresium) y redirección (botón «Pagar con Mercado Pago»).
- **El botón «Simular pago» se mantiene** para mostrar la plataforma sin pagar. Queda visible solo cuando la configuración lo habilita (`PERMITIR_SIMULAR_PAGO`), también en producción mientras la autora lo necesite, y queda registrado en la auditoría que el pago fue simulado.
- **Seguridad**: la firma del aviso se valida con la clave secreta antes de mirar su contenido; el estado del pago se confirma consultando la orden a Mercado Pago con el token del servidor; un aviso repetido no acredita dos veces. El token y la clave viven en Parameter Store (`MERCADO_PAGO_TOKEN`, `MERCADO_PAGO_SECRETO_AVISOS`), nunca en el repositorio ni en el frontend.
- **Estado en `/estado`**: si Mercado Pago responde con el token configurado.
- Cresium queda como proveedor alternativo (simulado), sin borrarlo.

## Criterios de aceptación

- [ ] **CA1**: Al pagar un plan, la persona va a Mercado Pago (modo de prueba) y vuelve a la plataforma; el plan queda pagado solo cuando llega el aviso firmado y la orden consultada figura como pagada.
- [ ] **CA2**: Un aviso con firma inválida se rechaza sin cambiar nada; uno repetido no acredita dos veces.
- [ ] **CA3**: Con `PERMITIR_SIMULAR_PAGO` activo, el botón «Simular pago» acredita el cobro y la auditoría lo marca como simulado; desactivado, no aparece y la ruta lo rechaza.
- [ ] **CA4**: Probado contra el modo de prueba real de Mercado Pago con una cuenta compradora de prueba (pago aprobado y rechazado), por la autora con una guía.
- [ ] **CA5**: Pruebas automáticas del proveedor (sin red), del aviso y de las pantallas; sensores y recorridos en computadora y celular.

## Pendiente para implementar

La documentación oficial de Mercado Pago (Orders y firma de los avisos) tiene que estar a la vista al escribir el proveedor: el entorno del agente todavía no puede abrir `www.mercadopago.com.ar` aunque la autora aprobó el permiso.
