# 3. Requisitos funcionales

Cada requisito indica su prioridad, las reglas de negocio que aplica y sus criterios de aceptación (CA) en formato *Dado / Cuando / Entonces*.

## Resumen

| Módulo | Requisitos |
|---|---|
| M1. Cuentas y sesión | RF01 – RF09 |
| M2. Organizaciones | RF10 – RF18 |
| M3. Planes y administración | RF19 – RF22 |
| M4. Casos | RF23 – RF33 |
| M5. Imágenes | RF34 – RF37 |
| M6. Análisis e informes | RF38 – RF46 |
| M7. Notificaciones y panel | RF47 – RF48 |
| M8. Retención de datos | RF49 – RF51 |
| M9. Ampliaciones del 2026-10-25 | RF52 – RF56 |

---

## M1. Cuentas y sesión

### RF01 — Registrar usuario
**Prioridad:** Debe · **Reglas:** RN01, RN02, RN03

El sistema debe permitir que un visitante se registre indicando nombre, apellido, correo electrónico, contraseña y perfil (Abogado o Aseguradora), con la aceptación explícita de los Términos de Uso y de la Política de Privacidad. Según el perfil, puede declarar opcionalmente el colegio de abogados o la empresa.

- **CA1:** Dado un visitante en el formulario de registro, cuando completa los datos obligatorios y acepta los términos, entonces se crea la cuenta en estado *pendiente de verificación* y se envía un correo de verificación.
- **CA2:** Dado un visitante que no marca la aceptación de los términos, cuando envía el formulario, entonces el registro se rechaza indicando que la aceptación es obligatoria.
- **CA3:** Dado un correo ya registrado, cuando un visitante intenta registrarse con él, entonces el sistema muestra un mensaje genérico que no revela si el correo existe y envía un aviso al titular de esa cuenta.
- **CA4:** Dada una contraseña que no cumple la política de RNF01, cuando se envía el formulario, entonces el registro se rechaza indicando qué condición no se cumple.
- **CA5:** Dado un registro exitoso, entonces quedan almacenadas la versión de los Términos y de la Política aceptadas, junto con la fecha y hora de aceptación.

### RF02 — Verificar correo electrónico
**Prioridad:** Debe · **Reglas:** RN03

El sistema debe exigir la verificación del correo electrónico mediante un enlace con token temporal antes de permitir el primer inicio de sesión.

- **CA1:** Dado un usuario pendiente de verificación, cuando abre el enlace vigente, entonces la cuenta queda activa.
- **CA2:** Dado un enlace vencido (más de 24 horas) o ya utilizado, cuando se abre, entonces se informa el motivo y se ofrece reenviar el correo.
- **CA3:** Dado un usuario no verificado, cuando intenta iniciar sesión, entonces se rechaza el acceso y se ofrece reenviar el correo de verificación.

### RF03 — Iniciar sesión
**Prioridad:** Debe

El sistema debe permitir iniciar sesión con correo y contraseña.

- **CA1:** Dadas credenciales válidas de una cuenta activa, cuando el usuario inicia sesión, entonces accede a su panel principal (RF48).
- **CA2:** Dadas credenciales inválidas, cuando se intenta iniciar sesión, entonces se muestra un mensaje genérico que no indica cuál de los datos es incorrecto.
- **CA3:** Dados cinco intentos fallidos consecutivos sobre una misma cuenta, entonces la cuenta se bloquea temporalmente según RNF01.
- **CA4:** Dado cualquier intento de inicio de sesión, exitoso o fallido, entonces queda registrado en la auditoría (RNF06).

### RF04 — Cerrar sesión
**Prioridad:** Debe

El sistema debe permitir cerrar la sesión activa.

- **CA1:** Dado un usuario autenticado, cuando cierra sesión, entonces la sesión se invalida en el servidor y cualquier solicitud posterior con la misma cookie es rechazada.
- **CA2:** Dada una sesión inactiva durante el tiempo definido en RNF01, entonces se cierra automáticamente.

### RF05 — Recuperar contraseña
**Prioridad:** Debe

El sistema debe permitir restablecer la contraseña mediante un enlace enviado por correo, con un token firmado que vence a la hora de emitido.

- **CA1:** Dado un correo registrado, cuando se solicita la recuperación, entonces se envía un enlace válido por 1 hora.
- **CA2:** Dado un correo no registrado, cuando se solicita la recuperación, entonces se muestra el mismo mensaje que en CA1 y no se envía ningún correo.
- **CA3:** Dado un enlace vigente, cuando el usuario define una contraseña válida, entonces la contraseña se actualiza, el token queda invalidado y se cierran todas las sesiones abiertas de esa cuenta.
- **CA4:** Dado un enlace vencido, alterado o ya utilizado, cuando se abre, entonces se rechaza y se ofrece solicitar uno nuevo.

### RF06 — Cambiar contraseña
**Prioridad:** Debe

El sistema debe permitir a un usuario autenticado cambiar su contraseña indicando la contraseña actual.

- **CA1:** Dada la contraseña actual correcta y una nueva contraseña válida, cuando se confirma, entonces la contraseña se actualiza y se envía un aviso por correo.
- **CA2:** Dada una contraseña actual incorrecta, cuando se confirma, entonces el cambio se rechaza.

