# 2026-10-16 — Funcionalidad 021: organizaciones de aseguradoras

## Qué se hizo

La autora definió cómo trabajan las aseguradoras (CP-17): la empresa se registra desde el catálogo de la Superintendencia de Seguros, el Administrador de la plataforma aprueba el registro, los empleados se suman solo por invitación y, si se quedan sin aseguradora, su cuenta se desactiva. Los abogados siguen siendo individuales y pueden crear estudios jurídicos. Documentos: [especificación](../funcionalidades/021-organizaciones-de-aseguradoras/especificacion.md), [plan](../funcionalidades/021-organizaciones-de-aseguradoras/plan.md) y [tareas](../funcionalidades/021-organizaciones-de-aseguradoras/tareas.md).

- **Catálogo**: `backend/recursos/catalogos/aseguradoras_ssn.csv`, con las 192 aseguradoras del conjunto de datos de la SSN que aportó la autora, sin reaseguradoras.
- **Registro**: el paso 1 ofrece "Abogado o abogada" o "Registrar mi aseguradora"; el paso 3 tiene un buscador por nombre o CUIT. Los empleados se registran desde el enlace de la invitación en solo dos pasos (datos y cuenta) y, al verificar el correo, quedan dentro de la aseguradora.
- **Administración**: pantalla para aprobar o rechazar (con motivo) las aseguradoras pendientes. Los administradores se crean desde la terminal: `flask --app wsgi administracion promover <correo>`.
- **Cuentas desactivadas**: al abandonar, ser desvinculado o eliminarse la aseguradora; se cierran sus sesiones y no pueden ingresar, salvo para aceptar una invitación vigente, que las reactiva.
- **Reglas nuevas** RN36 a RN40 en la especificación general; RN35 suma la excepción de que el Administrador aprueba aseguradoras.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA5 Registro de la aseguradora | Pruebas de API (catálogo, alta, CUIT repetido, sin catálogo) y de pantalla (buscador por nombre y CUIT) | Cumplidos |
| CA6 – CA9 Aprobación | Pruebas de API y de pantalla, incluido quien no es Administrador | Cumplidos |
| CA10 – CA12 Empleados | Pruebas de registro con invitación, correo distinto e invitación cancelada | Cumplidos |
| CA13 – CA16 Cuentas desactivadas | Pruebas de desvinculación, abandono, eliminación, inicio de sesión, reactivación y de un abogado que no se desactiva | Cumplidos |
| CA17 – CA19 Organizaciones y auditoría | Pruebas de creación y edición restringidas y de las entradas de auditoría | Cumplidos |

Cifras: backend con 195 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y contratos de capas cumplidos; frontend con 129 pruebas, cobertura del 99 %, ESLint sin errores y compilación correcta. Migración probada en PostgreSQL. Recorrido en navegador con tres personas (Administrador, Referente de Seguros Galicia y una empleada en celular): registro, aprobación, invitación, registro de la empleada, abandono con cuenta desactivada e inicio de sesión rechazado, sin errores en la consola.

## Decisiones

- **De la autora**: aprobación manual del Administrador; desactivar la cuenta al quedarse sin aseguradora; hacer la 021 antes de la 005.
- **Del asistente**:
  - Una sola organización por CUIT; si la empresa ya está registrada, se indica pedir una invitación a su Referente.
  - El rechazo elimina la organización (así la empresa queda libre para quien corresponda) y desactiva a su Referente.
  - Un abogado invitado a una aseguradora puede sumarse y, al salir, conserva su cuenta y su espacio personal.
  - Se puede iniciar sesión con una cuenta desactivada solo si tiene invitaciones vigentes.
  - El nombre de una aseguradora es el del catálogo y no se edita; el tipo de ninguna organización se puede cambiar.
  - Los administradores solo se crean desde la terminal del servidor, nunca desde la interfaz.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| Las reglas nuevas se numeraron RN35 a RN39, pero RN35 ya existía (el Administrador solo consulta) | Se renumeraron a RN36 a RN40 en el código, las pruebas y los documentos, y se agregó a RN35 la excepción de aprobar aseguradoras |
| La migración autogenerada creaba la restricción única del CUIT sin nombre, y su `downgrade` fallaba | Se le puso nombre en el modelo y en la migración, que además agrega la restricción del estado |
| Un CUIT ya registrado se detectaba después de crear la cuenta en la transacción | Se valida antes de crear la cuenta |
| El servicio de organizaciones superó la cantidad de métodos públicos que admite pylint | Se dejó documentada la excepción: concentra las reglas de la organización en una sola transacción |
| El trabajo se interrumpió por un reinicio del entorno y por el límite de uso | Se retomó desde los archivos sin commit, que se conservaron |

## Pendientes

- **Autora**: revisar y abrir el Pull Request de `funcionalidad/021-organizaciones-de-aseguradoras` hacia `desarrollo`. Confirmar la licencia del conjunto de datos de la SSN (CP-18). Crear el primer Administrador en cada entorno con `flask --app wsgi administracion promover <correo>`.
- **014**: tablero completo de administración.
- Siguiente: **005, Casos y permisos**, que debe completar las reglas de casos pendientes de la 004.
