# Plan técnico: 005 — Casos y permisos

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Dos tablas nuevas: `casos` y `accesos_caso`. Un `ServicioCasos` concentra las reglas: espacio de trabajo, permisos (Responsable > Colaboración > Lectura), transiciones de estado (RN18), retención, accesos compartidos, transferencias y eliminación. Cada operación, exitosa o rechazada, se registra en la auditoría de la 003 en la misma transacción.

**Permisos.** El permiso se calcula en el servicio a partir del Responsable y de los accesos individuales o de toda la organización. Un acceso solo vale mientras el usuario sea miembro de la organización del caso, y si hay dos, prevalece el más alto. Quien no tiene permiso recibe 404, como si el caso no existiera (RNF05). Quien tiene un permiso menor al necesario recibe 403. La misma condición de acceso, escrita como una consulta SQL, filtra el listado, así que nunca aparece un caso sin permiso.

**Acciones.** Cada respuesta incluye la lista `acciones` (editar, cerrar, archivar, desarchivar, reabrir, compartir, transferir y eliminar), calculada en el backend según el permiso y el estado. El frontend solo muestra lo que esa lista habilita y no repite las reglas.

**Número de caso.** El número `CASO-AAAA-NNNNNN` se toma del identificador de la fila, que es la secuencia global (RN16). El caso se inserta con un número provisorio único (`TMP-…`) y se reemplaza en la misma transacción, después del `flush`.

**Transferencias.** En una organización, la transferencia es inmediata: los dos son miembros y el Referente ya puede reasignar casos (RN14). En el espacio personal, el destinatario tiene que aceptarla (RF33 CA2), porque el caso entra en su espacio. Mientras espera, la solicitud queda en `transferencia_a` y `transferencia_en`.

**Reglas pendientes de la 004.** `ServicioOrganizaciones` recibe el repositorio de casos y aplica tres reglas:
- No deja abandonar a quien es Responsable de casos de la organización (409 `debe_transferir_casos`).
- Al desvincular a un miembro, reasigna sus casos al Referente y le quita sus accesos.
- Al eliminar la organización, elimina sus casos e informa la cantidad.

## Capas afectadas

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Modelos | `app/modelos/caso.py` (`Caso`, `AccesoCaso`, `normalizar_texto`) | Tablas, restricciones e índices |
| Repositorios | `app/repositorios/base.py` (`RepositorioBase`), `repositorio_casos.py`; `repositorio_organizaciones.py` hereda de la base | Consultas, condición de acceso y búsqueda |
| Servicios | `servicio_casos.py`; `servicio_organizaciones.py` (reglas de la 004); `auditoria.py` (acciones); `servicio_correos.py` (5 correos); `fabrica.py` | Reglas de negocio |
| Esquemas | `app/esquemas/casos.py` | Validación, filtros, `acciones_permitidas` y salida JSON |
| Rutas | `app/rutas/casos.py` | API REST, paginación de 20 |
| Plantillas | `app/plantillas/correos/caso_*` (texto y HTML) | Avisos |
| Migraciones | `057c1b5b72d9_crear_tablas_de_casos.py` | Tablas e índices |
| Frontend | `src/api/casos.js`; `PaginaCasos.jsx`, `PaginaNuevoCaso.jsx`, `PaginaCaso.jsx`, `PaginaInicio.jsx`; `CampoAreaTexto.jsx`, `CampoSeleccion.jsx`; `utilidades/casos.js`, `utilidades/fechas.js`; `Encabezado.jsx`, `App.jsx`, estilos | Pantallas |

## Contratos

### API

| Método y ruta | Quién | Respuesta |
|---|---|---|
| `GET /api/casos` | Usuario | `{casos, total, pagina, paginas}`; filtros `numero`, `expediente`, `estado`, `tipo`, `espacio`, `desde`, `hasta`, `pagina` |
| `POST /api/casos` | Abogado o miembro de una organización activa | 201 con el detalle |
| `GET /api/casos/resumen` | Usuario | `{por_estado}` |
| `GET /api/casos/transferencias` | Usuario | Transferencias que esperan su respuesta |
| `GET /api/casos/<id>` | Con permiso | `{caso, accesos}` |
| `PATCH /api/casos/<id>` | Responsable o Colaboración | Detalle actualizado |
| `DELETE /api/casos/<id>` | Responsable | Cuerpo `{"confirmacion": "<número>"}` |
| `POST /api/casos/<id>/estado` | Responsable | `{"operacion": "cerrar" \| "archivar" \| "desarchivar" \| "reabrir"}` |
| `POST /api/casos/<id>/accesos` | Responsable | `{"nivel", "id_usuario"}` (sin `id_usuario`: toda la organización) |
| `PATCH /api/casos/<id>/accesos/<id_acceso>` | Responsable | `{"nivel"}` |
| `DELETE /api/casos/<id>/accesos/<id_acceso>` | Responsable | Revoca |
| `POST /api/casos/<id>/transferencia` | Responsable | `{"destino", "conservar_colaboracion"}`: id de un miembro o correo de un abogado |
| `DELETE /api/casos/<id>/transferencia` | Responsable | Cancela la solicitud |
| `POST /api/casos/<id>/transferencia/aceptacion` | Destinatario | Pasa a Responsable |
| `POST /api/casos/<id>/transferencia/rechazo` | Destinatario | Rechaza |

### Acciones de auditoría

`caso.creacion`, `caso.edicion` (con valor anterior y nuevo), `caso.cambio_estado`, `caso.compartir`, `caso.acceso_modificacion`, `caso.acceso_revocacion`, `caso.transferencia`, `caso.eliminacion`. El recurso es `caso` con su identificador.

## Cambios en datos

- `casos`:
  - Columnas: `id`, `numero` (20, único), `id_organizacion` (FK `CASCADE`, nulo = personal), `id_responsable` (FK), `tipo`, `fecha_hecho`, `lugar` (200), `expediente` (100, nulo), `expediente_normalizado` (índice), `descripcion`, `estado`, `retencion_desde`, `transferencia_a` (FK `SET NULL`), `transferencia_en`, `creado_en` y `actualizado_en`.
  - Restricciones de tipo y estado. Índices por Responsable, organización y última actualización.
- `accesos_caso`:
  - Columnas: `id`, `id_caso` (FK `CASCADE`), `id_usuario` (FK `CASCADE`, nulo si es para toda la organización), `toda_organizacion`, `nivel` y `otorgado_en`.
  - Únicos: `(id_caso, id_usuario)` y, como índice parcial, un solo acceso de toda la organización por caso.

## Bibliotecas nuevas

Ninguna.

## Estrategia de pruebas

- Integración por la API: una o más pruebas por criterio de aceptación, incluidos los permisos (sin acceso, Lectura, Colaboración y Responsable), las transiciones inválidas, los correos y la auditoría.
- Frontend: pruebas de cada pantalla con la API simulada (listado, filtros, paginación, alta, detalle según el permiso, compartir, transferir y eliminar).
- Manual: recorrido en navegador con dos cuentas, en escritorio y en celular.

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La búsqueda por expediente no distingue acentos en SQLite y PostgreSQL de la misma forma | Se guarda `expediente_normalizado` (minúsculas y sin tildes) y se busca sobre esa columna |
| Un acceso de toda la organización alcanza a ex miembros | La condición de acceso exige la membresía actual en cada consulta |
| "Reabrir" debería volver a Analizado si hay informes | `Caso.tiene_informes` devuelve `False` hasta la 008, que lo implementa |