### RF07 — Editar perfil propio
**Prioridad:** Debe · **Reglas:** RN02, RN04

El sistema debe permitir al usuario modificar sus datos personales (nombre, apellido, correo, colegio o empresa). El perfil (Abogado o Aseguradora) **no puede modificarse** después del registro (RN01, CP-12).

- **CA1:** Dado un usuario autenticado, cuando modifica su nombre o apellido, entonces los cambios se guardan y se registran en la auditoría.
- **CA2:** Dado un usuario que cambia su correo, entonces el cambio queda pendiente hasta que confirme el enlace enviado a la nueva dirección, y se envía un aviso a la dirección anterior.
- **CA3:** Dado cualquier otro usuario, incluidos el Referente y el Administrador, entonces el sistema no ofrece ninguna operación para modificar los datos personales de terceros.
- **CA4:** Dado un usuario autenticado, cuando intenta modificar su perfil (Abogado o Aseguradora), entonces la operación se rechaza.

### RF08 — Eliminar cuenta propia
> **Planificación:** se implementa en la funcionalidad 019, después de la 005, porque depende de que existan casos y organizaciones.

**Prioridad:** Debe · **Reglas:** RN05, RN08, RN34

El sistema debe permitir al usuario eliminar su cuenta, exigiendo previamente que resuelva la situación de sus casos activos y de las organizaciones que referencia.

- **CA1:** Dado un usuario Responsable de casos activos, cuando solicita eliminar su cuenta, entonces el sistema lista esos casos y exige elegir para cada uno *transferir* (RF33) o *eliminar* (RF32) antes de continuar.
- **CA2:** Dado un usuario que es el único Referente de una organización con otros miembros, cuando solicita eliminar su cuenta, entonces el sistema exige designar un nuevo Referente (RF15).
- **CA3:** Dadas las condiciones resueltas, cuando el usuario confirma con su contraseña, entonces la cuenta y sus datos personales se suprimen, se cierran sus sesiones y la auditoría conserva sus entradas con el usuario anonimizado.
- **CA4:** Dada la eliminación completada, entonces se envía un correo de confirmación a la dirección de la cuenta eliminada.

### RF09 — Solicitar copia de datos personales
> **Planificación:** se implementa en la funcionalidad 019, después de la 005, porque depende de que existan casos y organizaciones.

**Prioridad:** Debe · **Reglas:** RN04

El sistema debe permitir al usuario obtener una copia de los datos personales que el sistema almacena sobre él (derecho de acceso, Ley N.° 25.326, art. 14).

- **CA1:** Dado un usuario autenticado, cuando solicita la copia, entonces el sistema genera un archivo descargable (JSON y PDF legible) con sus datos de cuenta, membresías, consentimientos aceptados y la lista de casos de los que es Responsable.
- **CA2:** Dada la copia generada, entonces se entrega mediante una URL firmada de corta duración y se notifica por correo.
- **CA3:** La copia no incluye datos personales de terceros ni el contenido de casos ajenos.
- **CA4:** Dada una solicitud, entonces la entrega se produce en un plazo inferior a 10 días corridos (art. 14, inc. 2); el objetivo del sistema es entregarla en forma inmediata.

---

## M2. Organizaciones

### RF10 — Crear organización
**Prioridad:** Debe · **Reglas:** RN06, RN07, RN15

El sistema debe permitir a un usuario crear una organización indicando nombre, tipo (Estudio Jurídico o Aseguradora) y datos de contacto, y designar automáticamente al creador como Referente.

- **CA1:** Dado un usuario autenticado, cuando crea una organización con datos válidos, entonces la organización queda creada con su plan inicial **[A DEFINIR]** y el creador como Referente.
- **CA2:** Dado un usuario que ya pertenece a otras organizaciones, cuando crea una nueva, entonces conserva todas sus membresías anteriores.

### RF11 — Editar datos de la organización
**Prioridad:** Debe

El sistema debe permitir al Referente modificar el nombre, el tipo y los datos de contacto de la organización.

- **CA1:** Dado el Referente, cuando modifica los datos, entonces se guardan y se registran en la auditoría.
- **CA2:** Dado un Miembro que no es Referente, entonces no puede modificar los datos de la organización.

### RF12 — Invitar miembros
**Prioridad:** Debe · **Reglas:** RN10, RN15

El sistema debe permitir al Referente invitar personas por correo electrónico, estén o no registradas.

- **CA1:** Dado el Referente, cuando invita a un correo registrado, entonces se envía un correo con un enlace para aceptar o rechazar la invitación.
- **CA2:** Dado el Referente, cuando invita a un correo no registrado, entonces se envía un correo con un enlace que lleva al registro (RF01) y, una vez verificada la cuenta, a la aceptación de la invitación.
- **CA3:** Dado que la organización alcanzó el límite de miembros de su plan, cuando se intenta invitar, entonces la operación se rechaza indicando el límite.
- **CA4:** Dada una invitación pendiente, el Referente puede reenviarla o cancelarla.
- **CA5:** Dado un correo que ya es miembro de la organización, cuando se lo invita, entonces la operación se rechaza.

### RF13 — Responder invitación
**Prioridad:** Debe · **Reglas:** RN10

