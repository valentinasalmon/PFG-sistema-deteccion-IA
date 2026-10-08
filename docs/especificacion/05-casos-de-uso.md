# 5. Casos de uso

## 5.1 Inventario

| ID | Caso de uso | Actor principal | Requisitos |
|---|---|---|---|
| CU01 | Registrarse | Visitante | RF01, RF02 |
| CU02 | Iniciar sesión | Visitante | RF03 |
| CU03 | Cerrar sesión | Usuario | RF04 |
| CU04 | Recuperar contraseña | Visitante | RF05 |
| CU05 | Gestionar perfil propio | Usuario | RF06, RF07 |
| CU06 | Eliminar cuenta propia | Usuario | RF08 |
| CU07 | Solicitar copia de datos personales | Usuario | RF09 |
| CU08 | Crear organización | Usuario | RF10 |
| CU09 | Editar datos de la organización | Referente | RF11 |
| CU10 | Invitar miembro | Referente | RF12 |
| CU11 | Responder invitación | Visitante / Usuario | RF13 |
| CU12 | Gestionar miembros | Referente | RF14, RF15 |
| CU13 | Consultar miembros | Miembro | RF16 |
| CU14 | Abandonar organización | Miembro / Referente | RF17 |
| CU15 | Eliminar organización | Referente | RF18 |
| CU16 | Consultar plan y consumo | Usuario / Referente | RF19, RF20 |
| CU17 | Consultar tablero de administración | Administrador | RF21, RF22 |
| CU18 | Crear caso | Usuario | RF23 |
| CU19 | Buscar y consultar casos | Usuario | RF24, RF26 |
| CU20 | Editar caso | Responsable / Colaborador | RF25 |
| CU21 | Cambiar estado del caso | Responsable | RF27, RF28, RF29 |
| CU22 | Compartir caso y gestionar accesos | Responsable | RF30, RF31 |
| CU23 | Transferir caso | Responsable | RF33 |
| CU24 | Eliminar caso | Responsable | RF32 |
| CU25 | Cargar imágenes | Responsable / Colaborador | RF34, RF35, RF37 |
| CU26 | Eliminar imagen | Responsable / Colaborador | RF36 |
| CU27 | Analizar imágenes | Responsable / Colaborador | RF38, RF46 |
| CU28 | Procesar análisis y generar informe | Sistema | RF39 – RF44, RF47 |
| CU29 | Consultar y descargar informes | Responsable / Colaborador / Lector | RF45 |
| CU30 | Consultar panel principal | Usuario | RF48 |
| CU31 | Prorrogar retención | Responsable | RF51 |
| CU32 | Aplicar política de retención | Sistema | RF49, RF50 |

## 5.2 Relaciones entre casos de uso

- **CU01** se extiende desde **CU11** cuando el invitado no está registrado.
- **CU06** incluye **CU23** o **CU24** por cada caso activo, y **CU12** (designar Referente) cuando corresponde.
- **CU14** incluye **CU23** cuando el miembro es Responsable de casos de la organización, y se extiende a **CU15** cuando el Referente es el único miembro.
- **CU27** desencadena **CU28**, que se ejecuta en segundo plano.
- **CU25** desencadena el sellado de tiempo (RF37) en segundo plano.
- **CU32** desencadena el aviso de RF50 y, al vencer el plazo, la destrucción con la misma lógica que **CU24**.

Precondición común a todos los casos de uso cuyo actor es Usuario, Referente, Miembro, Responsable, Colaborador, Lector o Administrador: **el actor ha iniciado sesión**. Postcondición común a todos: **la operación queda registrada en la auditoría** (RNF06).

---

## 5.3 Especificación

### CU01 — Registrarse

| | |
|---|---|
| **Actor** | Visitante |
| **Objetivo** | Obtener una cuenta para usar la plataforma. |
| **Precondiciones** | El visitante no ha iniciado sesión. |
| **Postcondiciones** | Existe una cuenta activa con el consentimiento registrado. |

**Flujo principal**
1. El visitante selecciona "Crear cuenta".
2. El sistema muestra el formulario: nombre, apellido, correo, contraseña, confirmación, perfil (Abogado o Aseguradora) y casillas de aceptación de Términos de Uso y Política de Privacidad, con enlaces a ambos documentos.
3. El visitante elige el perfil; el sistema muestra el campo opcional correspondiente (colegio de abogados o empresa).
4. El visitante completa los datos, acepta los términos y confirma.
5. El sistema valida los datos, crea la cuenta pendiente de verificación, registra el consentimiento y envía el correo de verificación.
6. El visitante abre el enlace del correo.
7. El sistema activa la cuenta y lo dirige al inicio de sesión.

