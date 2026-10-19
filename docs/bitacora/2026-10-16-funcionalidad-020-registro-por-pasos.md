# 2026-10-16 — Funcionalidad 020: registro guiado por pasos

## Qué se hizo

A pedido de la autora, el registro de la funcionalidad 002 pasó de un formulario largo en una sola pantalla a cuatro pasos cortos, con una pregunta principal por pantalla. Se hizo antes de continuar con la 003. Documentos: [especificación](../funcionalidades/020-registro-por-pasos/especificacion.md), [plan](../funcionalidades/020-registro-por-pasos/plan.md) y [tareas](../funcionalidades/020-registro-por-pasos/tareas.md).

- **Pasos**: 1) "¿Cómo vas a usar la plataforma?", con dos tarjetas grandes (Abogado o abogada, Aseguradora) y el aviso de que el perfil no se puede cambiar; 2) nombre y apellido; 3) colegio de abogados o empresa, opcional; 4) correo, contraseña y aceptación de los términos.
- **Componentes nuevos** (asistente): `IndicadorPasos` ("Paso N de 4" con barra decorativa) y `OpcionTarjeta` (botón de opción nativo con forma de tarjeta), con sus estilos.
- **Pantalla y hook** (autora): `PaginaRegistro` por pasos y `marcarErrores` en `useFormulario` para marcar varios campos a la vez.
- Solo cambió el frontend: la API y los criterios de RF01 siguen iguales.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 – CA4 Pasos y validación | Pruebas de la pantalla y recorrido en navegador | Cumplidos |
| CA5 Volver atrás conserva los datos | Prueba que recorre los cuatro pasos hacia atrás y hacia adelante | Cumplido |
| CA6 Crear la cuenta | Prueba de la solicitud enviada y correo recibido en el recorrido | Cumplido |
| CA7 Error de un paso anterior | Prueba y recorrido con un nombre demasiado largo, que vuelve al paso 2 | Cumplido |
| CA8 Avance y foco | Prueba del foco en el título y recorrido con teclado (Tab, flechas y Enter) | Cumplido |

Cifras finales: frontend con 74 pruebas, cobertura del 99 %, ESLint sin errores y compilación correcta. Recorrido en navegador real en escritorio y a 375 px sin desbordes, y recorrido manual de la autora (T05) con Docker y Mailpit. Integración continua del [Pull Request #4](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/4) en verde en sus tres trabajos.

## Decisiones tomadas

- **Cuatro pasos** y la 020 antes de la 003 (decisión de la autora).
- **El foco pasa al título de cada paso** al cambiar de paso, pero no al abrir la pantalla, para no interrumpir la lectura inicial.
- **Si cambia el perfil**, solo se envía el colegio o la empresa del perfil final.
- **CP-17**: los abogados podrán trabajar como usuarios individuales y las aseguradoras dentro de una organización; se especifica en la 004.
- **CP-18 resuelta**: la empresa aseguradora se valida contra el catálogo "Entidades activas" de la Superintendencia de Seguros de la Nación, sin las 140 reaseguradoras, porque no gestionan siniestros de asegurados y las 125 admitidas son extranjeras sin CUIT argentino. Quedan 192 aseguradoras.
- **CP-19 resuelta**: los abogados no se verifican. El Registro Público de Graduados Universitarios acredita el título, no la habilitación para ejercer.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| Los dos commits de la autora se hicieron y se subieron en la rama `funcionalidad/003-auditoria` | Se copiaron a la 020 con `git cherry-pick` y la 003 volvió a su último commit con `git reset --hard` y `git push --force-with-lease`. Desde ahora, antes de cada commit se revisa la rama con `git branch --show-current` |
| La primera cuenta de reaseguradoras (132) era incorrecta: se habían separado las columnas por comas y algunos nombres tienen comas | Se recontó leyendo el archivo como CSV: son 140 |

## Pendientes

- Especificar la validación de aseguradoras (CP-18): licencia del catálogo, funcionalidad en la que entra y cómo se actualiza.
- Seguir con la **003, Auditoría**: la especificación espera la aprobación de la autora. Antes de planificar, la rama `funcionalidad/003-auditoria` debe incorporar `desarrollo` con la 020 integrada.
