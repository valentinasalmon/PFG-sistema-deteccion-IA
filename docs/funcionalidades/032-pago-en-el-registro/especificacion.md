# Especificación: 032 — Pago del plan en el registro (simulado con Cresium)

- **Rama**: `funcionalidad/032-pago-en-el-registro`
- **Estado**: Implementada (frames 10a a 10g validados por la autora el 2026-10-29, con la tarjeta del registro más ancha)
- **Requisitos que realiza**: RF01, RF10, RF19, RF20; RNF10
- **Reglas de negocio aplicadas**: RN15, RN36 a RN40; CP-01 y CP-34 (pago simulado)
- **Casos de uso**: CU01 (registrarse), CU08 (crear organización), CU16 (plan y consumo)

## Problema

Hasta ahora el plan de una organización se elegía y se «pagaba» en una sección aparte, después de crearla. La autora decidió (2026-10-29) que el plan se elija y se pague **al registrarse**, para los estudios jurídicos y las aseguradoras. El cobro real será con Cresium, una *fintech* argentina que cobra por transferencia a un CVU. Como todavía no hay acceso a su API ni a un entorno de pruebas, el pago se **simula** con la misma forma que tendrá el real.

## Alcance

### Incluido
- **Registro con tres caminos**: abogado independiente (plan personal, sin pago), abogado con estudio jurídico (con el nombre del estudio) y aseguradora (del catálogo de la SSN).
- **Plan Básico o Profesional** para el estudio y la aseguradora, con sus límites y el precio «A confirmar».
- **Pago por transferencia** al final del registro: CVU, alias, titular y una referencia; el pago se acredita solo. Mientras no esté la API de Cresium, un botón «Simular la transferencia» hace de aviso de acreditación.
- **Estados de la organización**: queda «pago pendiente» hasta que se acredita. El estudio pasa a activo. La aseguradora pasa a «pendiente de aprobación» y después la aprueba o la rechaza el Administrador; si la rechaza, el pago se devuelve (simulado).
- **El independiente crea su estudio después**, desde Mi perfil, con el plan y el pago.
- **El cambio de plan** también pasa por el pago, y el plan nuevo rige al acreditarse.
- **El plan impacta en el sistema**: miembros, análisis por mes e imágenes por caso. Con el cupo de miembros lleno, «Invitar» queda deshabilitado y se ofrece pasar a Profesional.
- **Retomar un pago pendiente** desde la organización.
- La tarjeta del registro es más ancha y los pasos se ven con nombre en el panel de la izquierda.

### Excluido
- El cobro real con la API de Cresium y el aviso por *webhook*: cuando Cresium dé acceso, reemplaza al proveedor simulado sin cambiar las pantallas.
- Los precios: quedan «A confirmar» hasta que los defina la autora.
- La facturación y la renovación mensual automática.

## Criterios de aceptación

- [x] **CA1**: Dado un abogado que elige «independiente», cuando completa el registro, entonces no ve pasos de plan ni de pago.
- [x] **CA2**: Dado un abogado que elige «con estudio jurídico», cuando no escribe el nombre del estudio, entonces no puede avanzar.
- [x] **CA3**: Dado un estudio o una aseguradora, cuando crea la cuenta, entonces la organización queda con «pago pendiente», con el plan elegido, y se muestran el CVU, el alias y la referencia del cobro.
- [x] **CA4**: Dado un cobro pendiente, cuando se acredita (simulado), entonces el estudio queda activo y la aseguradora queda pendiente de aprobación; queda en la auditoría.
- [x] **CA5**: Dado un correo ya registrado, cuando alguien intenta registrarse con él, entonces la respuesta y la pantalla de pago son iguales a las de un correo nuevo (no se revela que existe, RF01 CA3).
- [x] **CA6**: Dada una aseguradora pagada y rechazada por el Administrador, entonces su cobro queda devuelto (simulado).
- [x] **CA7**: Dada una organización con «pago pendiente», entonces no se puede invitar ni crear casos en ella, y su Referente puede retomar el pago.
- [x] **CA8**: Dado un Referente que pide pasar a otro plan, entonces el plan cambia recién cuando se acredita el pago.
- [x] **CA9**: Dado un independiente, cuando crea su estudio desde Mi perfil, entonces elige el plan y paga antes de que el estudio quede activo.
- [x] **CA10**: Dada una organización con el cupo de miembros lleno, entonces «Invitar» se deshabilita y se ofrece pasar a Profesional.

## Preguntas abiertas

- Precios de los planes (a confirmar por la autora).
- API, entorno de pruebas y costos de Cresium (CP-34): pedirlos a su equipo comercial.