**Flujos alternativos**
- **4a. Datos inválidos o términos no aceptados:** el sistema señala cada campo con error junto al campo; vuelve al paso 4.
- **5a. Correo ya registrado:** el sistema muestra el mismo mensaje de éxito y envía al titular un aviso de intento de registro.
- **6a. Enlace vencido:** el sistema informa el vencimiento y ofrece reenviar el correo.
- **7a. Registro originado en una invitación:** tras la activación, el sistema continúa con CU11.

### CU02 — Iniciar sesión

| | |
|---|---|
| **Actor** | Visitante |
| **Objetivo** | Acceder a la plataforma. |
| **Precondiciones** | Existe una cuenta activa. |
| **Postcondiciones** | Hay una sesión autenticada. |

**Flujo principal**
1. El visitante ingresa correo y contraseña.
2. El sistema valida las credenciales, crea la sesión y muestra el panel principal (CU30), o el tablero (CU17) si es Administrador.

**Flujos alternativos**
- **2a. Credenciales inválidas:** el sistema muestra un mensaje genérico e incrementa el contador de intentos.
- **2b. Quinto intento fallido:** el sistema bloquea la cuenta 15 minutos y notifica al titular.
- **2c. Cuenta no verificada:** el sistema ofrece reenviar el correo de verificación.

### CU03 — Cerrar sesión

**Actor:** Usuario. **Flujo principal:** 1. El usuario selecciona "Cerrar sesión". 2. El sistema invalida la sesión y muestra la pantalla de inicio de sesión.
**Flujo alternativo:** 1a. La sesión supera el tiempo de inactividad: el sistema la cierra y, en la siguiente acción, solicita iniciar sesión nuevamente.

### CU04 — Recuperar contraseña

| | |
|---|---|
| **Actor** | Visitante |
| **Objetivo** | Recuperar el acceso ante el olvido de la contraseña. |
| **Postcondiciones** | La contraseña fue reemplazada y las sesiones anteriores fueron cerradas. |

**Flujo principal**
1. El visitante selecciona "Olvidé mi contraseña" e ingresa su correo.
2. El sistema muestra un mensaje genérico y, si el correo existe, envía un enlace válido por 1 hora.
3. El visitante abre el enlace e ingresa la nueva contraseña dos veces.
4. El sistema valida la política, actualiza la contraseña, invalida el token, cierra las sesiones abiertas y notifica por correo.

**Flujos alternativos**
- **3a. Enlace vencido, alterado o utilizado:** el sistema lo informa y ofrece solicitar uno nuevo.
- **4a. Contraseña que no cumple la política:** el sistema indica la condición incumplida; vuelve al paso 3.

### CU05 — Gestionar perfil propio

**Actor:** Usuario. **Objetivo:** mantener actualizados sus datos personales y su contraseña.

**Flujo principal**
1. El usuario accede a "Mi perfil".
2. El sistema muestra sus datos personales.
3. El usuario modifica nombre, apellido, colegio o empresa y confirma.
4. El sistema guarda los cambios.

**Flujos alternativos**
- **3a. Cambio de correo:** el sistema envía un enlace de confirmación a la nueva dirección y un aviso a la anterior; el cambio se aplica al confirmar.
- **3b. Cambio de contraseña:** el usuario ingresa la contraseña actual y la nueva; el sistema valida, actualiza y notifica por correo.
- **4a. Contraseña actual incorrecta:** el sistema rechaza el cambio.

### CU06 — Eliminar cuenta propia

| | |
|---|---|
| **Actor** | Usuario |
| **Objetivo** | Ejercer el derecho de supresión de sus datos. |
| **Postcondiciones** | Los datos personales fueron suprimidos y la auditoría quedó anonimizada. |

**Flujo principal**
1. El usuario selecciona "Eliminar mi cuenta".
2. El sistema informa las consecuencias y verifica las condiciones previas.
3. El sistema solicita la contraseña como confirmación.
4. El usuario la ingresa y confirma.
5. El sistema elimina la cuenta, suprime los datos personales, cierra las sesiones, anonimiza la auditoría y envía un correo de confirmación.

