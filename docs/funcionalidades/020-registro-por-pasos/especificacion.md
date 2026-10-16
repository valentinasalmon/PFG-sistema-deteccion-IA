# Especificación: 020 — Registro guiado por pasos

- **Rama**: `funcionalidad/020-registro-por-pasos`
- **Estado**: En implementación
- **Requisitos que realiza**: RF01 (interfaz de registro, sin cambios en sus criterios); RNF10 (facilidad de uso para usuarios no técnicos)
- **Reglas de negocio aplicadas**: RN01, RN02
- **Casos de uso**: CU01

## Problema

El formulario de registro de la funcionalidad 002 muestra todos los datos en una sola pantalla: nombre, apellido, correo, contraseña, perfil, colegio o empresa y términos. Para personas no técnicas, como abogados y personal de aseguradoras, un formulario largo resulta pesado y facilita que se pase por alto algo importante, como que el perfil no puede cambiarse después.

Dividir el registro en pasos cortos, con una pregunta principal por pantalla, hace la tarea más clara, destaca la elección del perfil y permite corregir cada dato en su contexto.

## Alcance

### Incluido

- Registro en **4 pasos**, con barra de progreso y botones para volver y avanzar:
  1. **¿Cómo vas a usar la plataforma?** Elección del perfil (Abogado o Aseguradora) con opciones grandes, aclarando que no podrá cambiarse.
  2. **Tus datos**: nombre y apellido.
  3. **Tu colegio de abogados o tu empresa**, según el perfil elegido, opcional.
  4. **Tu cuenta**: correo, contraseña con sus reglas y aceptación de los Términos de Uso y la Política de Privacidad.
- Validación de cada paso antes de avanzar, con el error junto al campo.
- Al volver a un paso anterior se conservan los datos cargados.
- Si al crear la cuenta el sistema rechaza un dato de un paso anterior, se vuelve a ese paso y se muestra el error junto al campo.
- La pantalla de confirmación ("Revisá tu correo") y el resto del comportamiento del registro de la funcionalidad 002 no cambian.
- Accesible con teclado y lector de pantalla: el paso actual se anuncia y el foco pasa al título de cada paso.

### Excluido

- Cambios en la API o en las reglas del registro: los criterios de RF01 no cambian.
- Elegir entre usuario individual u organización, e invitar a otras personas: funcionalidad 004 (ver CP-17).
- Validación del nombre de la aseguradora contra un catálogo: pendiente (ver CP-18).
- Verificación de la habilitación de los abogados: pendiente de decisión (ver CP-19).
- Pasos en el inicio de sesión: sigue siendo una sola pantalla, porque solo pide correo y contraseña.

## Criterios de aceptación

- [ ] **CA1**: Dado un visitante en el registro, entonces ve el paso 1 de 4 con la pregunta "¿Cómo vas a usar la plataforma?" y las opciones Abogado y Aseguradora, junto con la aclaración de que el perfil no podrá cambiarse.
- [ ] **CA2**: Dado el paso 1, cuando el visitante intenta avanzar sin elegir un perfil, entonces no avanza y se indica que debe elegir uno.
- [ ] **CA3**: Dado el paso 2, cuando el visitante intenta avanzar sin nombre o sin apellido, entonces no avanza y se marca cada campo vacío.
- [ ] **CA4**: Dado el paso 3, entonces se pide el colegio de abogados si eligió Abogado o la empresa si eligió Aseguradora, como dato opcional que permite avanzar vacío.
- [ ] **CA5**: Dado cualquier paso posterior al primero, cuando el visitante vuelve atrás, entonces encuentra los datos que había cargado.
- [ ] **CA6**: Dado el paso 4 completo, cuando el visitante crea la cuenta, entonces se cumplen los criterios de RF01 (CA1 a CA5) y se muestra la confirmación "Revisá tu correo".
- [ ] **CA7**: Dado un rechazo del sistema por un dato de un paso anterior, entonces se vuelve a ese paso con el error junto al campo.
- [ ] **CA8**: En todos los pasos se muestra el avance ("Paso N de 4"), y al cambiar de paso el foco pasa al título del paso nuevo.

## Preguntas abiertas

- Ninguna para esta funcionalidad. Las ideas relacionadas que quedan para después están registradas como CP-17, CP-18 y CP-19.
