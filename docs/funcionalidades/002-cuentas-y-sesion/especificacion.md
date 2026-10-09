# Especificación: 002 — Cuentas y sesión

- **Rama**: `funcionalidad/002-cuentas-y-sesion`
- **Estado**: Borrador
- **Requisitos que realiza**: RF01, RF02, RF03, RF04, RF05, RF06, RF07; RNF01; RNF02 (CA2, CA3); RNF04 (CA1); RNF08 (CA1, CA2, CA7)
- **Reglas de negocio aplicadas**: RN01, RN02, RN03, RN04
- **Casos de uso**: CU01, CU02, CU03, CU04, CU05

## Problema

Para usar la plataforma, abogados y personal de aseguradoras necesitan una cuenta propia y segura. La cuenta identifica a quien solicita cada análisis y permite, en funcionalidades posteriores, proteger los casos y compartirlos. Como la plataforma trata información sensible (imágenes de siniestros que pueden contener datos de salud), la autenticación debe cumplir estándares de seguridad y el registro debe obtener el consentimiento expreso que exige la Ley N.° 25.326.

## Alcance

### Incluido

**Registro y verificación (RF01, RF02)**
- Formulario de registro con nombre, apellido, correo, contraseña, perfil (Abogado o Aseguradora) y, según el perfil, colegio de abogados o empresa (opcionales).
- Aceptación expresa de los Términos de Uso y de la Política de Privacidad, con registro de la versión aceptada y la fecha.
- Correo de verificación con enlace temporal; la cuenta solo se activa al verificarla.
- Reenvío del correo de verificación.

**Sesión (RF03, RF04)**
- Inicio de sesión con correo y contraseña.
- Bloqueo temporal de la cuenta tras intentos fallidos consecutivos.
- Cierre de sesión manual y automático por inactividad o por duración máxima.

**Contraseña (RF05, RF06)**
- Recuperación mediante enlace enviado por correo, válido por 1 hora y de un solo uso.
- Cambio de contraseña desde el perfil, indicando la contraseña actual.
- Política de contraseñas y almacenamiento con bcrypt.

**Perfil (RF07)**
- Consulta y edición de nombre, apellido y colegio o empresa.
- Cambio de correo con confirmación en la dirección nueva y aviso a la anterior.
- El perfil (Abogado o Aseguradora) se muestra pero no puede modificarse.

**Interfaz**
- Pantallas de registro, verificación, inicio de sesión, recuperación, restablecimiento y perfil.
- Rutas protegidas: sin sesión, la aplicación redirige al inicio de sesión.
- Encabezado con el nombre del usuario y la opción de cerrar sesión.
- Páginas de Términos de Uso y Política de Privacidad, con texto provisorio versionado.

**Correo**
- Envío de los correos de esta funcionalidad, en español, capturados por Mailpit en desarrollo.

### Excluido

- Registro de las acciones en la auditoría (RF03 CA4, RF07 CA1): funcionalidad 003.
- Eliminación de la cuenta (RF08) y copia de los datos personales (RF09): funcionalidad 019.
- Cuenta y tablero del Administrador: funcionalidad 014.
- Envío de correos en segundo plano: en esta funcionalidad el envío es directo; pasa a la cola de tareas en la funcionalidad 007.
- Envío real de correos con Amazon SES: funcionalidad 017.
- Texto definitivo de los Términos de Uso y la Política de Privacidad: debe validarse con los tutores.

## Criterios de aceptación

### Registro y verificación
- [ ] **CA1**: Dado un visitante, cuando completa el registro con datos válidos y acepta los términos, entonces la cuenta queda pendiente de verificación y llega un correo de verificación a Mailpit.
- [ ] **CA2**: Dado un visitante que no acepta los términos, cuando envía el formulario, entonces el registro se rechaza indicando que la aceptación es obligatoria.
- [ ] **CA3**: Dado un correo ya registrado, cuando alguien intenta registrarse con él, entonces se muestra el mismo mensaje que en un registro exitoso y el titular recibe un aviso por correo.
- [ ] **CA4**: Dada una contraseña con menos de 10 caracteres, sin letras, sin números o presente en la lista de contraseñas comunes, cuando se envía el formulario, entonces se rechaza indicando la condición incumplida.
- [ ] **CA5**: Dado un registro exitoso, entonces quedan guardadas la versión de los términos aceptados y la fecha y hora de aceptación.
- [ ] **CA6**: Dado un enlace de verificación vigente, cuando se abre, entonces la cuenta queda activa; dado un enlace vencido (más de 24 horas) o ya usado, entonces se informa el motivo y se ofrece reenviar el correo.

### Sesión
- [ ] **CA7**: Dadas credenciales válidas de una cuenta activa, cuando se inicia sesión, entonces se accede a la aplicación y se muestra el nombre del usuario.
- [ ] **CA8**: Dadas credenciales inválidas, cuando se intenta iniciar sesión, entonces se muestra un mensaje genérico que no indica qué dato es incorrecto.
- [ ] **CA9**: Dada una cuenta no verificada, cuando intenta iniciar sesión, entonces se rechaza el acceso y se ofrece reenviar el correo de verificación.
- [ ] **CA10**: Dados 5 intentos fallidos consecutivos, entonces la cuenta se bloquea 15 minutos y el titular recibe un aviso por correo.
- [ ] **CA11**: Dado un usuario autenticado, cuando cierra sesión, entonces cualquier solicitud posterior con la misma cookie es rechazada.
- [ ] **CA12**: Dada una sesión inactiva por 30 minutos, o iniciada hace más de 8 horas, entonces la siguiente solicitud exige iniciar sesión nuevamente.

### Contraseña
- [ ] **CA13**: Dado un correo registrado, cuando se solicita la recuperación, entonces llega un enlace válido por 1 hora; dado un correo no registrado, entonces se muestra el mismo mensaje y no se envía ningún correo.
- [ ] **CA14**: Dado un enlace de recuperación vigente, cuando se define una contraseña válida, entonces la contraseña cambia, el enlace deja de funcionar y se cierran las sesiones abiertas de esa cuenta.
- [ ] **CA15**: Dado un enlace de recuperación vencido, alterado o ya usado, entonces se rechaza y se ofrece solicitar uno nuevo.
- [ ] **CA16**: Dado un usuario autenticado, cuando cambia su contraseña indicando la actual correcta, entonces se actualiza y recibe un aviso por correo; con la actual incorrecta, se rechaza.

### Perfil
- [ ] **CA17**: Dado un usuario autenticado, cuando modifica su nombre, apellido o colegio o empresa, entonces los cambios se guardan.
- [ ] **CA18**: Dado un usuario que cambia su correo, entonces el cambio queda pendiente hasta confirmar el enlace enviado a la dirección nueva, y la dirección anterior recibe un aviso.
- [ ] **CA19**: Dado un usuario autenticado, cuando intenta modificar su perfil (Abogado o Aseguradora), entonces la operación se rechaza.

### Seguridad
- [ ] **CA20**: Las contraseñas se almacenan únicamente como hash bcrypt con costo 12 o mayor.
- [ ] **CA21**: La cookie de sesión tiene los atributos `HttpOnly` y `SameSite=Strict` (y `Secure` en producción), y toda solicitud que modifica datos sin un token CSRF válido es rechazada.
- [ ] **CA22**: Sin sesión iniciada, las pantallas protegidas redirigen al inicio de sesión y la API responde 401.

## Preguntas abiertas

- Texto definitivo de los Términos de Uso y de la Política de Privacidad: se usa un texto provisorio hasta validarlo con los tutores.
