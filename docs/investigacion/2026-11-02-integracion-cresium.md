# Integración del cobro real con Cresium (2026-11-02)

Investigación pedida por la autora: cómo pasar del cobro simulado de la funcionalidad 032 (ADR-0020) al cobro real con Cresium.

## 1. Qué se sabe (con fuente)

Fuente: búsqueda web del 2026-11-02. Desde el entorno del agente **no se pudo abrir** `cresium.com` ni `docs.cresium.com` (el proxy no resuelve esos dominios), así que lo que sigue sale de los resúmenes de los buscadores y hay que confirmarlo en la documentación oficial.

- **Hay una API pública para empresas**, documentada en `docs.cresium.com` ([página de APIs](https://cresium.com/productos/apis)). Cubre:
  - saldos y movimientos;
  - transferencias, con validación previa de CBU, CVU y alias y un modo *preview*;
  - **cobros con CVU**: se puede emitir un CVU propio por pedido, por factura o por cliente;
  - **webhooks firmados con HMAC-SHA256**, que avisan cuando entra un cobro, sin tener que consultar a cada rato.
- **Credenciales**: se generan desde el panel, en `cresium.app` → Configuración → Desarrolladores.
- **También ofrece un servidor MCP**, para operar la cuenta desde un asistente.
- **Quiénes pueden transferir**: la cuenta virtual recibe fondos desde cualquier CBU o CVU, del titular o de terceros ([términos](https://cresium.com/terminos)).
- **Empresa**: *fintech* argentina para pymes, con cuenta empresa en pesos y dólares, eCheqs, cobros, pagos y conciliación automática; financiamiento *pre-seed* ([iProUP](https://www.iproup.com/finanzas/55501-cresium-asi-es-la-nueva-solucion-clave-con-ia-para-simplificar-los-cobros-en-pymes), [LatamFintech](https://www.latamfintech.co/articles/conoce-cresium-la-fintech-que-esta-mejorando-los-tramites-y-escalando-la-eficiencia-de-las-pymes-argentinas)).

## 2. Qué falta confirmar (preguntas para Cresium)

1. **Cuenta**: ¿puede abrirla una persona física o monotributista, o hace falta una sociedad con CUIT? ¿Qué cuesta y qué comisión cobra por cada cobro?
2. **Entorno de pruebas**: ¿hay *sandbox* con dinero ficticio? ¿Cómo se simula una transferencia entrante?
3. **Cobro con CVU propio**: endpoint, campos (monto, referencia, vencimiento), si el CVU se puede crear por cobro y si rechaza montos distintos.
4. **Webhook**: lista de eventos, campos del aviso (id del movimiento, CVU de destino, monto, CBU y CUIT de origen, fecha), nombre del encabezado de la firma, qué se firma exactamente (¿el cuerpo crudo? ¿con marca de tiempo?) y política de reintentos.
5. **Consulta de estado**: endpoint para buscar movimientos por CVU o por referencia (para conciliar si se pierde un aviso).
6. **Devoluciones**: si se pueden hacer por API, a la cuenta de origen.
7. **Facturación**: si Cresium emite la factura electrónica (ARCA) o hay que emitirla aparte.

## 3. Cómo encaja en el sistema

El sistema ya está preparado (ADR-0020): pantallas, estados del cobro, auditoría y devolución al rechazar una aseguradora son los definitivos. Para cobrar de verdad hay que **agregar piezas, no cambiar las que hay**.

| Pieza | Qué hace | Dónde |
|---|---|---|
| `ProveedorPagosCresium` | Con la misma interfaz que el simulado: `datos_de_cobro(referencia)` pide a la API un CVU para ese cobro y devuelve CVU y alias. `permite_simular = False`, así desaparece el botón de simulación | `backend/app/integraciones/pagos.py` |
| Aviso de acreditación | `POST /api/pagos/aviso`: verifica la firma HMAC-SHA256 sobre el cuerpo crudo con comparación en tiempo constante, ignora avisos repetidos (por id del movimiento), busca el cobro por su CVU, **comprueba que el monto sea el precio del plan** y lo acredita con la misma lógica que hoy usa la simulación. Sin sesión ni CSRF, con límite de pedidos | `rutas/pagos.py` → `servicio_pagos.py` |
| Conciliación de respaldo | Un temporizador (como el de los sellos) consulta los cobros pendientes en la API, por si se perdió un aviso | `comandos.py` + `infraestructura/systemd/` |
| Devolución | Al rechazar una aseguradora, transferir el monto a la cuenta de origen por API; si la API no lo permite, el Administrador lo hace a mano y lo marca | `servicio_pagos.devolver_cobros` |
| Secretos | `CRESIUM_CLAVE_API` y `CRESIUM_SECRETO_AVISOS` en SSM como SecureString; `PROVEEDOR_PAGOS = "cresium"` en Terraform | `infraestructura/terraform/` |

Casos que hay que cubrir con pruebas:
- aviso con firma inválida (se rechaza y se audita);
- aviso repetido (no acredita dos veces);
- monto distinto del precio (queda pendiente y avisa al Administrador);
- pago después de vencido;
- transferencia a un CVU que no es de ningún cobro.

## 4. Dependencias y orden

1. **Precios de los planes (CP-38)**: sin precio no se puede verificar el monto. Es lo primero.
2. **Cuenta de Cresium y entorno de pruebas** (autora): abrir la cuenta, pedir el *sandbox* y generar las credenciales.
3. **Implementación** (agente): unos 2 o 3 días con la documentación a mano, pruebas incluidas.
4. **Prueba real** con un monto chico y su devolución.

Hasta que estén los puntos 1 y 2, el cobro queda simulado, que es la decisión de respaldo de CP-34. La entrega es antes del 2026-11-19, así que, si la cuenta no está antes del 2026-11-10, conviene presentarlo como trabajo futuro con el diseño de esta página.

## 5. Para el informe final

- El diseño con proveedor intercambiable permitió avanzar con el registro y el pago sin depender de un tercero: el cobro real se agrega sin tocar pantallas ni reglas.
- El riesgo principal de un cobro por transferencia es el **aviso falsificado**: por eso la firma HMAC, la comprobación del monto y la conciliación de respaldo.
