# Especificación: 019 — Eliminación de cuenta y copia de datos personales

- **Rama**: `funcionalidad/019-baja-de-cuenta`
- **Estado**: Completada (pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF08, RF09; RNF06 (CA5); RNF08 (CA4: derechos de acceso y supresión)
- **Reglas de negocio aplicadas**: RN04, RN05, RN08, RN09, RN34
- **Casos de uso**: CU06, CU07 (incluye CU12, CU15, CU23 y CU24)

## Problema

La Ley N.° 25.326 da a cada persona el derecho de **acceder** a los datos que la plataforma guarda sobre ella (art. 14) y de **pedir su supresión** (art. 16). Hoy no hay forma de ejercer ninguno de los dos desde la plataforma.

La baja no puede dejar casos sin Responsable ni organizaciones sin Referente. Por eso, antes de eliminar la cuenta, la persona tiene que resolver esas situaciones.

## Alcance

### Incluido

**Copia de los datos personales (RF09)**
- Desde "Mi perfil", la persona pide una copia de sus datos. El sistema la genera al momento en dos formatos:
  - **JSON**, para usarla en otros sistemas.
  - **PDF**, para leerla o imprimirla.
- Qué incluye la copia:
  - Datos de la cuenta y el consentimiento aceptado (versión de los términos y fecha).
  - Organizaciones a las que pertenece, con su rol y su cargo.
  - Invitaciones pendientes que recibió.
  - Lista de los casos de los que es Responsable: número, tipo, estado, espacio y fechas.
  - Su propia actividad registrada en la auditoría: fecha, acción, resultado y dirección IP.
- Qué no incluye: datos de otras personas (otros miembros, quién la invitó, el detalle de la auditoría) ni el contenido de los casos (lugar, expediente, descripción), que puede referirse a terceros.
- La descarga se hace con enlaces firmados que vencen a los 15 minutos. Además, el enlace exige la sesión de la misma persona, así que no sirve por sí solo.
- Se envía un correo que avisa que se generó una copia, sin enlace, para que la persona sepa si no fue ella.

**Eliminación de la cuenta (RF08)**
- Desde "Mi perfil", la persona ve qué tiene que resolver antes de irse:
  - Los casos de los que es Responsable. Para cada uno, un enlace lleva al caso, donde ya puede transferirlo o eliminarlo.
  - Las organizaciones en las que es Referente y hay otros miembros: tiene que designar otro Referente.
  - Las organizaciones en las que es el único miembro: se eliminan con la cuenta, con sus casos. Se le avisa cuántos casos son.
- Cuando no queda nada por resolver, confirma con su contraseña. Entonces el sistema:
  - Elimina sus organizaciones de un solo miembro y sus casos.
  - Elimina sus membresías, sus accesos a casos y las invitaciones pendientes dirigidas a su correo.
  - Cancela las transferencias de casos personales que esperaban su aceptación.
  - Suprime la cuenta y cierra todas sus sesiones.
- La auditoría conserva sus entradas sin el usuario (RN34).
- Se envía un correo de confirmación a la dirección de la cuenta eliminada.
- El correo queda libre: puede volver a registrarse como una cuenta nueva.

**Auditoría**: la solicitud y la descarga de la copia, y la eliminación (exitosa o rechazada).

### Excluido

- Imágenes e informes en el almacenamiento: no existen todavía. Cuando se eliminan casos, la 006 y la 008 tienen que borrar sus archivos con la misma lógica.
- Plazo de gracia o recuperación de la cuenta eliminada: la supresión es inmediata.
- Entrega de la copia por almacenamiento S3: la copia se genera en el momento y no se guarda. La 006 incorpora S3 y se puede revisar si conviene guardarla.

## Criterios de aceptación

### Copia de datos (RF09)
- [x] **CA1**: Dado un usuario con sesión, cuando pide la copia, entonces recibe dos enlaces (JSON y PDF) que vencen a los 15 minutos, y se le envía un correo de aviso (RF09 CA1, CA2, CA4).
- [x] **CA2**: La copia contiene sus datos de cuenta, el consentimiento, sus membresías, sus invitaciones pendientes, los casos de los que es Responsable y su actividad registrada (RF09 CA1).
- [x] **CA3**: La copia no contiene datos personales de otras personas ni el contenido de los casos (RF09 CA3).
- [x] **CA4**: Un enlace vencido, alterado o de otra persona no descarga nada.

### Eliminación (RF08)
- [x] **CA5**: Dado un usuario Responsable de casos, cuando consulta la baja, entonces ve la lista de esos casos y no puede eliminar la cuenta hasta transferirlos o eliminarlos (RF08 CA1, RN05).
- [x] **CA6**: Dado un usuario que es Referente de una organización con otros miembros, entonces no puede eliminar la cuenta hasta designar otro Referente (RF08 CA2, RN08).
- [x] **CA7**: Dado un usuario que es el único miembro de una organización, entonces se le informa que la organización y sus casos se eliminarán, y se eliminan junto con la cuenta (RN08, RN09).
- [x] **CA8**: Dada una contraseña incorrecta, entonces la cuenta no se elimina y el intento queda en la auditoría.
- [x] **CA9**: Dadas las condiciones resueltas y la contraseña correcta, entonces se suprimen la cuenta, sus membresías, sus accesos y las invitaciones a su correo; se cierran sus sesiones; y la auditoría conserva sus entradas sin el usuario (RF08 CA3, RN34, RNF06 CA5).
- [x] **CA10**: Dada la eliminación completada, entonces se envía un correo de confirmación a la dirección de la cuenta eliminada (RF08 CA4).
- [x] **CA11**: Dada una cuenta eliminada, entonces su correo puede registrarse otra vez como una cuenta nueva, sin datos de la anterior.

## Preguntas abiertas

- **CP-20 (para la autora y los tutores)**: algunas entradas de auditoría guardan correos en su detalle (por ejemplo, los inicios de sesión fallidos, RNF06 CA7, y los cambios de correo). Al eliminar la cuenta, esas entradas quedan sin usuario, pero el correo sigue en el detalle.
  - **Propuesta provisoria**: conservarlas tal cual hasta que venzan los 5 años de CP-05. El registro es de solo inserción (RNF06 CA3) y su finalidad es la trazabilidad legal.
  - Lo único que cambia hoy es la Política de Privacidad, que lo informa.
  - Registrada en `docs/especificacion/06-cuestiones-abiertas.md`.
