# Plan técnico: 021 — Organizaciones de aseguradoras

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Se reutiliza todo el modelo de la 004 (organizaciones, membresías, invitaciones y auditoría) y se agregan las reglas RN36 a RN40:

- **Catálogo de la SSN** en `backend/recursos/catalogos/aseguradoras_ssn.csv` (192 aseguradoras, sin reaseguradoras). Se lee una sola vez y se mantiene en memoria; una ruta pública lo entrega al registro.
- **Registro**: `SolicitudRegistro` admite `id_aseguradora` (registrar la aseguradora) o `token_invitacion` (sumarse con una invitación). `ServicioCuentas` valida de dónde sale el perfil Aseguradora y, al registrar una aseguradora, `ServicioOrganizaciones.crear_aseguradora` crea la organización **pendiente** en la misma transacción que la cuenta. Al verificar el correo, las invitaciones vigentes de aseguradoras se aceptan solas.
- **Aprobación**: `organizaciones.estado` (`pendiente` o `activa`). El Administrador (rol `administrador`, creado con `flask administracion promover`) aprueba o rechaza; el rechazo elimina la organización y desactiva a su Referente.
- **Cuentas desactivadas**: `usuarios.activo`. Al salir de la última aseguradora (abandono, desvinculación, eliminación o rechazo) la cuenta se desactiva y se incrementa `version_sesion` para cerrar sus sesiones. Iniciar sesión se rechaza con `CuentaDesactivada` (403), salvo que haya invitaciones vigentes; aceptar una la reactiva. Si quien abandona queda desactivado, la ruta cierra su sesión y el frontend vuelve al inicio de sesión con el aviso.

## Capas afectadas

| Capa | Archivos |
|---|---|
| Modelos | `usuario.py` (`activo`), `organizacion.py` (`cuit`, `estado`, `aprobada_en`) |
| Repositorios | `catalogo_aseguradoras.py` (nuevo), `repositorio_organizaciones.py` |
| Servicios | `servicio_organizaciones.py`, `servicio_cuentas.py`, `servicio_sesion.py`, `servicio_correos.py`, `auditoria.py`, `errores.py`, `fabrica.py` |
| Esquemas y rutas | `esquemas/cuentas.py`, `esquemas/organizaciones.py`, `rutas/administracion.py`, `rutas/catalogos.py`, `rutas/organizaciones.py`, `rutas/errores.py` |
| Comandos | `app/comandos.py` |
| Plantillas | `aseguradora_aprobada`, `aseguradora_rechazada`; aviso de desactivación en `desvinculacion` y `organizacion_eliminada` |
| Migración | `6cfe78aed499_agregar_aseguradoras_y_cuentas_desactivadas.py` |
| Frontend | `PaginaRegistro.jsx` (pasos según el caso), `SelectorAseguradora.jsx`, `PaginaAdministracion.jsx`, `PaginaOrganizaciones.jsx`, `PaginaNuevaOrganizacion.jsx`, `PaginaOrganizacion.jsx`, `PaginaInvitacion.jsx`, `ProveedorSesion.jsx` (`terminarSesion`), `Rutas.jsx`, `Encabezado.jsx` |

## Contratos nuevos

| Método y ruta | Quién |
|---|---|
| `GET /api/catalogos/aseguradoras` | Público |
| `GET /api/administracion/aseguradoras-pendientes` | Administrador |
| `POST /api/administracion/organizaciones/<id>/aprobacion` | Administrador |
| `POST /api/administracion/organizaciones/<id>/rechazo` (`{"motivo"}`) | Administrador |

`POST /api/organizaciones/<id>/abandono` y `DELETE /api/organizaciones/<id>` devuelven además `cuenta_desactivada`. Errores nuevos: `cuenta_desactivada` (403), `aseguradora_registrada` y `organizacion_pendiente` (409).

## Estrategia de pruebas

Pruebas de API por criterio (`test_aseguradoras.py`), pruebas de pantalla (`aseguradoras.test.jsx` y las del registro), migración en PostgreSQL y recorrido completo en navegador con tres personas (Administrador, Referente y empleada).

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Alguien registra una aseguradora en la que no trabaja | Aprobación manual del Administrador (RN38) |
| El catálogo queda desactualizado | Se reemplaza el archivo; las organizaciones guardan su CUIT |
| Cuentas con perfil Aseguradora creadas antes de la 021 | Solo existen en desarrollo; no se migran |