El sistema debe permitir aceptar o rechazar una invitación vigente.

- **CA1:** Dado un usuario autenticado con el mismo correo de la invitación, cuando la acepta, entonces se incorpora como Miembro y se notifica al Referente.
- **CA2:** Dado un usuario autenticado con un correo distinto al invitado, cuando abre el enlace, entonces se rechaza la aceptación.
- **CA3:** Dada una invitación vencida o cancelada, cuando se abre el enlace, entonces se informa que no está vigente.

### RF14 — Desvincular miembro
**Prioridad:** Debe · **Reglas:** RN14

El sistema debe permitir al Referente desvincular a un miembro de la organización.

- **CA1:** Dado el Referente, cuando desvincula a un miembro, entonces este pierde de inmediato el acceso a los casos de la organización y se le notifica por correo.
- **CA2:** Dado un miembro desvinculado que era Responsable de casos de la organización, entonces la responsabilidad de esos casos pasa al Referente.
- **CA3:** El Referente no puede desvincularse a sí mismo; debe usar RF17 previa designación de un nuevo Referente.

### RF15 — Gestionar membresías y designar Referente
**Prioridad:** Debe · **Reglas:** RN07, RN08, RN11

El sistema debe permitir al Referente editar los datos de la membresía (cargo o área) de cada miembro y transferir el rol de Referente a otro miembro.

- **CA1:** Dado el Referente, cuando modifica el cargo de un miembro, entonces se guarda sin alterar los datos personales del miembro.
- **CA2:** Dado el Referente, cuando designa a otro miembro como Referente, entonces el designado pasa a ser Referente, el anterior pasa a ser Miembro y ambos son notificados.

### RF16 — Consultar miembros de la organización
**Prioridad:** Debe

El sistema debe permitir a cualquier miembro consultar el listado de miembros de su organización.

- **CA1:** Dado un miembro, cuando consulta el listado, entonces ve nombre, perfil, cargo, rol en la organización y fecha de incorporación de cada miembro.
- **CA2:** Dado un usuario que no pertenece a la organización, entonces no puede consultar su listado.

### RF17 — Abandonar organización
**Prioridad:** Debe · **Reglas:** RN08, RN14

El sistema debe permitir a cualquier miembro abandonar voluntariamente una organización.

- **CA1:** Dado un Miembro sin casos a cargo en la organización, cuando la abandona, entonces pierde el acceso a sus casos y se notifica al Referente.
- **CA2:** Dado un Miembro Responsable de casos de la organización, cuando intenta abandonarla, entonces el sistema exige transferir esos casos a otro miembro.
- **CA3:** Dado el Referente, cuando intenta abandonarla, entonces el sistema exige designar previamente un nuevo Referente; si es el único miembro, se le advierte que la organización se eliminará (RF18).

### RF18 — Eliminar organización
**Prioridad:** Debería · **Reglas:** RN09

El sistema debe permitir al Referente eliminar la organización.

- **CA1:** Dado el Referente, cuando solicita eliminar la organización, entonces el sistema muestra la cantidad de casos que se eliminarán y exige escribir el nombre de la organización como confirmación.
- **CA2:** Dada la confirmación, entonces se eliminan la organización y todos los casos de su espacio aplicando RN21, y se notifica a todos los miembros.

---

## M3. Planes y administración

### RF19 — Aplicar límites de uso por plan
**Prioridad:** Debe · **Reglas:** RN13, RN15

El sistema debe controlar, para cada espacio de trabajo, las capacidades y límites de su plan: posibilidad de compartir, cantidad de miembros, análisis por mes, imágenes por caso y almacenamiento.

- **CA1:** Dado un caso del espacio personal, entonces la opción de compartir no está disponible.
- **CA2:** Dado un espacio que alcanzó su límite mensual de análisis, cuando se solicita un análisis, entonces se rechaza indicando el límite y la fecha de renovación.
- **CA3:** Dado un cambio en los valores de un plan, entonces se aplica sin modificar el código, mediante configuración o datos.

### RF20 — Consultar plan y consumo
**Prioridad:** Debería

El sistema debe permitir al usuario consultar el plan de su espacio personal y al Referente el plan de su organización, junto con el consumo del período.

- **CA1:** Dado el Referente, cuando consulta el plan, entonces ve el nombre del plan, los límites y el consumo actual de cada uno.
- **CA2:** Dado el Referente, cuando elige otro plan, entonces recorre un flujo de pago **simulado**, que se presenta como tal y no pide datos de pago, y al confirmarlo el plan se aplica de inmediato con sus límites y queda registrado en la auditoría como pago simulado (CP-01).

### RF21 — Consultar tablero de administración
**Prioridad:** Debe · **Reglas:** RN35

El sistema debe ofrecer al Administrador un tablero con estadísticas agregadas: cantidad de usuarios por perfil, organizaciones por tipo y por plan, casos por estado y por tipo, análisis realizados por período y altas de usuarios en el tiempo.

- **CA1:** Dado el Administrador, cuando accede al tablero, entonces ve los indicadores con la posibilidad de filtrar por rango de fechas.
- **CA2:** Ningún indicador permite identificar ni abrir un caso, una imagen o un informe.
- **CA3:** Dado un usuario que no es Administrador, cuando intenta acceder al tablero, entonces se le deniega el acceso.