**Flujos alternativos**
- **2a. El usuario es Responsable de casos activos:** el sistema lista los casos y, para cada uno, el usuario elige transferirlo (CU23) o eliminarlo (CU24). El flujo no continúa hasta que no quede ninguno.
- **2b. El usuario es Referente de organizaciones con otros miembros:** el sistema exige designar un nuevo Referente en cada una (CU12).
- **2c. El usuario es el único miembro de una organización:** el sistema advierte que la organización y sus casos se eliminarán (CU15).

### CU07 — Solicitar copia de datos personales

**Actor:** Usuario.

**Flujo principal**
1. El usuario selecciona "Descargar mis datos".
2. El sistema genera la copia en JSON y en PDF.
3. El sistema notifica por correo y muestra el enlace de descarga.
4. El usuario descarga la copia mediante una URL firmada.

### CU08 — Crear organización

**Actor:** Usuario. **Postcondiciones:** existe la organización con el usuario como Referente.

**Flujo principal**
1. El usuario selecciona "Crear organización".
2. El sistema solicita nombre, tipo (Estudio Jurídico o Aseguradora) y datos de contacto.
3. El usuario completa y confirma.
4. El sistema crea la organización con su plan inicial y designa al usuario como Referente.
5. El sistema ofrece invitar miembros (CU10).

**Flujo alternativo:** 3a. Datos inválidos: el sistema señala los errores; vuelve al paso 3.

### CU09 — Editar datos de la organización

**Actor:** Referente. **Flujo principal:** 1. El Referente accede a la configuración de la organización. 2. Modifica los datos y confirma. 3. El sistema valida y guarda los cambios.

### CU10 — Invitar miembro

| | |
|---|---|
| **Actor** | Referente |
| **Postcondiciones** | Existe una invitación pendiente y el invitado recibió un correo. |

**Flujo principal**
1. El Referente selecciona "Invitar miembro".
2. El sistema solicita el correo del invitado y, opcionalmente, su cargo.
3. El Referente confirma.
4. El sistema verifica el límite de miembros del plan, crea la invitación con vencimiento de 7 días y envía el correo.
5. El sistema muestra la invitación como pendiente en el listado de miembros.

**Flujos alternativos**
- **4a. Límite del plan alcanzado:** el sistema rechaza la invitación indicando el límite.
- **4b. El correo ya es miembro:** el sistema rechaza la invitación.
- **5a. Reenviar o cancelar:** el Referente reenvía la invitación (se renueva el vencimiento) o la cancela.

### CU11 — Responder invitación

| | |
|---|---|
| **Actor** | Visitante o Usuario invitado |
| **Precondiciones** | Existe una invitación vigente. |
| **Postcondiciones** | El invitado es Miembro, o la invitación queda rechazada. |

**Flujo principal**
1. El invitado abre el enlace del correo.
2. El sistema verifica la vigencia del token y muestra la organización que invita.
3. El invitado inicia sesión con el correo invitado.
4. El invitado acepta.
5. El sistema lo incorpora como Miembro y notifica al Referente.

**Flujos alternativos**
- **2a. Invitación vencida o cancelada:** el sistema lo informa y finaliza.
- **3a. El invitado no tiene cuenta:** se ejecuta CU01 con el correo precargado y luego se retoma en el paso 4.
- **3b. Sesión iniciada con un correo distinto:** el sistema rechaza la aceptación e indica con qué correo debe ingresar.
- **4a. El invitado rechaza:** el sistema marca la invitación como rechazada y notifica al Referente.

### CU12 — Gestionar miembros

**Actor:** Referente.

**Flujo principal (editar membresía)**
1. El Referente accede al listado de miembros y elige un miembro.
2. Modifica el cargo o área y confirma.
3. El sistema guarda el cambio sin alterar los datos personales del miembro.

**Flujos alternativos**
- **2a. Desvincular:** el Referente selecciona "Desvincular" y confirma; el sistema retira la membresía, transfiere al Referente la responsabilidad de los casos de la organización a cargo del miembro, revoca sus accesos y lo notifica.
- **2b. Designar Referente:** el Referente selecciona "Designar como Referente" y confirma; el sistema intercambia los roles y notifica a ambos.

### CU13 — Consultar miembros

**Actor:** Miembro. **Flujo principal:** 1. El miembro accede a la organización. 2. El sistema muestra los miembros con su nombre, perfil, cargo, rol y fecha de incorporación.

### CU14 — Abandonar organización

**Actor:** Miembro o Referente.

**Flujo principal**
1. El miembro selecciona "Abandonar organización".
2. El sistema verifica las condiciones previas y solicita confirmación.
3. El miembro confirma.
4. El sistema retira la membresía, revoca sus accesos a los casos de la organización y notifica al Referente.

