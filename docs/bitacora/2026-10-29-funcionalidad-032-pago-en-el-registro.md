# 2026-10-29 — Funcionalidad 032: pago del plan en el registro

## Qué se hizo

- **Registro por caminos** (frames 10a a 10g, aprobados por la autora con la tarjeta más ancha):
  - el primer paso elige entre abogado independiente, abogado con estudio jurídico (con el nombre del estudio) o aseguradora;
  - el estudio y la aseguradora eligen el plan Básico o Profesional y pagan al final del registro, también con Google;
  - los pasos se ven con su nombre en el panel verde de la izquierda y la tarjeta pasa de 30 a 50 rem de ancho;
  - la landing puede llegar con el camino y el plan elegidos: `/registro?tipo=estudio&plan=profesional`.
- **Pago por transferencia como cobra Cresium** (`PanelPago`): CVU, alias y referencia con botón para copiar, resumen del plan y estado que se actualiza solo. Mientras no esté la API, «Simular la transferencia» acredita el pago (CP-34).
- **Después del pago:** el estudio queda activo; la aseguradora queda pendiente de aprobación y recién ahí la ve el Administrador, con la etiqueta «Pago acreditado». Si la rechaza, el pago se devuelve (simulado).
- **Crear el estudio desde Mi perfil:** tres pasos (datos, plan, pago) que terminan en la página `/pago/<token>`.
- **Organización:**
  - con el pago pendiente no se invita ni se cargan casos, y el Referente puede «Retomar el pago» (el enlace anterior deja de servir);
  - el cambio de plan también pasa por el pago y rige al acreditarse;
  - con los lugares ocupados (miembros más invitaciones pendientes), «Enviar invitación» se desactiva y se sugiere pasar a un plan con más lugares.
- **Backend:** modelo `Cobro`, estado `pago_pendiente`, migración `f9a3b5c7d032`, `ServicioPagos`, proveedor intercambiable (ADR-0020), rutas `/api/pagos/<token>` y `/api/catalogos/planes`, y auditoría `organizacion.cobro`.
- Capturas en `docs/funcionalidades/032-pago-en-el-registro/capturas/`.

## Decisiones del agente

- **El token del enlace de pago es la credencial** de la página de pago, que no pide sesión (quien se registra todavía no verificó su correo). En la base solo se guarda su huella SHA-256, como los tokens de verificación.
- **Cobro «señuelo» con un correo existente:** la respuesta y la pantalla de pago son iguales a las de un registro nuevo, para no revelar qué correos existen (RF01 CA3). El cobro no se aplica a nada.
- **La cuenta de prueba** (`cuenta-de-prueba`) acredita el pago sola, para no trabar las demostraciones.
- **Precio vacío = «A confirmar»** en toda la interfaz, hasta que la autora defina los valores en `PLANES`.

## Calidad

- Backend: 541 pruebas, cobertura 97,55 %, flake8 sin observaciones, pylint 10/10 e import-linter con los 3 contratos.
- Frontend: 239 pruebas, eslint sin observaciones y compilación correcta.
- Recorrido completo en el navegador, en computadora y en celular (390 px): registro de un estudio con plan Profesional, pago simulado y resultado.

## Pendiente

- Precios de los planes (autora).
- API, entorno de pruebas y costos reales de Cresium: cuando estén, se reemplaza `ProveedorPagosSimulado` y se recibe el aviso de acreditación por *webhook*.
- Landing pública con los planes: propuesta para validar antes de implementar.
