# Especificación: 003 — Auditoría

- **Rama**: `funcionalidad/003-auditoria`
- **Estado**: En implementación
- **Requisitos que realiza**: RNF06 (CA1 a CA5, CA7 y CA8, para las acciones de cuenta y sesión); RF03 (CA4); RF07 (CA1, registro en la auditoría)
- **Reglas de negocio aplicadas**: RN34 (preparación: las entradas se conservan al eliminarse una cuenta)
- **Casos de uso**: postcondición común de los casos de uso con actor autenticado ("la operación queda registrada en la auditoría"), aplicada a CU01 a CU05

## Problema

La plataforma trata pruebas que pueden terminar en un juicio o en un reclamo a una aseguradora. Para que su uso sea defendible hace falta poder reconstruir, después de los hechos, quién hizo qué, cuándo, desde dónde y con qué resultado. Además, el registro permite detectar usos indebidos, como intentos de acceso a cuentas ajenas.

Esta funcionalidad crea el registro de auditoría y empieza a usarlo con las acciones de cuenta y sesión de la funcionalidad 002. Las funcionalidades siguientes (organizaciones, casos, imágenes, análisis, informes y retención) registran sus propias acciones sobre esta base.

## Alcance

### Incluido

**Registro de auditoría**
- Un registro único, de solo inserción, para todas las acciones relevantes del sistema.
- Cada entrada guarda: fecha y hora en UTC, usuario que actuó (si lo hay), dirección IP de origen, acción, tipo e identificador del recurso afectado, resultado (exitoso, fallido o rechazado) y detalle de los cambios.
- La acción y su entrada de auditoría se guardan juntas: si la entrada no puede guardarse, la acción se cancela.

**Acciones de la funcionalidad 002 que se registran**
- Registro de una cuenta, incluido el intento con un correo ya registrado.
- Verificación del correo y reenvío del enlace.
- Inicio de sesión exitoso y fallido (credenciales incorrectas, correo inexistente con el correo intentado, cuenta bloqueada o sin verificar).
- Bloqueo de la cuenta por intentos fallidos.
- Cierre de sesión manual y por duración máxima.
- Solicitud de recuperación y restablecimiento de la contraseña, incluido el uso de un enlace inválido.
- Cambio de contraseña desde el perfil.
- Edición del perfil, con el valor anterior y el nuevo de cada campo, e intento rechazado de cambiar el perfil.
- Solicitud y confirmación del cambio de correo, con el correo anterior y el nuevo.

**Información a la persona usuaria**
- La Política de Privacidad informa la existencia del registro de auditoría, qué datos guarda, su finalidad y su conservación de 5 años.

### Excluido

- Interfaz de consulta del registro: fuera del alcance del proyecto (visión y alcance).
- Acciones de organizaciones, casos, imágenes, análisis, informes, descargas y retención: se registran en las funcionalidades 004 a 016, cada una con sus propias acciones.
- Registro de las consultas del Administrador: funcionalidad 014.
- Eliminación automática de las entradas con más de 5 años: funcionalidad 015 (retención de datos).
- Anonimización de las entradas al eliminarse una cuenta (RNF06 CA5, RN34): funcionalidad 019.
- Cierre de sesión por inactividad: la sesión vence sola en el servidor, sin una solicitud que permita registrarlo.

## Criterios de aceptación

Precisados de RNF06 para las acciones de cuenta y sesión.

### Contenido de las entradas
- [ ] **CA1**: Dada cualquier acción registrada, entonces su entrada contiene la fecha y hora en UTC, el usuario que actuó (vacío si no había sesión ni cuenta identificable), la dirección IP de origen, la acción, el tipo y el identificador del recurso, el resultado y el detalle.
- [ ] **CA2**: Dada cualquier entrada, entonces no contiene contraseñas, hashes de contraseñas, tokens de enlaces, identificadores de sesión ni cookies.

### Sesión
- [ ] **CA3**: Dadas credenciales válidas, cuando se inicia sesión, entonces se registra un inicio de sesión exitoso del usuario.
- [ ] **CA4**: Dado un intento de inicio de sesión fallido, entonces se registra como fallido con su motivo (contraseña incorrecta, correo inexistente, cuenta bloqueada o sin verificar) y, si el correo no existe, el correo intentado; el mensaje que ve la persona sigue siendo el genérico.
- [ ] **CA5**: Dados 5 intentos fallidos consecutivos, cuando la cuenta se bloquea, entonces se registra el bloqueo con su vencimiento.
- [ ] **CA6**: Dado un usuario autenticado, cuando cierra sesión, o cuando su sesión se cierra por superar la duración máxima, entonces se registra el cierre indicando el motivo.

### Registro, verificación y contraseña
- [ ] **CA7**: Dado un registro, entonces se registra la creación de la cuenta; dado un registro con un correo ya existente, entonces se registra el intento sin revelarlo en la respuesta.
- [ ] **CA8**: Dada la verificación del correo o el pedido de reenvío, entonces se registran; dado un enlace vencido, alterado o ya usado, entonces se registra como fallido.
- [ ] **CA9**: Dada una solicitud de recuperación, entonces se registra con el correo indicado; dado un restablecimiento, entonces se registra como exitoso o, si el enlace no es válido, como fallido.
- [ ] **CA10**: Dado un cambio de contraseña desde el perfil, entonces se registra como exitoso o, si la contraseña actual es incorrecta, como fallido.

### Perfil y correo
- [ ] **CA11**: Dada una edición del perfil, entonces se registra el valor anterior y el nuevo de cada campo modificado; dado un intento de cambiar el perfil (Abogado o Aseguradora), entonces se registra como rechazado.
- [ ] **CA12**: Dada una solicitud de cambio de correo y su confirmación, entonces se registran ambas con el correo anterior y el nuevo.

### Integridad
- [ ] **CA13**: La aplicación no ofrece ninguna operación para modificar ni eliminar entradas del registro.
- [ ] **CA14**: Dada una acción cuya entrada de auditoría no puede guardarse, entonces la acción no se aplica y la persona recibe un mensaje de error genérico.

## Preguntas abiertas

- Ninguna. Las decisiones de esta funcionalidad quedaron resueltas el 2026-10-16: conservación de 5 años (CP-05), registro del correo intentado en los inicios de sesión fallidos y cancelación de la acción si la entrada no puede guardarse (RNF06 CA6 a CA8).