### RF22 — Consultar listados de usuarios y organizaciones
**Prioridad:** Debe · **Reglas:** RN04, RN35

El sistema debe permitir al Administrador consultar, en modo de solo lectura, el listado global de usuarios (nombre, correo, perfil, estado, fecha de alta) y de organizaciones (nombre, tipo, plan, cantidad de miembros).

- **CA1:** Dado el Administrador, cuando consulta los listados, entonces puede buscar, filtrar y paginar, pero no dispone de operaciones de modificación.
- **CA2:** Los listados no muestran los casos de usuarios ni de organizaciones.

---

## M4. Casos

### RF23 — Crear caso
**Prioridad:** Debe · **Reglas:** RN12, RN16, RN17

El sistema debe permitir crear un caso indicando espacio de trabajo (personal o una organización de la que el usuario es miembro), tipo (Automovilístico o Laboral), fecha del hecho, lugar y, opcionalmente, expediente y descripción.

- **CA1:** Dados datos válidos, cuando se crea el caso, entonces el sistema le asigna un número de caso único, el estado Borrador y al creador como Responsable.
- **CA2:** Dada una fecha del hecho posterior a la fecha actual, entonces se rechaza la creación.
- **CA3:** Dado un usuario que intenta crear un caso en una organización de la que no es miembro, entonces se rechaza la operación.

### RF24 — Consultar detalle del caso
**Prioridad:** Debe · **Reglas:** RN20

El sistema debe permitir consultar el detalle de un caso: datos, estado, imágenes, historial de análisis e informes, accesos compartidos y plazo de retención.

- **CA1:** Dado un usuario con algún permiso sobre el caso, cuando lo consulta, entonces ve el detalle y únicamente las acciones que su permiso habilita.
- **CA2:** Dado un usuario sin permiso, cuando intenta acceder al caso, entonces el sistema responde como si el caso no existiera (RNF05).

### RF25 — Editar caso
**Prioridad:** Debe · **Reglas:** RN16, RN19, RN20

El sistema debe permitir al Responsable y a los Colaboradores modificar el tipo, la fecha del hecho, el lugar, el expediente y la descripción.

- **CA1:** Dado un Colaborador y un caso en estado Borrador o Analizado, cuando modifica los datos, entonces se guardan y se registra en la auditoría el valor anterior y el nuevo de cada campo.
- **CA2:** Dado un caso Cerrado o Archivado, entonces no se permite la edición.
- **CA3:** El número de caso no puede modificarse.

### RF26 — Listar, buscar y filtrar casos
**Prioridad:** Debe

El sistema debe permitir listar los casos a los que el usuario tiene acceso y buscarlos y filtrarlos por número de caso, expediente, estado, tipo, espacio de trabajo y rango de fechas.

- **CA1:** Dado un usuario, cuando abre el listado, entonces ve sus casos y los compartidos con él, paginados y ordenados por última actualización, excluyendo los Archivados.
- **CA2:** Dado un filtro por estado Archivado, entonces se muestran los casos archivados.
- **CA3:** Dada una búsqueda por expediente, entonces la coincidencia es parcial y no distingue mayúsculas, minúsculas ni acentos.
- **CA4:** Los resultados nunca incluyen casos sobre los que el usuario no tiene permiso.

### RF27 — Cerrar caso
**Prioridad:** Debe · **Reglas:** RN18, RN19, RN30

El sistema debe permitir al Responsable cerrar un caso en estado Borrador o Analizado.

- **CA1:** Dado el Responsable, cuando cierra el caso, entonces pasa a Cerrado, queda en solo lectura y comienza el cómputo del plazo de retención, cuya fecha de vencimiento se muestra en el detalle.
- **CA2:** Dado un caso En análisis, entonces no puede cerrarse hasta que el análisis finalice.

### RF28 — Archivar y desarchivar caso
**Prioridad:** Debe · **Reglas:** RN18, RN30

El sistema debe permitir al Responsable archivar un caso Cerrado y desarchivarlo.

- **CA1:** Dado un caso Cerrado, cuando se archiva, entonces pasa a Archivado y deja de mostrarse en el listado por defecto.
- **CA2:** Dado un caso Archivado, cuando se desarchiva, entonces vuelve a Cerrado y el cómputo de retención continúa sin reiniciarse.

### RF29 — Reabrir caso
**Prioridad:** Debe · **Reglas:** RN18, RN30

El sistema debe permitir al Responsable reabrir un caso Cerrado o Archivado.

- **CA1:** Dado un caso Cerrado o Archivado con informes, cuando se reabre, entonces pasa a Analizado; sin informes, pasa a Borrador.
- **CA2:** Dada la reapertura, entonces el cómputo de retención se detiene y se elimina la fecha de vencimiento.

### RF30 — Compartir caso
**Prioridad:** Debe · **Reglas:** RN13, RN20

El sistema debe permitir al Responsable compartir un caso de una organización con miembros puntuales o con toda la organización, con permiso de Lectura o de Colaboración.

