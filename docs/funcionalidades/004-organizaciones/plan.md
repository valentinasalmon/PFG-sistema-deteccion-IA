# Plan técnico: 004 — Organizaciones e invitaciones

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Tres tablas nuevas: `organizaciones`, `membresias` (usuario, organización, rol y cargo) e `invitaciones` (correo, cargo, estado y vencimiento). Un `ServicioOrganizaciones` concentra las reglas: permisos por rol, exactamente un Referente, límite de miembros del plan, vencimiento y respuesta de invitaciones, abandono y eliminación. Cada operación se registra en la auditoría de la 003, en la misma transacción.

La invitación se guarda en la base (hace falta listarla, reenviarla y cancelarla) y el enlace del correo lleva un token firmado con el identificador de la invitación. El token solo sirve para **consultar** la invitación sin sesión; para responderla hay que iniciar sesión con el correo invitado, así el token no da ningún permiso por sí mismo (RN10). Después de registrarse e iniciar sesión, la persona ve sus invitaciones pendientes y las responde desde la lista de organizaciones.

Los permisos se resuelven en el servicio: quien no es miembro recibe "no encontrada" (404), para no revelar qué organizaciones existen; un Miembro que intenta algo reservado al Referente recibe "acceso denegado" (403).

Los límites de los planes se guardan en la configuración (`PLANES`), como datos que pueden ajustarse sin cambiar el código (RF19 CA3). La 014 los pasará a la base cuando el Administrador pueda cambiar el plan de una organización (CP-01).

## Capas afectadas

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Modelos | `app/modelos/organizacion.py` (`Organizacion`, `Membresia`, `Invitacion`) | Tablas, restricciones e índices únicos parciales |
| Repositorios | `app/repositorios/repositorio_organizaciones.py` | Consultas de organizaciones, membresías e invitaciones |
| Servicios | `app/servicios/servicio_organizaciones.py`; `errores.py` (`AccesoDenegado`, `NoEncontrado`); `auditoria.py` (acciones); `servicio_correos.py` (7 correos); `tokens.py` (propósito); `fabrica.py` | Reglas de negocio |
| Esquemas | `app/esquemas/organizaciones.py` | Validación de las solicitudes y salida JSON |
| Rutas | `app/rutas/organizaciones.py`, `app/rutas/invitaciones.py`, `errores.py` (403 y 404) | API REST |
| Configuración | `entornos.py` (`PLANES`, `PLAN_INICIAL_ORGANIZACION`, `VIGENCIA_INVITACION`) | Límites y vencimiento |
| Plantillas | `app/plantillas/correos/` (7 correos en texto y HTML) | Avisos |
| Migraciones | `<id>_crear_tablas_de_organizaciones.py` | Tablas e índices |
| Frontend | `src/api/organizaciones.js`; `src/paginas/PaginaOrganizaciones.jsx`, `PaginaNuevaOrganizacion.jsx`, `PaginaOrganizacion.jsx`, `PaginaInvitacion.jsx`; `Encabezado.jsx`; `Rutas`/`App.jsx`; estilos | Pantallas |

## Contratos

### API

| Método y ruta | Quién | Respuesta |
|---|---|---|
| `GET /api/organizaciones` | Usuario | Mis organizaciones con mi rol |
| `POST /api/organizaciones` | Usuario | 201 con la organización |
| `GET /api/organizaciones/<id>` | Miembro | Datos, plan, límite, mi rol |
| `PATCH /api/organizaciones/<id>` | Referente | Datos actualizados |
| `DELETE /api/organizaciones/<id>` | Referente | Cuerpo `{"confirmacion": "<nombre>"}` |
| `GET /api/organizaciones/<id>/miembros` | Miembro | Listado |
| `PATCH /api/organizaciones/<id>/miembros/<id_usuario>` | Referente | Cargo |
| `DELETE /api/organizaciones/<id>/miembros/<id_usuario>` | Referente | Desvincular |
| `POST /api/organizaciones/<id>/referente` | Referente | `{"id_usuario": n}` |
| `POST /api/organizaciones/<id>/abandono` | Miembro | `{"confirmar_eliminacion": bool}` |
| `GET /api/organizaciones/<id>/invitaciones` | Referente | Pendientes |
| `POST /api/organizaciones/<id>/invitaciones` | Referente | `{"correo", "cargo"}` |
| `POST /api/organizaciones/<id>/invitaciones/<id_inv>/reenvio` | Referente | Renueva el vencimiento |
| `DELETE /api/organizaciones/<id>/invitaciones/<id_inv>` | Referente | Cancela |
| `GET /api/invitaciones` | Usuario | Mis invitaciones pendientes |
| `POST /api/invitaciones/consulta` | Público | `{"token"}` → organización, correo, vigencia |
| `POST /api/invitaciones/<id_inv>/aceptacion` | Usuario con el correo invitado | Membresía creada |
| `POST /api/invitaciones/<id_inv>/rechazo` | Usuario con el correo invitado | Invitación rechazada |

Errores nuevos: `AccesoDenegado` (403, `acceso_denegado`), `NoEncontrado` (404, `no_encontrado`). Los conflictos de reglas (límite, Referente que abandona) usan `ConflictoDatos` (409) con un `codigo` propio.

### Acciones de auditoría

`organizacion.creacion`, `organizacion.edicion`, `organizacion.eliminacion`, `invitacion.envio`, `invitacion.reenvio`, `invitacion.cancelacion`, `invitacion.aceptacion`, `invitacion.rechazo`, `membresia.edicion`, `membresia.desvinculacion`, `membresia.abandono`, `organizacion.cambio_referente`.

## Cambios en datos

- `organizaciones`: `id`, `nombre` (150), `tipo` (`estudio_juridico` | `aseguradora`), `correo_contacto` (254, nulo), `telefono` (30, nulo), `plan` (20), `creada_en`, `actualizada_en`.
- `membresias`: `id`, `id_organizacion` (FK, `CASCADE`), `id_usuario` (FK, `CASCADE`), `rol` (`referente` | `miembro`), `cargo` (100, nulo), `incorporado_en`. Únicos: `(id_organizacion, id_usuario)` y, parcial, un solo `referente` por organización.
- `invitaciones`: `id`, `id_organizacion` (FK, `CASCADE`), `correo` (254), `cargo` (100, nulo), `estado` (`pendiente` | `aceptada` | `rechazada` | `cancelada`), `id_invitante` (FK, `SET NULL`), `creada_en`, `vence_en`, `respondida_en`. Único parcial: una invitación `pendiente` por `(id_organizacion, correo)`.

## Bibliotecas nuevas

Ninguna.

## Estrategia de pruebas

- Integración por la API: un caso por criterio de aceptación, incluidos los permisos (no miembro, Miembro, Referente), el límite, los vencimientos y la auditoría de cada operación.
- Correos: cada aviso tiene su texto propio (la prueba existente de plantillas cubre las nuevas).
- Frontend: pruebas de cada pantalla con la API simulada.
- Manual: recorrido en navegador con dos cuentas (Referente e invitado) y correo real.

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Dos solicitudes simultáneas superan el límite de miembros | Aceptado para el alcance del proyecto; el índice único parcial evita al menos dos invitaciones pendientes al mismo correo |
| El enlace de invitación reenviado varias veces deja enlaces viejos vigentes | El token solo consulta; la vigencia real la decide la base (`vence_en` y `estado`) |
| La 005 debe recordar completar RF14 CA2, RF17 CA2 y RF18 | Anotado en la especificación de la 005 cuando se escriba |
