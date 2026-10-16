# Especificación: 004 — Organizaciones e invitaciones

- **Rama**: `funcionalidad/004-organizaciones`
- **Estado**: Aprobada (por el asistente, según el reparto del 2026-10-16; pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF10 a RF18 (los criterios que dependen de los casos se completan en la 005); RNF06 (acciones de organizaciones y membresías); RF47 (correos de estos eventos)
- **Reglas de negocio aplicadas**: RN06, RN07, RN08, RN09 (parcial), RN10, RN11, RN15 (límite de miembros)
- **Casos de uso**: CU08 a CU15

## Problema

Los estudios jurídicos y las aseguradoras trabajan en equipo: varias personas siguen los mismos reclamos. Para compartir casos más adelante (funcionalidad 005), primero tiene que existir la organización, con un Referente que la administra e invita a su equipo por correo, y con reglas claras para entrar, salir y transferir la administración.

## Alcance

### Incluido

**Organizaciones**
- Crear una organización con nombre, tipo (Estudio Jurídico o Aseguradora) y datos de contacto opcionales (correo y teléfono). El creador queda como Referente y la organización recibe el plan inicial **Organización Básico** (hasta 5 miembros, CP-02).
- Ver mis organizaciones con mi rol en cada una.
- Editar los datos (solo el Referente).
- Eliminar la organización escribiendo su nombre como confirmación (solo el Referente).

**Invitaciones**
- Invitar por correo, con cargo opcional, a personas registradas o no. La invitación vence a los 7 días (RN10).
- El límite de miembros del plan cuenta los miembros y las invitaciones pendientes vigentes.
- Ver, reenviar (renueva el vencimiento) y cancelar las invitaciones pendientes (solo el Referente).
- Abrir el enlace del correo: muestra qué organización invita y a qué correo. Sin sesión, ofrece iniciar sesión o crear una cuenta con ese correo.
- Ver mis invitaciones pendientes después de iniciar sesión, y aceptarlas o rechazarlas. Solo puede responderlas quien inició sesión con el correo invitado.

**Miembros**
- Ver los miembros (cualquier miembro): nombre, perfil, cargo, rol y fecha de incorporación.
- Editar el cargo de un miembro, desvincularlo y designar a otro miembro como Referente (solo el Referente).
- Abandonar la organización. El Referente debe designar antes a otro Referente; si es el único miembro, la organización se elimina con su salida, después de confirmarlo (RN08).

**Avisos por correo**
- Invitación; aceptación o rechazo (al Referente); desvinculación (al desvinculado); cambio de Referente (a ambos); abandono (al Referente); eliminación (a todos los miembros).

**Auditoría**
- Cada operación queda registrada con su resultado, sobre la base de la funcionalidad 003.

**Interfaz**
- Pantallas: mis organizaciones (con invitaciones pendientes), crear organización, detalle de la organización (datos, miembros, invitaciones y acciones según el rol) y respuesta a una invitación.

### Excluido

- Casos del espacio de la organización: funcionalidad 005. Por eso, en esta funcionalidad, abandonar o desvincular no transfiere casos (RF14 CA2, RF17 CA2) y eliminar la organización no elimina casos (RF18 CA1 y CA2 en la parte de casos): no existen todavía. La 005 agrega esas reglas.
- Cambiar de plan, consumo y límites distintos del de miembros: funcionalidades 014 y 019 (CP-01).
- Que el perfil Aseguradora deba trabajar dentro de una organización (CP-17): queda como cuestión abierta; por ahora cualquier persona puede crear o no organizaciones.
- Validar el nombre de la aseguradora contra el catálogo de la SSN (CP-18).
- Eliminar la cuenta de un Referente: funcionalidad 019.

## Criterios de aceptación

### Organizaciones
- [ ] **CA1**: Dado un usuario autenticado, cuando crea una organización con nombre y tipo válidos, entonces queda creada con el plan Organización Básico y el creador como Referente (RF10 CA1).
- [ ] **CA2**: Dado un usuario que ya pertenece a otras organizaciones, cuando crea una nueva, entonces conserva todas sus membresías (RF10 CA2, RN06).
- [ ] **CA3**: Dado el Referente, cuando modifica los datos de la organización, entonces se guardan y se registran en la auditoría con el valor anterior y el nuevo; dado un Miembro, entonces no puede modificarlos (RF11).
- [ ] **CA4**: Dado un usuario que no pertenece a la organización, cuando intenta verla, ver sus miembros u operar sobre ella, entonces el sistema responde como si no existiera (RF16 CA2).

### Invitaciones
- [ ] **CA5**: Dado el Referente, cuando invita a un correo, esté registrado o no, entonces se crea una invitación pendiente que vence a los 7 días y se envía un correo con el enlace (RF12 CA1, CA2; RN10).
- [ ] **CA6**: Dado que los miembros más las invitaciones pendientes alcanzaron el límite del plan, cuando se invita, entonces se rechaza indicando el límite (RF12 CA3, RN15).
- [ ] **CA7**: Dado un correo que ya es miembro o que ya tiene una invitación pendiente en la organización, cuando se lo invita, entonces se rechaza (RF12 CA5).
- [ ] **CA8**: Dada una invitación pendiente, el Referente puede reenviarla, lo que renueva el vencimiento, o cancelarla (RF12 CA4).
- [ ] **CA9**: Dado el enlace de una invitación vigente, cuando se abre, entonces se ve la organización que invita y el correo invitado; sin sesión, se ofrece iniciar sesión o crear una cuenta con ese correo (CU11).
- [ ] **CA10**: Dado un usuario autenticado con el correo invitado, cuando acepta, entonces se incorpora como Miembro con el cargo indicado y se avisa al Referente; cuando rechaza, la invitación queda rechazada y se avisa al Referente (RF13 CA1, CU11 4a).
- [ ] **CA11**: Dado un usuario autenticado con otro correo, cuando intenta responder, entonces se rechaza e indica con qué correo debe ingresar (RF13 CA2).
- [ ] **CA12**: Dada una invitación vencida, cancelada o ya respondida, cuando se abre el enlace o se intenta responder, entonces se informa que no está vigente (RF13 CA3).
- [ ] **CA13**: Dado un usuario autenticado, entonces ve sus invitaciones pendientes vigentes y puede responderlas desde allí (CU11 3a).

### Miembros
- [ ] **CA14**: Dado un miembro, cuando consulta el listado, entonces ve nombre, perfil, cargo, rol y fecha de incorporación de cada miembro (RF16 CA1).
- [ ] **CA15**: Dado el Referente, cuando modifica el cargo de un miembro, entonces se guarda sin alterar sus datos personales (RF15 CA1, RN11).
- [ ] **CA16**: Dado el Referente, cuando designa a otro miembro como Referente, entonces el designado pasa a Referente, el anterior a Miembro, la organización sigue teniendo exactamente un Referente y ambos reciben un aviso (RF15 CA2, RN07).
- [ ] **CA17**: Dado el Referente, cuando desvincula a un miembro, entonces este deja de pertenecer a la organización de inmediato y recibe un aviso; el Referente no puede desvincularse a sí mismo (RF14 CA1, CA3).
- [ ] **CA18**: Dado un Miembro, cuando abandona la organización, entonces deja de pertenecer y se avisa al Referente (RF17 CA1).
- [ ] **CA19**: Dado el Referente con otros miembros, cuando intenta abandonar, entonces se le exige designar antes otro Referente; si es el único miembro, se le advierte que la organización se eliminará y, si lo confirma, se elimina (RF17 CA3, RN08).

### Eliminación
- [ ] **CA20**: Dado el Referente, cuando elimina la organización escribiendo su nombre exacto, entonces se eliminan la organización, sus membresías y sus invitaciones, y se avisa a todos los miembros; si el nombre no coincide, no se elimina (RF18, RN09 sin casos).

### Auditoría y permisos
- [ ] **CA21**: Cada operación de esta funcionalidad, exitosa o rechazada, queda registrada en la auditoría con la organización como recurso (RNF06 CA1).
- [ ] **CA22**: Dado un Miembro que no es Referente, cuando intenta una operación reservada al Referente, entonces se rechaza indicando que solo el Referente puede hacerla.

## Preguntas abiertas

- Ninguna que bloquee. Quedan como cuestiones abiertas de la especificación general: CP-01 (cómo se contrata un plan), CP-17 (si el perfil Aseguradora debe trabajar dentro de una organización) y la propuesta de RN09 y RN10 (eliminación de casos y vencimiento de 7 días).