- **CA1:** Dado un caso de organización, cuando el Responsable lo comparte con un miembro, entonces ese miembro obtiene el permiso elegido y recibe una notificación.
- **CA2:** Dado un caso compartido con toda la organización, entonces todos los miembros actuales y futuros obtienen el permiso elegido mientras pertenezcan a ella.
- **CA3:** Si un usuario tiene más de un permiso (individual y por organización), prevalece el de mayor nivel.
- **CA4:** Dado un caso del espacio personal, entonces la opción de compartir no está disponible (RF19).
- **CA5:** Dado un usuario que no pertenece a la organización del caso, entonces no puede ser elegido como destinatario.

### RF31 — Revocar o modificar accesos
**Prioridad:** Debe

El sistema debe permitir al Responsable revocar un acceso compartido o cambiar su nivel.

- **CA1:** Dado un acceso revocado, entonces el usuario pierde el acceso de inmediato, incluida la descarga de informes mediante URL firmadas emitidas a partir de ese momento.
- **CA2:** Dado un cambio de nivel, entonces se aplica a la siguiente solicitud del usuario afectado.

### RF32 — Eliminar caso
**Prioridad:** Debe · **Reglas:** RN20, RN21

El sistema debe permitir al Responsable eliminar definitivamente un caso.

- **CA1:** Dado el Responsable, cuando solicita eliminar un caso, entonces el sistema advierte que la operación es irreversible y exige escribir el número de caso como confirmación.
- **CA2:** Dada la confirmación, entonces se eliminan los datos del caso, sus imágenes y sus informes, incluidas todas las versiones en S3, y se notifica a los usuarios con acceso.
- **CA3:** Dada la eliminación, entonces la auditoría conserva la constancia de la operación y las huellas SHA-256 de los archivos eliminados, sin su contenido.
- **CA4:** Dado un caso En análisis, entonces no puede eliminarse hasta que el análisis finalice.

### RF33 — Transferir responsabilidad del caso
**Prioridad:** Debe · **Reglas:** RN12, RN14

El sistema debe permitir al Responsable transferir la responsabilidad de un caso a otro usuario.

- **CA1:** Dado un caso de organización, cuando se transfiere a otro miembro de esa organización, entonces el destinatario pasa a ser Responsable y el anterior conserva permiso de Colaboración, salvo que indique lo contrario.
- **CA2:** Dado un caso del espacio personal, cuando se transfiere a otro usuario registrado, entonces el destinatario debe aceptar la transferencia y el caso pasa a su espacio personal **[PROPUESTA]**.
- **CA3:** Dada una transferencia, entonces se notifica a ambos usuarios y se registra en la auditoría.

---

## M5. Imágenes

### RF34 — Cargar imágenes
**Prioridad:** Debe · **Reglas:** RN15, RN19, RN22, RN23

El sistema debe permitir al Responsable y a los Colaboradores cargar una o más imágenes JPEG o PNG en un caso en estado Borrador o Analizado.

- **CA1:** Dado un archivo cuyo contenido corresponde a JPEG o PNG y no supera el tamaño máximo, cuando se carga, entonces se almacena en S3 cifrado, se calcula su huella SHA-256 y se registran nombre original, tamaño, formato, dimensiones, huella y usuario que lo cargó.
- **CA2:** Dado un archivo con extensión `.jpg` cuyo contenido no es JPEG, entonces se rechaza indicando que el formato real no es válido.
- **CA3:** Dado un archivo que supera el tamaño máximo o que excede el límite de imágenes por caso del plan, entonces se rechaza indicando el límite.
- **CA4:** Dada una imagen con la misma huella que otra ya cargada en el caso, entonces se advierte que es un duplicado y no se vuelve a almacenar.
- **CA5:** Dada una carga de varios archivos, entonces cada archivo se valida en forma independiente y se informa el resultado de cada uno.

### RF35 — Consultar imágenes del caso
**Prioridad:** Debe

El sistema debe permitir consultar las imágenes de un caso con su vista previa y sus datos técnicos.

- **CA1:** Dado un usuario con permiso sobre el caso, cuando consulta las imágenes, entonces ve una vista previa, el nombre original, el tamaño, la huella SHA-256, la fecha de carga, el estado del sello de tiempo y los informes en los que fue incluida.
- **CA2:** Las vistas previas se sirven mediante URL firmadas de corta duración.

### RF36 — Eliminar imagen
**Prioridad:** Debe · **Reglas:** RN19, RN24

El sistema debe permitir al Responsable y a los Colaboradores eliminar una imagen que no forme parte de un informe generado.

- **CA1:** Dada una imagen no incluida en ningún informe, cuando se elimina, entonces se borra de S3 con todas sus versiones y se registra en la auditoría con su huella.
- **CA2:** Dada una imagen incluida en un informe, entonces la opción de eliminar no está disponible y se informa el motivo.

### RF37 — Registrar sello de tiempo en Hedera
**Prioridad:** Debería · **Reglas:** RN23

El sistema debe registrar la huella SHA-256 de cada imagen cargada en Hedera Consensus Service, sin enviar el archivo (ADR-0018, reemplaza a Blockchain Federal Argentina).

