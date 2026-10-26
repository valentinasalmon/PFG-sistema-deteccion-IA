# Especificación: 027 — Inicio de sesión y registro con Google

- **Rama**: `funcionalidad/027-inicio-con-google`
- **Estado**: Implementada (pendiente de probar con el cliente OAuth real)
- **Requisitos que realiza**: RF52; RNF01, RNF02, RNF06
- **Reglas de negocio aplicadas**: RN01, RN02, RN36, RN39
- **Casos de uso**: CU01 (registrarse), CU02 (iniciar sesión)

## Problema

Registrarse con correo y contraseña obliga a crear otra contraseña y a esperar el correo de verificación, que en modo de prueba de SES solo llega a destinatarios verificados. Con Google, abogados y liquidadores entran con la cuenta que ya usan.

La plataforma necesita además saber el rubro de cada persona (Abogado o Aseguradora), porque de él dependen el lenguaje, los permisos y el informe. Google no informa ese dato.

## Alcance

### Incluido
- Botón "Continuar con Google" en el inicio de sesión y en el registro, también desde el enlace de una invitación. Solo se muestra si el cliente de Google está configurado.
- Paso obligatorio "Completá tu registro" la primera vez (decisión de la autora, 2026-10-28):
  - perfil;
  - nombre y apellido, que vienen de Google y se pueden corregir;
  - colegio o aseguradora del catálogo de la SSN;
  - aceptación de los Términos.
- Vinculación con una cuenta existente con el mismo correo.
- Auditoría de cada inicio, rechazo, registro y vinculación.
- Configuración en Terraform y SSM, y guía para crear el cliente en Google Cloud.

### Excluido
- Desvincular Google desde el perfil (trabajo futuro).
- Otros proveedores, como Microsoft o Apple.
- Publicar la aplicación de Google para todo el público: se hace con el dominio propio (CP-30).

## Criterios de aceptación

- [x] **CA1**: Si el cliente de Google no está configurado, el botón no aparece y el acceso con correo y contraseña sigue igual. Si está configurado, el botón lleva a Google con `state`, `nonce` y PKCE (S256).
- [x] **CA2**: Si el correo que informa Google no tiene cuenta, la persona va a "Completá tu registro" y la cuenta todavía no se crea.
- [x] **CA3**: La cuenta solo se crea cuando la persona elige el perfil, completa la institución (la aseguradora es obligatoria para el perfil Aseguradora, RN36) y acepta los Términos. Además:
  - queda verificada, sin correo de verificación, y con la sesión iniciada;
  - el correo es siempre el que informó Google y no se puede cambiar.
- [x] **CA4**: El registro pendiente vence a los 15 minutos y se usa una sola vez. Sin él no se puede crear una cuenta con Google.
- [x] **CA5**: Una cuenta ya vinculada entra directamente, sin completar nada. La promoción a Administrador por configuración también se aplica.
- [x] **CA6**: Si el correo ya tiene una cuenta, se vincula solo si Google lo informa como verificado.
  - Si esa cuenta no estaba verificada, queda verificada, su contraseña se anula y se cierran sus sesiones. Así nadie que haya registrado antes ese correo ajeno conserva el acceso.
  - Si estaba verificada, su contraseña sigue sirviendo.
- [x] **CA7**: Una cuenta desactivada (RN39) tampoco entra con Google.
- [x] **CA8**: Se rechazan:
  - un `state` distinto o ausente;
  - la cancelación en Google;
  - un código rechazado;
  - un *ID token* con otra audiencia, otro emisor, vencido o con otro `nonce`.
  
  La persona vuelve al inicio de sesión con un aviso, y el motivo queda en la auditoría.
- [x] **CA9**: Todo queda en la auditoría con `metodo: google`: el inicio de sesión (exitoso o no), el registro y la vinculación (RF52 CA3).

## Preguntas abiertas

- CP-30: con la dirección `sslip.io`, Google podría rechazar la dirección de retorno. Si pasa, se prueba en local hasta comprar el dominio.
