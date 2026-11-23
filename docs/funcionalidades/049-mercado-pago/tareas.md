# 049 · Tareas

- [x] **T01**: interfaz del proveedor con `estilo` (transferencia o redirección) y botón «Simular pago» detrás de `PERMITIR_SIMULAR_PAGO` (activo por defecto; con el proveedor simulado siempre se puede). Pruebas en `pruebas/unitarias/test_simular_pago.py`. *Decisión del agente*: el valor por defecto es «si» porque la autora pidió conservar el botón para las demostraciones; se apaga con `PERMITIR_SIMULAR_PAGO=no` en Parameter Store.
- [ ] **T02**: proveedor `mercado_pago` con la API de Orders (crear y consultar la orden). Espera poder leer la documentación oficial desde el entorno del agente.
- [ ] **T03**: ruta del aviso firmado `/api/pagos/mercado-pago/aviso` (firma, consulta de la orden, idempotencia).
- [ ] **T04**: botón «Pagar con Mercado Pago» en `PanelPago` para el estilo redirección y la vuelta a la plataforma.
- [ ] **T05**: estado de Mercado Pago en `/estado` y `PROVEEDOR_PAGOS=mercado_pago` en producción.
- [ ] **T06**: prueba real en el modo de prueba con una cuenta compradora (la autora, con guía).
