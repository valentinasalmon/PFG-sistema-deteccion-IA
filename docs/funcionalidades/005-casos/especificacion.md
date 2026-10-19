# Especificación: 005 — Casos y permisos

- **Rama**: `funcionalidad/005-casos`
- **Estado**: Completada (pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF23 a RF33; completa RF14 CA2, RF17 CA2 y RF18 de la funcionalidad 004; RNF05 (sin revelar casos ajenos); RNF06 (acciones de casos)
- **Reglas de negocio aplicadas**: RN09, RN12, RN13, RN14, RN16, RN17, RN18 (sin las transiciones de análisis), RN19, RN20, RN21 (sin imágenes todavía), RN30 (fecha de vencimiento), RN36 a RN40
- **Casos de uso**: CU18 a CU24

## Problema

El caso es la unidad de trabajo de la plataforma: agrupa las imágenes de un siniestro o de un reclamo laboral, sus análisis y sus informes. Antes de cargar imágenes (006) hay que poder crear casos, encontrarlos, decidir quién los ve y quién los modifica, cerrarlos, archivarlos y eliminarlos, y que esas reglas respeten a las organizaciones de la 004 y la 021.

## Alcance

### Incluido

**Crear y consultar**
- Crear un caso en el espacio personal o en una organización activa de la que el usuario es miembro, con tipo (Automovilístico o Laboral), fecha del hecho, lugar y, opcionales, expediente y descripción. El sistema asigna el número `CASO-AAAA-NNNNNN`, el estado Borrador y al creador como Responsable.
- Las personas con perfil Aseguradora no tienen espacio personal: sus casos siempre son de su aseguradora (decisión de la 021).
- Detalle del caso con sus datos, estado, accesos, vencimiento de la retención y las acciones que el permiso habilita.
- Listado paginado (20 por página) de los casos accesibles, ordenado por última actualización y sin los archivados; búsqueda por número y por expediente (parcial, sin distinguir mayúsculas ni acentos) y filtros por estado, tipo, espacio y rango de fechas del hecho.

**Editar y cambiar de estado**
- Editar tipo, fecha, lugar, expediente y descripción (Responsable y Colaborador), con el valor anterior y el nuevo en la auditoría.
- Cerrar, archivar, desarchivar y reabrir (solo el Responsable). Al cerrar comienza el plazo de retención de 2 años y se muestra la fecha de vencimiento; desarchivar no lo reinicia; reabrir lo detiene.

**Compartir y transferir**
- Compartir un caso de organización con un miembro o con toda la organización, con permiso de Lectura o de Colaboración; modificar el nivel y revocar. Prevalece el permiso más alto. Los casos personales no se comparten.
- Transferir la responsabilidad: en una organización, a otro miembro (el anterior conserva Colaboración salvo que indique lo contrario); en el espacio personal, a otro usuario registrado, que debe aceptarla.

**Eliminar**
- Eliminar escribiendo el número de caso como confirmación; se avisa por correo a quienes tenían acceso.

**Reglas pendientes de la 004**
- Un miembro Responsable de casos de la organización no puede abandonarla sin transferirlos antes.
- Al desvincular a un miembro, sus casos de la organización pasan al Referente y pierde sus accesos.
- Al eliminar una organización se eliminan sus casos; la confirmación informa cuántos.

**Avisos por correo**: caso compartido, acceso modificado o revocado, transferencia (solicitud, aceptación y aviso a ambos) y caso eliminado.

**Auditoría**: cada operación sobre casos, exitosa o rechazada.

### Excluido

- Imágenes, análisis e informes: funcionalidades 006 a 008. Por eso los estados "En análisis" y "Analizado" existen pero ninguna operación de esta funcionalidad lleva a ellos, y reabrir siempre vuelve a Borrador hasta que haya informes.
- Destrucción automática al vencer la retención y prórroga: funcionalidad 015.
- Límites del plan para casos (análisis, imágenes, almacenamiento): funcionalidad 014.
- Panel principal con resumen: funcionalidad 013.

## Criterios de aceptación

### Crear y consultar
- [x] **CA1**: Dados datos válidos, cuando se crea el caso, entonces recibe un número `CASO-AAAA-NNNNNN` único, el estado Borrador y al creador como Responsable (RF23 CA1, RN16).
- [x] **CA2**: Dada una fecha del hecho futura, entonces se rechaza (RF23 CA2).
- [x] **CA3**: Dado un espacio que es una organización de la que el usuario no es miembro, o que está pendiente de aprobación, entonces se rechaza; dado un usuario con perfil Aseguradora, entonces no puede crear casos en el espacio personal (RF23 CA3).
- [x] **CA4**: Dado un usuario con algún permiso, cuando consulta el caso, entonces ve el detalle y solo las acciones que su permiso habilita; sin permiso, el sistema responde como si el caso no existiera (RF24).
- [x] **CA5**: Dado el listado, entonces muestra los casos propios y compartidos, paginados, por última actualización y sin los archivados; nunca incluye casos sin permiso (RF26 CA1, CA4).
- [x] **CA6**: Dado un filtro por estado Archivado, entonces se muestran los archivados; dada una búsqueda por expediente, entonces la coincidencia es parcial y no distingue mayúsculas ni acentos; además se filtra por número, tipo, espacio y fechas (RF26 CA2, CA3).

### Editar y estados
- [x] **CA7**: Dado un Responsable o Colaborador y un caso en Borrador o Analizado, cuando edita los datos, entonces se guardan y la auditoría registra el valor anterior y el nuevo; el Lector no puede editar y el número no se modifica (RF25 CA1, CA3; RN20).
- [x] **CA8**: Dado un caso Cerrado o Archivado, entonces no se puede editar (RF25 CA2, RN19).
- [x] **CA9**: Dado el Responsable, cuando cierra un caso en Borrador o Analizado, entonces pasa a Cerrado y se muestra el vencimiento de la retención a 2 años (RF27 CA1, RN30).
- [x] **CA10**: Dado un caso Cerrado, cuando se archiva, entonces pasa a Archivado y sale del listado por defecto; al desarchivarlo vuelve a Cerrado sin reiniciar el plazo (RF28).
- [x] **CA11**: Dado un caso Cerrado o Archivado, cuando se reabre, entonces pasa a Borrador (o a Analizado si tiene informes) y se elimina la fecha de vencimiento (RF29).
- [x] **CA12**: Toda transición que no respeta RN18, o que intenta alguien que no es el Responsable, se rechaza.

### Compartir
- [x] **CA13**: Dado un caso de organización, cuando el Responsable lo comparte con un miembro, entonces ese miembro obtiene el permiso elegido y recibe un aviso (RF30 CA1).
- [x] **CA14**: Dado un caso compartido con toda la organización, entonces los miembros actuales y futuros tienen el permiso mientras pertenezcan a ella; si alguien tiene dos permisos, prevalece el más alto (RF30 CA2, CA3).
- [x] **CA15**: Dado un caso personal, entonces no se puede compartir; dado un usuario que no es miembro de la organización del caso, entonces no puede ser destinatario (RF30 CA4, CA5; RN13).
- [x] **CA16**: Dado un acceso, cuando el Responsable lo revoca o cambia su nivel, entonces se aplica en la siguiente solicitud y se avisa al afectado (RF31).

### Transferir
- [x] **CA17**: Dado un caso de organización, cuando se transfiere a otro miembro, entonces el destinatario pasa a Responsable y el anterior conserva Colaboración, salvo que indique lo contrario; se avisa a ambos (RF33 CA1, CA3).
- [x] **CA18**: Dado un caso personal, cuando se transfiere a otro usuario registrado, entonces el destinatario debe aceptarlo y, al aceptar, el caso pasa a su espacio personal; puede rechazarlo y el Responsable puede cancelar la solicitud (RF33 CA2).

### Eliminar
- [x] **CA19**: Dado el Responsable, cuando elimina un caso escribiendo su número exacto, entonces el caso y sus accesos se eliminan, la auditoría conserva la constancia y se avisa a quienes tenían acceso; con otro número no se elimina (RF32 CA1 a CA3).
- [x] **CA20**: Dado un caso En análisis, entonces no se puede cerrar ni eliminar (RF27 CA2, RF32 CA4).

### Reglas de la 004
- [x] **CA21**: Dado un miembro Responsable de casos de la organización, cuando intenta abandonarla, entonces se le exige transferirlos antes (RF17 CA2).
- [x] **CA22**: Dado un miembro desvinculado, entonces sus casos de la organización pasan al Referente y pierde todos sus accesos a casos de la organización (RF14 CA2, RN14).
- [x] **CA23**: Dada la eliminación de una organización, entonces la confirmación informa cuántos casos se eliminarán y se eliminan junto con ella (RF18, RN09).

### Auditoría
- [x] **CA24**: Cada operación sobre casos, exitosa o rechazada, queda en la auditoría con el caso como recurso.

## Preguntas abiertas

- Ninguna que bloquee. RN12, RN14 y RF33 CA2 siguen marcadas como propuestas en la especificación general.