**Flujos alternativos**
- **2a. El miembro es Responsable de casos de la organización:** el sistema exige transferirlos a otro miembro (CU23).
- **2b. El actor es el Referente:** el sistema exige designar un nuevo Referente (CU12).
- **2c. El actor es el único miembro:** el sistema advierte que la organización se eliminará y continúa con CU15.

### CU15 — Eliminar organización

**Actor:** Referente.

**Flujo principal**
1. El Referente selecciona "Eliminar organización".
2. El sistema muestra la cantidad de casos y miembros afectados y solicita escribir el nombre de la organización.
3. El Referente escribe el nombre y confirma.
4. El sistema elimina los casos del espacio (con la lógica de CU24), las membresías y la organización, y notifica a los miembros.

**Flujo alternativo:** 3a. El nombre no coincide: el sistema no habilita la confirmación.

### CU16 — Consultar plan y consumo

**Actor:** Usuario (espacio personal) o Referente (organización). **Flujo principal:** 1. El actor accede a "Plan". 2. El sistema muestra el plan, sus límites y el consumo del período. **Nota:** la contratación o el cambio de plan están **[A DEFINIR]** (CP-01).

### CU17 — Consultar tablero de administración

| | |
|---|---|
| **Actor** | Administrador |
| **Postcondiciones** | La consulta queda registrada en la auditoría. |

**Flujo principal**
1. El Administrador inicia sesión.
2. El sistema muestra el tablero con los indicadores agregados.
3. El Administrador filtra por rango de fechas.
4. El sistema actualiza los indicadores.

**Flujos alternativos**
- **2a. Consultar listados:** el Administrador accede al listado de usuarios u organizaciones, en modo de solo lectura, con búsqueda, filtros y paginación.

### CU18 — Crear caso

| | |
|---|---|
| **Actor** | Usuario |
| **Postcondiciones** | Existe un caso en estado Borrador con el usuario como Responsable. |

**Flujo principal**
1. El usuario selecciona "Nuevo caso".
2. El sistema solicita espacio de trabajo (Personal o alguna de sus organizaciones), tipo, fecha del hecho, lugar, expediente (opcional) y descripción (opcional).
3. El usuario completa y confirma.
4. El sistema valida, asigna el número de caso y crea el caso en Borrador.
5. El sistema muestra el detalle del caso y ofrece cargar imágenes (CU25).

**Flujos alternativos**
- **2a. El usuario no pertenece a ninguna organización:** el espacio Personal se selecciona automáticamente.
- **4a. Datos inválidos (por ejemplo, fecha futura):** el sistema señala los errores; vuelve al paso 3.

### CU19 — Buscar y consultar casos

**Actor:** Usuario.

**Flujo principal**
1. El usuario accede a "Casos".
2. El sistema muestra los casos accesibles, excluidos los archivados, paginados y ordenados por última actualización.
3. El usuario aplica filtros (número, expediente, estado, tipo, espacio, fechas).
4. El sistema muestra los resultados.
5. El usuario selecciona un caso.
6. El sistema muestra el detalle con las acciones que su permiso habilita.

**Flujos alternativos**
- **4a. Sin resultados:** el sistema lo informa y ofrece limpiar los filtros.
- **6a. El usuario no tiene permiso:** el sistema responde que el caso no existe.

### CU20 — Editar caso

**Actor:** Responsable o Colaborador. **Precondiciones:** el caso está en Borrador o Analizado.
**Flujo principal:** 1. El actor selecciona "Editar". 2. Modifica los datos y confirma. 3. El sistema valida, guarda y registra los valores anteriores y nuevos.
**Flujo alternativo:** 1a. El caso está Cerrado o Archivado: la opción no está disponible y se sugiere reabrirlo.

### CU21 — Cambiar estado del caso

**Actor:** Responsable.

**Flujo principal (cerrar)**
1. El Responsable selecciona "Cerrar caso" en un caso en Borrador o Analizado.
2. El sistema informa que el caso quedará en solo lectura y que comenzará el plazo de retención de 2 años, con su fecha de vencimiento.
3. El Responsable confirma.
4. El sistema cambia el estado a Cerrado y registra la fecha de inicio de la retención.

**Flujos alternativos**
- **1a. Archivar:** sobre un caso Cerrado; el sistema lo pasa a Archivado y lo oculta del listado por defecto.
- **1b. Desarchivar:** sobre un caso Archivado; el sistema lo devuelve a Cerrado sin reiniciar el plazo.
- **1c. Reabrir:** sobre un caso Cerrado o Archivado; el sistema lo pasa a Analizado o Borrador y detiene el plazo de retención.
- **1d. Caso En análisis:** el sistema impide el cambio hasta que el análisis finalice.

