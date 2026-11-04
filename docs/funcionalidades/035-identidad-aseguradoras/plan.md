# Plan técnico: 035 — Verificación de identidad del Referente de una aseguradora

## Capas

| Capa | Archivo | Qué hace |
|---|---|---|
| Modelo | `app/modelos/verificacion_identidad.py` | `VerificacionIdentidad`: organización, usuario, proveedor, referencia externa, huella del token, estado, motivo, fechas. Sin datos biométricos |
| Migración | `migraciones/versions/a3c5e7f9b035_verificacion_de_identidad.py` | Tabla `verificaciones_identidad` |
| Integración | `app/integraciones/identidad.py` | `ProveedorIdentidadSimulado` (página propia y simulación) y `crear_proveedor_identidad` según `VERIFICACION_IDENTIDAD` (`simulado`, `desactivado`; `identik` cuando esté la API) |
| Repositorio | `app/repositorios/repositorio_verificaciones.py` | Última verificación de una organización, búsqueda por huella del token |
| Servicio | `app/servicios/servicio_identidad.py` | Iniciar (solo el Referente de una aseguradora pendiente), consultar, registrar el resultado, simular, estado por organización, exigir para aprobar |
| Servicio existente | `servicio_organizaciones.aprobar` | Antes de aprobar, pide al servicio de identidad que exija la verificación aprobada (RN41) |
| Rutas | `rutas/organizaciones.py` (`GET/POST /<id>/identidad`), `rutas/identidad.py` (`GET /api/identidad/<token>`, `POST /api/identidad/<token>/simulacion`), `rutas/administracion.py` (estado en las pendientes) | |
| Interfaz | `PaginaOrganizacion` (sección del Referente), `PaginaVerificacionIdentidad` (`/identidad/:token`), `PaginaAdministracion` (estado y aprobación bloqueada) | |
| Infraestructura | Terraform y `generar_entorno.sh` | Variable `verificacion_identidad` (por defecto `desactivado` en producción) |

## Decisiones

- **Igual que el cobro (ADR-0020)**: proveedor intercambiable con un simulado que arma la misma forma de datos. Cambiar a Identik toca solo la integración y suma la ruta del aviso firmado.
- **Token del enlace**: aleatorio, en la base solo su huella SHA-256, como el pago y la carga desde el celular.
- **Producción**: por defecto desactivada (la aprobación sigue como hoy); se puede activar `simulado` para mostrar el flujo o `identik` cuando esté conectado.
- **Sin biometría**: el modelo no tiene dónde guardarla; solo resultado, motivo de rechazo y referencia del proveedor.

## Pruebas

- Servicio: inicio por el Referente, rechazos (miembro, organización activa, verificación desactivada), resultado aprobado y rechazado, nueva verificación tras un rechazo, exigencia al aprobar.
- Rutas: inicio y consulta con sesión, página pública por token, simulación solo con el proveedor simulado, aprobación bloqueada.
- Interfaz: sección del Referente, página de verificación, estado en administración y botón de aprobar deshabilitado.