- **CA1:** Dada una imagen cargada, entonces el sistema solicita el sello de tiempo en segundo plano y registra su estado (pendiente, sellado o fallido).
- **CA2:** Dado un sello confirmado, entonces se almacenan la referencia de la transacción y la fecha del sello, y se incluyen en el informe.
- **CA3:** Dada una falla del servicio externo, entonces se reintenta en forma automática y la falla no impide cargar ni analizar la imagen.
- **CA4:** El componente de sellado es intercambiable (patrón Strategy), de modo que puede reemplazarse por una implementación simulada en desarrollo y pruebas.
- **CA5:** El mensaje publicado en Hedera contiene solo la huella y el tipo de registro, sin datos personales ni del caso. La referencia guardada (tema, número de secuencia y fecha de consenso) permite verificar el sello en un explorador público.

---

## M6. Análisis e informes

### RF38 — Solicitar análisis
**Prioridad:** Debe · **Reglas:** RN15, RN19, RN25

El sistema debe permitir al Responsable y a los Colaboradores solicitar el análisis de una o más imágenes del caso mediante el botón "Analizar".

- **CA1:** Dado un caso en Borrador o Analizado con al menos una imagen, cuando se seleccionan imágenes y se solicita el análisis, entonces el análisis se encola, el caso pasa a En análisis y la interfaz muestra el progreso.
- **CA2:** Dado que el usuario no selecciona imágenes, entonces el botón "Analizar" permanece deshabilitado.
- **CA3:** Dado un caso que ya está En análisis, entonces no se puede solicitar otro análisis hasta que finalice.
- **CA4:** Antes de procesar cada imagen, el sistema recalcula su huella SHA-256 y, si no coincide con la registrada, la excluye del análisis y lo informa como anomalía de integridad.

### RF39 — Ejecutar capa 1: metadatos EXIF/XMP
**Prioridad:** Debe · **Reglas:** RN26, RN27

El sistema debe extraer los metadatos EXIF y XMP con ExifTool y Pillow y detectar anomalías como software de edición declarado, historial de ediciones, fechas imposibles o inconsistentes y ausencia de metadatos esperables.

- **CA1:** Dada una imagen con el campo `Software` que declara un editor conocido, entonces se informa como anomalía.
- **CA2:** Dada una fecha de captura posterior a la fecha de carga, o anterior a la fecha de fabricación conocida del dispositivo declarado, entonces se informa como fecha imposible.
- **CA3:** Dada una imagen sin metadatos, entonces se informa su ausencia como dato, aclarando que puede deberse a la recompresión de plataformas de mensajería y que no implica manipulación por sí misma.
- **CA4:** El resultado incluye una tabla con los metadatos relevantes extraídos.

### RF40 — Ejecutar capa 2: credenciales de contenido C2PA
**Prioridad:** Debe · **Reglas:** RN26, RN27, RN28

El sistema debe leer el manifiesto C2PA con c2pa-python y verificar su firma contra la lista de confianza del consorcio.

- **CA1:** Dado un manifiesto válido que declara generación por IA, entonces el nivel de indicio es el máximo y se informa como el indicio más fuerte del sistema.
- **CA2:** Dado un manifiesto con firma inválida o emitida por un firmante fuera de la lista de confianza, entonces se informa como anomalía con el detalle de la validación.
- **CA3:** Dada una imagen sin manifiesto, entonces se informa "Sin credenciales de contenido", aclarando que su ausencia no constituye evidencia de autenticidad.
- **CA4:** Dado un manifiesto válido, entonces se informan el firmante, la herramienta declarada y las acciones registradas.

### RF41 — Ejecutar capa 3: análisis de niveles de error (ELA)
**Prioridad:** Debe · **Reglas:** RN26, RN27

El sistema debe aplicar ELA por bloques y señalar las regiones con un nivel de error significativamente distinto al resto de la imagen.

- **CA1:** Dada una imagen JPEG, entonces se genera un mapa ELA y se identifican los bloques cuyo nivel de error se aparta del comportamiento general según un umbral documentado.
- **CA2:** Dada una imagen PNG, entonces el resultado aclara que ELA tiene validez limitada en formatos sin pérdida.
- **CA3:** El resultado incluye la imagen del mapa ELA con las regiones señaladas y la aclaración de que se trata de una señal complementaria.

### RF42 — Ejecutar capa 4: clasificador de redes neuronales
**Prioridad:** Debe · **Reglas:** RN26, RN27, RN29

El sistema debe estimar con un clasificador de redes neuronales convolucionales, ejecutado con ONNX Runtime, la probabilidad de que la imagen sea íntegramente sintética.

- **CA1:** Dada una imagen, entonces se informa la probabilidad estimada de que sea sintética y la versión del modelo utilizado.
- **CA2:** El resultado aclara que el modelo no detecta ediciones parciales y que su desempeño puede disminuir frente a generadores no vistos durante el entrenamiento.
- **CA3:** El modelo se carga una sola vez por proceso de trabajo y no en cada solicitud.

### RF43 — Presentar resultado por capa
**Prioridad:** Debe · **Reglas:** RN26, RN27

Cada capa debe devolver un nivel de indicio de 0 % a 100 %, una lista de anomalías y una conclusión redactada como indicio, con la recomendación de consultar a un profesional especializado.

