# Especificación: 021 — Organizaciones de aseguradoras

- **Rama**: `funcionalidad/021-organizaciones-de-aseguradoras`
- **Estado**: Completada (modelo decidido por la autora el 2026-10-16; pendiente de revisión en el Pull Request)
- **Requisitos que realiza**: RF01 (registro de aseguradoras y por invitación), RF03 (cuentas desactivadas), RF10 y RF12 a RF17 (ajustes para aseguradoras); RNF06 (nuevas acciones)
- **Reglas de negocio aplicadas**: RN01, RN02, RN06, RN07, RN10, RN35 (con una excepción); reglas nuevas RN36 a RN40 (ver más abajo)
- **Casos de uso**: CU01, CU02, CU08, CU10, CU11, CU14; caso nuevo: aprobar una aseguradora (Administrador)

## Problema

Una aseguradora no trabaja como una persona suelta: es una empresa con empleados, y los casos que siguen son de la empresa. Con el modelo de la funcionalidad 004, cualquiera podía registrarse con el perfil Aseguradora sin pertenecer a ninguna, y cualquiera podía crear una organización con el nombre de una aseguradora real.

Decisión de la autora (CP-17, 2026-10-16): la aseguradora se registra como empresa, elegida del catálogo de la Superintendencia de Seguros de la Nación (CP-18); el Administrador de la plataforma aprueba la organización; los empleados se suman solo por invitación y, si dejan la aseguradora, su cuenta se desactiva. Los abogados siguen trabajando de forma individual y pueden crear un estudio jurídico.

## Reglas de negocio nuevas

Se agregan a la especificación general (`02-reglas-de-negocio.md`). RN35 suma una excepción: el Administrador, además de consultar, aprueba o rechaza el registro de las aseguradoras (RN38).

| ID | Regla |
|---|---|
| **RN36** | El perfil Aseguradora solo se obtiene de dos formas: registrando una aseguradora del catálogo de la SSN (quien la registra queda como Referente) o aceptando la invitación de una aseguradora. |
| **RN37** | Cada aseguradora del catálogo, identificada por su CUIT, puede tener una sola organización en la plataforma. |
| **RN38** | Una organización de aseguradora queda **pendiente** hasta que el Administrador la aprueba. Mientras está pendiente no puede invitar miembros. Si el Administrador la rechaza, se elimina y la cuenta de quien la registró se desactiva. |
| **RN39** | Una cuenta con perfil Aseguradora que deja de pertenecer a toda aseguradora (abandona, es desvinculada o la organización se elimina) queda **desactivada**: no puede iniciar sesión, salvo para aceptar una invitación vigente de otra aseguradora, que la reactiva. |
| **RN40** | Solo los usuarios con perfil Abogado pueden crear organizaciones, y solo del tipo Estudio Jurídico. Las organizaciones de aseguradora se crean únicamente al registrar la aseguradora (RN36). |

## Alcance

### Incluido

**Registro**
- El paso 1 del registro ofrece "Abogado o abogada" (uso individual) y "Registrar mi aseguradora" (para quien va a administrar la cuenta de la empresa).
- Con "Registrar mi aseguradora", el paso 3 pide buscar y elegir la empresa del catálogo de la SSN (192 aseguradoras, sin reaseguradoras). Si esa empresa ya está registrada, se indica que hay que pedir una invitación a su Referente.
- Al verificar el correo, la cuenta queda activa y la organización, pendiente de aprobación.
- **Registro por invitación**: desde el enlace de una invitación de aseguradora, la persona crea su cuenta con el correo y el perfil ya fijados, sin elegir perfil ni empresa. Al verificar el correo, queda incorporada a la aseguradora automáticamente.

**Aprobación por el Administrador**
- El Administrador ve las aseguradoras pendientes con su CUIT, denominación y la persona que las registró, y las aprueba o rechaza indicando un motivo.
- Se avisa por correo a quien la registró.
- Las cuentas de Administrador se crean desde la terminal del servidor (`flask administracion promover <correo>`), nunca desde la interfaz.

**Cuentas desactivadas**
- Se desactivan según RN39 y se cierran sus sesiones abiertas.
- Al intentar iniciar sesión se informa que la cuenta está desactivada porque ya no pertenece a una aseguradora, salvo que tenga una invitación vigente.

**Ajustes de la 004**
- Crear organización: solo para abogados y solo del tipo Estudio Jurídico (RN40).
- En una aseguradora, el nombre y el tipo no se editan (vienen del catálogo); los datos de contacto sí.
- La pantalla de una aseguradora pendiente lo indica y no ofrece invitar.