### CU22 — Compartir caso y gestionar accesos

| | |
|---|---|
| **Actor** | Responsable |
| **Precondiciones** | El caso pertenece al espacio de una organización. |

**Flujo principal**
1. El Responsable selecciona "Compartir".
2. El sistema muestra los accesos actuales y permite elegir destinatario: un miembro de la organización o "Toda la organización".
3. El Responsable elige destinatario y permiso (Lectura o Colaboración) y confirma.
4. El sistema otorga el acceso y notifica a los destinatarios.

**Flujos alternativos**
- **1a. Caso del espacio personal:** la opción no está disponible y se informa que compartir requiere una organización.
- **3a. Revocar:** el Responsable revoca un acceso; el sistema lo retira de inmediato y notifica al afectado.
- **3b. Modificar:** el Responsable cambia el nivel de un acceso; el sistema lo aplica y notifica.

### CU23 — Transferir caso

**Actor:** Responsable.

**Flujo principal**
1. El Responsable selecciona "Transferir".
2. El sistema muestra los posibles destinatarios: miembros de la organización del caso o, si es personal, un campo para indicar el correo de otro usuario registrado.
3. El Responsable elige al destinatario, indica si conserva permiso de Colaboración y confirma.
4. El sistema asigna al nuevo Responsable y notifica a ambos.

**Flujo alternativo:** 4a. Caso personal: el destinatario recibe una solicitud de transferencia y el cambio se aplica cuando la acepta **[PROPUESTA]**.

### CU24 — Eliminar caso

| | |
|---|---|
| **Actor** | Responsable |
| **Postcondiciones** | No queda rastro del caso salvo la constancia en la auditoría. |

**Flujo principal**
1. El Responsable selecciona "Eliminar caso".
2. El sistema advierte que la operación es irreversible y solicita escribir el número de caso.
3. El Responsable lo escribe y confirma.
4. El sistema elimina los datos, las imágenes y los informes, incluidas todas sus versiones en S3.
5. El sistema registra en la auditoría la operación y las huellas de los archivos, y notifica a los usuarios con acceso.

**Flujos alternativos**
- **1a. Caso En análisis:** el sistema impide la eliminación hasta que el análisis finalice.
- **3a. Número incorrecto:** el sistema no habilita la confirmación.

### CU25 — Cargar imágenes

| | |
|---|---|
| **Actor** | Responsable o Colaborador |
| **Precondiciones** | El caso está en Borrador o Analizado. |
| **Postcondiciones** | Las imágenes válidas quedan almacenadas con su huella y con el sellado solicitado. |

**Flujo principal**
1. El actor selecciona "Cargar imágenes" y elige uno o más archivos, o los arrastra.
2. El sistema verifica la firma binaria, el tamaño y el límite del plan de cada archivo.
3. El sistema calcula la huella SHA-256, almacena el archivo en S3 y registra sus datos.
4. El sistema muestra el resultado de cada archivo y la galería actualizada.
5. El sistema solicita en segundo plano el sello de tiempo de cada huella en Blockchain Federal Argentina.

**Flujos alternativos**
- **2a. Formato real inválido:** el archivo se rechaza con el motivo; los demás continúan.
- **2b. Tamaño o límite excedido:** el archivo se rechaza indicando el límite.
- **3a. Huella duplicada en el caso:** el sistema advierte el duplicado y no lo almacena.
- **5a. Falla del servicio de sellado:** el sistema reintenta en segundo plano; la imagen queda utilizable con el sello en estado pendiente o fallido.

### CU26 — Eliminar imagen

**Actor:** Responsable o Colaborador. **Precondiciones:** el caso está en Borrador o Analizado.
**Flujo principal:** 1. El actor selecciona "Eliminar" sobre una imagen. 2. El sistema solicita confirmación. 3. El actor confirma. 4. El sistema elimina el archivo y sus versiones y registra la operación con la huella.
**Flujo alternativo:** 1a. La imagen forma parte de un informe: la opción no está disponible y se informa el motivo.

### CU27 — Analizar imágenes

| | |
|---|---|
| **Actor** | Responsable o Colaborador |
| **Precondiciones** | El caso está en Borrador o Analizado y tiene al menos una imagen. |
| **Postcondiciones** | El análisis queda encolado y el caso En análisis. |