- **CA1:** Dado el resultado de cualquier capa, entonces contiene los tres elementos y el método de cálculo del nivel de indicio está documentado.
- **CA2:** Ninguna conclusión utiliza términos de veredicto como "falsa", "auténtica" o "adulterada" en forma afirmativa.
- **CA3:** Dada la falla de una capa, entonces su resultado es "No disponible" con el motivo, y las demás capas se presentan normalmente.
- **CA4:** El sistema no calcula ni muestra un puntaje que combine las cuatro capas.

### RF44 — Generar informe PDF
**Prioridad:** Debe · **Reglas:** RN25, RN27, RN29

Al finalizar cada análisis, el sistema debe generar un informe PDF en español, sencillo y explicativo, y almacenarlo en S3.

- **CA1:** El informe incluye: número de caso y expediente, tipo, fecha y lugar; solicitante con su perfil y colegio o empresa; fecha y hora del análisis; por cada imagen, su vista reducida, huella SHA-256 y estado del sello de tiempo; por cada capa, nivel de indicio, anomalías y conclusión; versiones de los componentes; y una sección de limitaciones y advertencia legal.
- **CA2:** Cada capa se explica en lenguaje no técnico, con un recuadro "¿Qué significa?".
- **CA3:** Dado un análisis finalizado, entonces el caso pasa a Analizado y se notifica por correo a quien lo solicitó (RF47).
- **CA4:** El informe almacenado no se modifica nunca; un nuevo análisis genera un informe nuevo.

### RF45 — Consultar historial y descargar informes
**Prioridad:** Debe

El sistema debe permitir consultar el historial de informes de un caso y descargar cualquiera de ellos.

- **CA1:** Dado un usuario con permiso sobre el caso, cuando consulta el historial, entonces ve cada informe con su fecha, solicitante e imágenes incluidas, ordenados del más reciente al más antiguo.
- **CA2:** Dada una solicitud de descarga, entonces el sistema verifica el permiso y entrega una URL firmada que vence a los 5 minutos.

### RF46 — Consultar estado del análisis
**Prioridad:** Debe

El sistema debe informar el estado de un análisis en curso: en cola, en proceso (con la capa e imagen en curso), finalizado o fallido.

- **CA1:** Dado un análisis en curso, cuando el usuario consulta el caso, entonces ve el progreso actualizado sin recargar manualmente la página.
- **CA2:** Dada una falla general (por ejemplo, la caída del proceso de trabajo), entonces el análisis queda Fallido, el caso vuelve a su estado anterior, se notifica al solicitante y no se descuenta del límite del plan.

---

## M7. Notificaciones y panel

### RF47 — Notificar eventos por correo electrónico
**Prioridad:** Debe

El sistema debe enviar correos automáticos en español, mediante Amazon SES, ante los siguientes eventos:

| Evento | Destinatario |
|---|---|
| Verificación de correo y cambio de correo | Usuario |
| Recuperación y cambio de contraseña | Usuario |
| Invitación a una organización | Invitado |
| Invitación aceptada, abandono de la organización | Referente |
| Desvinculación de la organización, designación como Referente | Miembro afectado |
| Caso compartido, transferido o con acceso revocado | Usuario afectado |
| Análisis finalizado o fallido (informe generado) | Solicitante y Responsable |
| Caso eliminado | Usuarios con acceso |
| Aviso de destrucción por retención | Responsable |
| Copia de datos personales disponible | Usuario |
| Cuenta eliminada | Usuario |

- **CA1:** Dado cualquiera de los eventos, entonces el correo se envía en segundo plano y su falla no revierte la operación que lo originó.
- **CA2:** Los correos no incluyen imágenes, informes ni datos sensibles del caso: solo el número de caso y un enlace a la plataforma.
- **CA3:** Dada una falla de envío, entonces se reintenta y se registra en el log de la aplicación.

### RF48 — Consultar panel principal
**Prioridad:** Debe

Al iniciar sesión, el sistema debe mostrar un panel con un resumen de los casos del usuario y la actividad reciente.

- **CA1:** El panel muestra la cantidad de casos por estado, los últimos casos actualizados, los análisis en curso, los casos compartidos recientemente, las invitaciones pendientes y los casos próximos a su destrucción por retención.
- **CA2:** La actividad reciente muestra los últimos eventos de los casos a los que el usuario tiene acceso (por ejemplo, "Ana López cargó 3 imágenes en CASO-2026-000123").
- **CA3:** Cada elemento del panel permite navegar al caso correspondiente.

---

## M8. Retención de datos

### RF49 — Destruir datos por vencimiento de retención
**Prioridad:** Debe · **Reglas:** RN30, RN33

El sistema debe ejecutar diariamente una tarea programada que destruya los casos cuyo plazo de retención haya vencido.

- **CA1:** Dado un caso Cerrado o Archivado cuyo plazo venció sin prórroga, cuando se ejecuta la tarea, entonces se destruye aplicando RN21.
- **CA2:** Dada la destrucción, entonces se registra en la auditoría con el número de caso y las huellas de los archivos destruidos.
- **CA3:** Las copias de respaldo de la base de datos vencen en un plazo acotado (RNF13), de modo que los datos destruidos no se conserven indefinidamente en los respaldos.

### RF50 — Avisar la destrucción próxima
**Prioridad:** Debe · **Reglas:** RN31

El sistema debe avisar al Responsable 30 días antes de la destrucción.

