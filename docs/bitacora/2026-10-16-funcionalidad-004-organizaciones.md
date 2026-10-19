# 2026-10-16 — Funcionalidad 004: organizaciones e invitaciones

## Qué se hizo

Estudios jurídicos y aseguradoras pueden trabajar en equipo: se crea una organización, el Referente invita por correo, las personas aceptan o rechazan y el Referente gestiona los miembros. Documentos: [especificación](../funcionalidades/004-organizaciones/especificacion.md), [plan](../funcionalidades/004-organizaciones/plan.md) y [tareas](../funcionalidades/004-organizaciones/tareas.md). La rama `funcionalidad/004-organizaciones` parte de la 003, porque usa la auditoría.

- **Backend**: tablas `organizaciones`, `membresias` e `invitaciones` (migración `cf00ca279723`), `ServicioOrganizaciones` con las reglas, 18 rutas nuevas, 6 correos nuevos (texto y HTML) y 12 acciones de auditoría.
- **Frontend**: pantallas "Organizaciones" (con las invitaciones pendientes), "Crear organización", la pantalla de cada organización según el rol y la del enlace de invitación; enlace "Organizaciones" en el encabezado; el registro precarga el correo invitado.
- **Componentes nuevos**: `BotonConfirmar` (confirmación en dos pasos, sin ventanas emergentes, con el foco en "Cancelar"), `Etiqueta`, el hook `useDatos` y `formatearFecha` (UTC a hora argentina).

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA4 Organizaciones | Pruebas de API (creación, varias organizaciones, edición con auditoría, acceso de quien no es miembro igual que una inexistente) y de pantalla | Cumplidos |
| CA5 – CA13 Invitaciones | Pruebas de API (correo registrado y no registrado, límite con invitaciones vencidas, duplicados, reenvío y cancelación, enlace sin sesión, aceptar, rechazar, otro correo, vencida, cancelada o respondida, lista de pendientes) y de pantalla | Cumplidos |
| CA14 – CA19 Miembros | Pruebas de API y de pantalla de cada operación, incluido el índice de un solo Referente | Cumplidos |
| CA20 Eliminación | Prueba con nombre incorrecto y correcto: se borran membresías e invitaciones y se avisa a los miembros | Cumplido |
| CA21, CA22 Auditoría y permisos | Pruebas de las entradas y de los rechazos a un Miembro | Cumplidos |

Cifras: backend con 167 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos; frontend con 110 pruebas, cobertura del 99 %, ESLint sin errores y compilación correcta. Migración probada con `upgrade`, `check` y `downgrade` en PostgreSQL.

Recorrido en navegador real con PostgreSQL, Redis y correo: una Referente crea la organización e invita a un correo sin cuenta; la invitada abre el enlace en un celular (375 px, sin desbordes), crea la cuenta con el correo precargado, la verifica, ve la invitación en "Organizaciones" y la acepta; la Referente designa a la invitada como Referente y abandona; la nueva Referente elimina la organización escribiendo su nombre. Llegaron los correos esperados y no hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Plan inicial "Organización Básico"** (hasta 5 miembros), con los valores propuestos en CP-02. Los límites viven en la configuración (`PLANES`) hasta que la 014 los pase a la base.
- **El límite cuenta las invitaciones pendientes vigentes**: así no se pueden enviar más invitaciones que lugares. Las vencidas no ocupan lugar y, si se vuelve a invitar al mismo correo, se renuevan en lugar de duplicarse.
- **El enlace de invitación solo sirve para consultarla**: responder exige iniciar sesión con el correo invitado (RN10). Por eso, el aviso a quien entra con otro correo no muestra el correo invitado en la respuesta de la API; la pantalla lo muestra a partir del enlace, que solo tiene quien recibió el correo.
- **Después de registrarse**, la persona responde la invitación desde "Organizaciones", en lugar de guardar el enlace en el navegador: es más simple y funciona aunque abra la verificación en otro dispositivo.
- **Quien no es miembro recibe 404** (como si la organización no existiera); un Miembro que intenta algo del Referente recibe 403.
- **Datos de contacto**: correo y teléfono, ambos opcionales.
- **CP-17 no se aplica todavía**: cualquier perfil puede crear organizaciones de cualquier tipo, hasta que la autora decida.
- **Sin las reglas de casos**: abandonar o desvincular no transfiere casos y eliminar no borra casos, porque todavía no existen. Queda anotado para la 005.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| Designar Referente violaba el índice único de un solo Referente al cambiar los dos roles en la misma operación | Se baja primero el rol actual con un `flush` y después se sube el del designado |
| SQLite (pruebas) no aplica `ON DELETE CASCADE` sin activar las claves foráneas | El ORM elimina membresías e invitaciones en cascada; la base lo hace también en PostgreSQL como respaldo |
| La validación de los datos respondía antes que el control de acceso, con un 400 en lugar de un 404 | No revela nada (la respuesta es igual para una organización inexistente); las pruebas de acceso usan cuerpos válidos |
| La regla de ESLint de React pedía funciones en línea en `useCallback` | La función de carga de la lista se definió fuera del componente y se pasa directamente |

## Pendientes

- **Autora**: revisar e integrar primero la 003 y después la 004 (su rama parte de la 003). Decidir CP-17.
- **005**: transferir los casos al abandonar o ser desvinculado (RF14 CA2, RF17 CA2) y eliminar los casos con la organización (RF18).
- **014**: planes en la base de datos y cambio de plan por el Administrador (CP-01).
