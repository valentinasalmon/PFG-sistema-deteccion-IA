# Tablero de Trello: convenciones y actualización automática

El [tablero de Trello](https://trello.com/b/FE1lU3cm) es la referencia de seguimiento del proyecto y figura como Anexo L del informe. Desde el 2026-10-29, por pedido de la autora, **el agente lo actualiza solo**, sin esperar a que se lo pidan: mueve las tarjetas cuando cambia el estado de una tarea y agrega las que falten.

## Cuándo se actualiza

1. **Al terminar cualquier trabajo**, la sesión del agente que lo hizo actualiza el tablero antes de despedirse: una funcionalidad, un Pull Request, un capítulo del informe, una investigación o una decisión nueva.
2. **Una vez por día**, una tarea programada revisa el repositorio, el documento del informe y el tablero, y corrige lo que haya quedado desfasado.

## Acceso

- La API de Trello se usa con las variables de entorno `TRELLO_KEY` y `TRELLO_TOKEN` del entorno de la nube. Nunca se escriben en el repositorio.
- Tablero: `6a5e9b7c997771574cc7ad51`.

## Listas

Coinciden con las columnas que declara el Capítulo V del informe.

| Lista | Id | Qué va |
|---|---|---|
| Backlog | `6a8643b36d5321de8ab5f1f0` | Lo pendiente, ordenado por prioridad y fecha |
| En análisis | `6adf8be68c0271d52216a9f8` | Lo que se está especificando o investigando |
| En desarrollo | `6a5e9b911773acbbbc3df085` | Lo que se está haciendo |
| En pruebas | `6a5e9b96a9f99082e0167323` | Lo hecho que espera la verificación o la revisión de la autora |
| Completado | `6a5e9bc102a99b823b81ea52` | Lo terminado, con la fecha real como vencimiento |

## Etiquetas

| Grupo | Etiquetas |
|---|---|
| Prioridad | P1 (imprescindible), P2 (suma mucho), P3 (opcional o trabajo futuro) |
| Quién | Autora, Agente IA, Tutores |
| Área | Desarrollo, Infraestructura, Documento, Relevamiento, Gestión |

Toda tarjeta nueva lleva una etiqueta de cada grupo; las de Completado no llevan prioridad.

## Reglas

- **Fuentes**: el estado se deduce de hechos comprobables. Valen los Pull Request integrados en `desarrollo` o `main`, los commits de las ramas, las casillas de `tareas.md`, la bitácora, `docs/guias/pendientes.md`, `docs/especificacion/06-cuestiones-abiertas.md` y el documento del informe en Google Drive.
- **Nada se da por hecho sin evidencia**: una tarea pasa a Completado solo si está integrada o si la autora la marcó. Lo que hizo el agente pero la autora no aceptó o no probó va a En pruebas.
- **Los movimientos de la autora mandan**: si la autora movió o editó una tarjeta a mano, no se la devuelve a otra lista. Ante una duda, se deja un comentario en la tarjeta en lugar de moverla.
- **No se borra nada**: lo que sobra se archiva con un comentario que explica por qué.
- **Cada cambio deja un comentario** en la tarjeta, que empieza con «Actualización automática (fecha):» y dice qué cambió y con qué evidencia.
- **Tarjetas completadas**: el vencimiento es la fecha real del hecho (integración del Pull Request, entrevista, entrega) y se marca como cumplido.
- **Descripciones**: enlace a la especificación y al Pull Request cuando existen; las listas de tareas reflejan las casillas de `tareas.md`.
- **Orden**: el Backlog se ordena por prioridad y luego por fecha; Completado, por fecha.
- **Decisiones de la autora**: no se toman. Si una tarea depende de una (alcance, privacidad, arquitectura grande o validación con los tutores), se crea o actualiza la tarjeta con la etiqueta Autora o Tutores y se sigue.
