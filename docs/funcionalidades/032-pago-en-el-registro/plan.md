# Plan técnico: 032 — Pago del plan en el registro

## Backend

- **Modelo `Cobro`** (tabla `cobros`): organización (puede quedar vacía), plan, motivo (`alta` o `cambio_plan`), referencia legible (`EVD-XXXXXX`), huella SHA-256 del token, estado (`pendiente`, `acreditado`, `devuelto`), proveedor, CVU, alias y fechas. Solo se guarda la huella del token, como en los enlaces de carga.
- **Organización**: nuevo estado `pago_pendiente`. Migración `f9a3b5c7d032`.
- **Proveedor de pagos intercambiable** (`integraciones/pagos.py`), como el sello de tiempo: hoy `ProveedorPagosSimulado` (Cresium simulado), que arma el CVU y el alias y permite simular la acreditación. ADR-0020.
- **`ServicioPagos`**: crear cobros, consultarlos por token, simular la acreditación (aplica el alta o el cambio de plan) y devolverlos al rechazar una aseguradora.
- **Registro**: nuevos campos `nombre_estudio` y `plan`. El estudio y la aseguradora se crean con `pago_pendiente` y la respuesta trae el token del cobro. Con un correo ya registrado se crea un cobro sin organización, para que la respuesta sea idéntica (RF01 CA3).
- **Rutas**:
  - `GET /api/catalogos/planes` (pública);
  - `GET /api/pagos/<token>` y `POST /api/pagos/<token>/simulacion` (públicas: el token es la credencial);
  - `POST /api/organizaciones/<id>/cobro` (retomar el pago);
  - `POST /api/organizaciones` y `POST /api/organizaciones/<id>/plan` devuelven el token del cobro.
- **Reglas**: no se invita ni se crean casos si la organización no está activa; el Administrador solo ve las aseguradoras ya pagadas.

## Frontend

- **Registro** con los pasos según el camino (4 o 6), panel de pasos con nombre a la izquierda y tarjeta ancha.
- **`PanelPago`** reutilizable (registro, `/pago/<token>`, crear estudio y cambio de plan) que consulta el estado cada pocos segundos.
- **Crear estudio** desde Mi perfil en tres pasos (datos, plan, pago).
- **Organización**: uso del plan, «Invitar» deshabilitado con el cupo lleno, aviso de pago pendiente y «Pasar a Profesional» con pago.
