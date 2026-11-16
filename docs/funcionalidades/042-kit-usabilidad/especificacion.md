# 042 · Kit imprimible de la prueba de usabilidad

**Estado**: implementada (2026-11-16). **Rama**: `funcionalidad/042-kit-usabilidad`. **Pedido**: preparar lo que la autora necesita para conducir la prueba de usabilidad (018).

## Problema

El protocolo (`docs/guias/prueba-de-usabilidad.md`) tenía el consentimiento, la planilla y el cuestionario SUS en Markdown: para usarlos en una sesión había que pasarlos a mano a un documento imprimible.

## Alcance

- PDF A4 de cuatro hojas, con la identidad visual del proyecto: consentimiento, guion con las consignas (solo para la autora), planilla de registro y cuestionario SUS con las preguntas finales.
- Fuente HTML junto al PDF, con el comando para regenerarlo.

## Criterios de aceptación

- [x] **CA1**: Cada hoja entra en una sola página A4 (comprobado renderizando el PDF).
- [x] **CA2**: El contenido coincide con el protocolo actualizado en la 041 (tareas T1 a T9, SUS, preguntas finales).