**Auditoría**: registro con aseguradora, aprobación, rechazo, desactivación y reactivación de cuentas.

### Excluido

- Tablero de administración, estadísticas y planes: funcionalidad 014. Esta funcionalidad solo agrega la lista de aseguradoras pendientes.
- Verificación por dominio del correo o por documentación de la empresa: no se hace (decisión de la autora: aprobación manual).
- Actualización automática del catálogo de la SSN: se reemplaza el archivo a mano (ver `backend/recursos/catalogos/README.md`).
- Migrar cuentas con perfil Aseguradora creadas antes de esta funcionalidad: solo existen en entornos de desarrollo.

## Criterios de aceptación

### Registro de una aseguradora
- [x] **CA1**: Dado un visitante en el paso 1 del registro, entonces puede elegir "Abogado o abogada" o "Registrar mi aseguradora".
- [x] **CA2**: Dado que eligió registrar su aseguradora, cuando busca por parte del nombre o del CUIT, entonces ve las aseguradoras del catálogo que coinciden y debe elegir una para avanzar.
- [x] **CA3**: Dado un registro con una aseguradora del catálogo, entonces se crean la cuenta (perfil Aseguradora) y la organización (tipo Aseguradora, con la denominación y el CUIT del catálogo, estado pendiente) con esa persona como Referente.
- [x] **CA4**: Dada una aseguradora que ya tiene organización, cuando alguien intenta registrarla, entonces se rechaza indicando que pida una invitación a su Referente (RN37).
- [x] **CA5**: Dado un registro con perfil Aseguradora sin empresa del catálogo ni invitación, entonces se rechaza (RN36).

### Aprobación
- [x] **CA6**: Dada una aseguradora pendiente, entonces su Referente ve que está pendiente de aprobación y no puede invitar miembros (RN38).
- [x] **CA7**: Dado el Administrador, entonces ve la lista de aseguradoras pendientes con denominación, CUIT, Referente y fecha; un usuario que no es Administrador no puede verla.
- [x] **CA8**: Dado el Administrador, cuando aprueba una aseguradora, entonces queda activa y se avisa al Referente por correo.
- [x] **CA9**: Dado el Administrador, cuando rechaza una aseguradora con un motivo, entonces la organización se elimina, la cuenta del Referente se desactiva y se le avisa por correo con el motivo (RN38).

### Empleados
- [x] **CA10**: Dada una invitación de una aseguradora a un correo sin cuenta, cuando la persona abre el enlace y crea la cuenta, entonces el correo y el perfil Aseguradora vienen fijados y no se pide empresa.
- [x] **CA11**: Dada esa cuenta, cuando verifica el correo, entonces queda incorporada a la aseguradora como Miembro con el cargo de la invitación, sin otro paso.
- [x] **CA12**: Dado un registro por invitación con un correo distinto del invitado, entonces se rechaza.

### Cuentas desactivadas
- [x] **CA13**: Dado un miembro con perfil Aseguradora, cuando abandona su única aseguradora, es desvinculado o la organización se elimina, entonces su cuenta se desactiva, sus sesiones se cierran y el aviso por correo lo indica (RN39).
- [x] **CA14**: Dada una cuenta desactivada sin invitaciones vigentes, cuando inicia sesión con la contraseña correcta, entonces se rechaza indicando que la cuenta está desactivada; con una contraseña incorrecta, el mensaje sigue siendo el genérico.
- [x] **CA15**: Dada una cuenta desactivada con una invitación vigente de otra aseguradora, cuando inicia sesión, entonces puede entrar y, al aceptar la invitación, la cuenta se reactiva.
- [x] **CA16**: Un abogado que deja una aseguradora o un estudio no se desactiva: conserva su espacio personal.

### Creación de organizaciones
- [x] **CA17**: Dado un usuario con perfil Aseguradora, entonces no puede crear organizaciones; dado un abogado, solo puede crear organizaciones del tipo Estudio Jurídico (RN40).
- [x] **CA18**: Dada una aseguradora, cuando su Referente edita los datos, entonces puede cambiar el contacto pero no el nombre ni el tipo.

### Auditoría
- [x] **CA19**: El registro de una aseguradora, su aprobación o rechazo y cada desactivación o reactivación de una cuenta quedan en la auditoría.

## Preguntas abiertas

- Licencia del catálogo de la SSN: pendiente de confirmar (CP-18).