**Flujo principal**
1. El actor selecciona las imágenes a analizar (por defecto, las no analizadas aún).
2. El actor presiona "Analizar".
3. El sistema verifica el límite mensual de análisis del plan.
4. El sistema encola el análisis, cambia el estado del caso a En análisis y muestra el progreso.
5. El sistema ejecuta CU28 en segundo plano.
6. Al finalizar, la interfaz muestra el resultado y el enlace al informe.

**Flujos alternativos**
- **3a. Límite mensual alcanzado:** el sistema rechaza la solicitud indicando el límite y la fecha de renovación.
- **4a. Ya hay un análisis en curso:** el sistema impide encolar otro.
- **6a. El actor abandona la pantalla:** el análisis continúa y se notifica por correo al finalizar.

### CU28 — Procesar análisis y generar informe

| | |
|---|---|
| **Actor** | Sistema (proceso de trabajo) |
| **Precondiciones** | Existe un análisis encolado. |
| **Postcondiciones** | Existe un informe PDF inmutable en S3, el caso está Analizado y se notificó al solicitante. |

**Flujo principal**
1. El proceso toma el análisis de la cola y lo marca En proceso.
2. Para cada imagen, recalcula la huella SHA-256 y verifica que coincida con la registrada.
3. Para cada imagen ejecuta, en forma independiente, las capas 1 (metadatos), 2 (C2PA), 3 (ELA) y 4 (red neuronal), y almacena para cada una el nivel de indicio, las anomalías, la conclusión y los archivos derivados.
4. El sistema genera el informe PDF con los resultados, las huellas, los sellos de tiempo, las versiones de los componentes y la advertencia legal.
5. El sistema almacena el informe en S3, lo asocia al caso y marca como no eliminables las imágenes incluidas.
6. El sistema cambia el estado del caso a Analizado y notifica por correo al solicitante y al Responsable.

**Flujos alternativos**
- **2a. La huella no coincide:** la imagen se excluye y el informe registra la anomalía de integridad.
- **3a. Falla una capa:** su resultado se registra como "No disponible" con el motivo y se continúa con las demás.
- **1a / 4a. Falla general del proceso:** se reintenta hasta 3 veces; si persiste, el análisis queda Fallido, el caso vuelve a su estado anterior, no se descuenta del plan y se notifica al solicitante.

### CU29 — Consultar y descargar informes

**Actor:** Responsable, Colaborador o Lector.
**Flujo principal:** 1. El actor accede a la sección "Informes" del caso. 2. El sistema muestra el historial con fecha, solicitante e imágenes incluidas. 3. El actor selecciona "Descargar". 4. El sistema verifica el permiso, registra la descarga y entrega una URL firmada que vence a los 5 minutos.

### CU30 — Consultar panel principal

**Actor:** Usuario.
**Flujo principal:** 1. El usuario inicia sesión o selecciona "Inicio". 2. El sistema muestra los casos por estado, los últimos casos actualizados, los análisis en curso, los casos compartidos recientemente, las invitaciones pendientes, los casos próximos a su destrucción y la actividad reciente. 3. El usuario selecciona un elemento y el sistema navega al recurso correspondiente.

### CU31 — Prorrogar retención

**Actor:** Responsable. **Precondiciones:** el caso está Cerrado o Archivado. **[PROPUESTA]**
**Flujo principal:** 1. El Responsable selecciona "Prorrogar conservación". 2. El sistema solicita el motivo. 3. El Responsable lo indica y confirma. 4. El sistema extiende la fecha de destrucción 1 año y registra el motivo en la auditoría.
**Flujo alternativo:** 3a. Motivo vacío: el sistema no habilita la confirmación.

### CU32 — Aplicar política de retención

| | |
|---|---|
| **Actor** | Sistema (tarea programada diaria) |
| **Postcondiciones** | Se avisó sobre los casos próximos a vencer y se destruyeron los vencidos. |

**Flujo principal**
1. La tarea identifica los casos Cerrados o Archivados cuyo vencimiento ocurre en 30 días y aún no fueron avisados.
2. Para cada uno, envía el aviso al Responsable y lo marca como avisado.
3. La tarea identifica los casos cuyo plazo venció sin prórroga.
4. Para cada uno, ejecuta la destrucción con la lógica de CU24 y registra la operación en la auditoría.

**Flujo alternativo:** 4a. Falla al eliminar un archivo en S3: se registra el error, el caso queda marcado para reintento en la próxima ejecución y no se informa como destruido hasta completar la eliminación.