- **CA1:** Dado un caso a 30 días de su destrucción, entonces se envía un correo al Responsable y el caso se destaca en su panel.

### RF51 — Prorrogar la retención
**Prioridad:** Debería · **Reglas:** RN32 **[PROPUESTA]**

El sistema debe permitir al Responsable prorrogar el plazo de retención por 1 año, indicando un motivo.

- **CA1:** Dado un caso Cerrado o Archivado, cuando el Responsable registra una prórroga con motivo, entonces la fecha de destrucción se extiende 1 año y el motivo queda en la auditoría.
- **CA2:** Dada una prórroga sin motivo, entonces se rechaza.

---

## M9. Ampliaciones del 2026-10-25

Requisitos agregados a pedido de la autora. Los marcados **[PROPUESTA]** dependen de las cuestiones abiertas CP-26 a CP-31. El detalle de la carga desde el celular está en `docs/investigacion/2026-10-25-carga-desde-el-celular.md`.

### RF52 — Iniciar sesión y registrarse con Google
**Prioridad:** Debería · **Reglas:** RN01, RN02 **[PROPUESTA]**

El sistema debe permitir iniciar sesión y registrarse con una cuenta de Google (OpenID Connect), además del correo y la contraseña.

- **CA1:** Dado un visitante que elige "Continuar con Google" y autoriza el acceso, cuando su correo no está registrado, entonces completa los datos que Google no provee (perfil Abogado o Aseguradora, colegio o empresa, aceptación de los Términos y de la Política) y la cuenta queda activa sin verificación por correo, porque Google ya verificó el correo.
- **CA2:** Dado un correo ya registrado con contraseña, cuando la persona entra con Google por primera vez, entonces se vincula a la misma cuenta solo si Google informa el correo como verificado.
- **CA3:** El inicio de sesión con Google queda registrado en la auditoría igual que el inicio con contraseña.

### RF53 — Cargar imágenes desde el celular
**Prioridad:** Debe · **Reglas:** RN19, RN22, RN23 **[PROPUESTA]**

El sistema debe permitir cargar imágenes desde un celular Android o iOS, ya sea sacando la foto en el momento o eligiéndola de la galería, sin instalar una aplicación.

- **CA1:** Dado un usuario en el celular, cuando abre un caso, entonces puede usar la cámara o la galería desde el navegador y la carga sigue las mismas validaciones de RF34.
- **CA2:** Dado un usuario en la computadora, cuando elige "Cargar desde el celular", entonces se muestra un código QR de un solo uso, que vence en 15 minutos, para cargar imágenes en ese caso sin iniciar sesión en el celular.
- **CA3:** Las imágenes HEIC/HEIF (formato por defecto del iPhone) se aceptan, se conservan tal cual como original y se genera una vista previa compatible.
- **CA4:** Se advierte que algunos celulares quitan la ubicación de la foto al elegirla de la galería, y que sacarla en el momento conserva más metadatos.

### RF54 — Informe adaptado al rubro
**Prioridad:** Debe · **Reglas:** RN27, RN29 **[PROPUESTA]**

El informe PDF debe usar el lenguaje del rubro de quien lo solicita (Legal o Seguros), ser más breve y entenderse sin usar la plataforma.

- **CA1:** Dado un solicitante con perfil Abogado, entonces el informe usa términos de expediente, prueba y perito; con perfil Aseguradora, términos de siniestro, liquidación y verificación.
- **CA2:** El informe se entiende por sí mismo: explica qué se analizó, cómo leer los niveles, qué limitaciones tiene y cómo verificar su autenticidad, sin depender de la plataforma.
- **CA3:** El detalle de las secciones lo define la autora (CP-28).

### RF55 — Informe inalterable y verificable
**Prioridad:** Debe · **Reglas:** RN23, RN29 **[PROPUESTA]**

El sistema debe registrar la huella SHA-256 de cada informe PDF en Hedera y permitir que cualquier persona compruebe que un PDF no fue modificado.

- **CA1:** Dado un informe generado, entonces su huella se registra en Hedera y la referencia queda guardada junto al informe.
- **CA2:** El PDF incluye un código QR y un código de verificación que llevan a una página pública de la plataforma.
- **CA3:** Dada una persona sin cuenta que sube un PDF en la página de verificación, cuando su huella coincide con la registrada, entonces ve la fecha de registro en Hedera y el enlace al explorador público. Si no coincide, se le informa que el documento fue modificado o no pertenece a la plataforma.
- **CA4:** (Opcional, CP-27) El PDF se firma digitalmente con el certificado de la plataforma, de modo que los lectores de PDF muestren una advertencia si se lo altera.

### RF56 — Registrar en Hedera cada versión desplegada
**Prioridad:** Debería · **Reglas:** RN29

El sistema debe registrar en Hedera la huella de cada versión que se despliega en producción, y cada análisis debe guardar con qué versión se hizo ("host tokenizado", CP-29).

- **CA1:** Dado un despliegue en producción, entonces se registra en Hedera un mensaje con el commit y la huella SHA-256 de los artefactos desplegados, y la referencia queda guardada.
- **CA2:** Dado un análisis, entonces el informe indica la versión del sistema con la que se hizo y su referencia en Hedera.
