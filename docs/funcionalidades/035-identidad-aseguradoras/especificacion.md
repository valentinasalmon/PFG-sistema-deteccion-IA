# Especificación: 035 — Verificación de identidad del Referente de una aseguradora

- **Rama**: `funcionalidad/035-identidad-aseguradoras`
- **Estado**: Implementada con proveedor simulado (falta conectar Identik: CP-35, CP-39)
- **Requisitos que realiza**: RF01, RF12 (aprobación de aseguradoras), RNF08 (datos personales)
- **Reglas de negocio aplicadas**: RN36 a RN40 (aprobación de aseguradoras); RN41 (nueva)
- **Casos de uso**: registro y aprobación de una aseguradora (021)

## Problema

Hoy una aseguradora se registra, paga el plan y queda pendiente hasta que el Administrador la aprueba a mano, comprobando que la persona trabaje ahí (021, 032). La autora decidió sumar una verificación de identidad con un servicio externo (Identik, CP-35), para confirmar que quien registra la aseguradora es quien dice ser antes de aprobarla.

## Alcance

### Incluido
- El Referente de una aseguradora pendiente inicia la verificación de su identidad desde la pantalla de la organización y la completa en la página del proveedor.
- El sistema guarda **solo el resultado** (pendiente, aprobada o rechazada, con fecha y referencia del proveedor), nunca imágenes del documento ni datos biométricos.
- El Administrador ve el estado de la verificación junto a cada aseguradora pendiente y no puede aprobarla sin la identidad aprobada mientras la verificación esté activa.
- Proveedor intercambiable: hoy **simulado** (para desarrollar y mostrar el flujo), después Identik, sin cambiar pantallas ni reglas.
- Auditoría de cada inicio y cada resultado.

### Excluido
- La conexión real con Identik (su API, los avisos firmados y el entorno de pruebas): se suma cuando Identik envíe la documentación de verificación de identidad y el sandbox.
- La firma digital del informe PDF con Identik (CP-27, opcional).
- La verificación de estudios jurídicos y abogados independientes.

## Reglas nuevas

- **RN41**: Si la verificación de identidad está activa, una aseguradora pendiente solo se aprueba con la identidad de su Referente aprobada. La plataforma guarda el resultado de la verificación, no los datos biométricos.

## Criterios de aceptación

- [x] **CA1**: Dado el Referente de una aseguradora pendiente, cuando elige «Verificar mi identidad», entonces recibe un enlace a la página del proveedor y la verificación queda pendiente.
- [x] **CA2**: Solo el Referente de una aseguradora pendiente puede iniciarla; un miembro, otra persona o una organización activa reciben un rechazo.
- [x] **CA3**: Cuando el proveedor informa el resultado, la verificación queda aprobada o rechazada con su fecha, y se registra en la auditoría sin datos biométricos.
- [x] **CA4**: El Administrador ve, en cada aseguradora pendiente, si la identidad está sin verificar, pendiente, aprobada o rechazada.
- [x] **CA5**: Con la verificación activa, aprobar una aseguradora sin la identidad aprobada se rechaza con un mensaje claro; con la verificación desactivada, la aprobación sigue como antes.
- [x] **CA6**: Con el proveedor simulado, la página de verificación permite simular el resultado y aclara que es una simulación; con un proveedor real, no.
- [x] **CA7**: Si la verificación fue rechazada, el Referente puede iniciar una nueva.

## Preguntas abiertas

- CP-35: flujo exacto de Identik (redirección o dentro de la web), validación contra RENAPER, prueba de vida, retención de los datos biométricos del lado de Identik y costo. Consultado a Identik el 2026-11-03.
