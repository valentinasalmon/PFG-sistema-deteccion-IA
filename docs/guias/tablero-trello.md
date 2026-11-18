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

- **Fuentes**: el estado se deduce de hechos comprobables. Valen los Pull Request integrados en `main` (antes del 2026-11-16, también en `desarrollo`), los commits de las ramas, las casillas de `tareas.md`, la bitácora, `docs/guias/pendientes.md`, `docs/especificacion/06-cuestiones-abiertas.md` y el documento del informe en Google Drive.
- **Nada se da por hecho sin evidencia**: una tarea pasa a Completado solo si está integrada o si la autora la marcó. Lo que hizo el agente pero la autora no aceptó o no probó va a En pruebas.
- **Conciliación completa en cada corrida** (pedido de la autora, 2026-11-16): no alcanza con mirar lo nuevo desde la última actualización. Cada corrida revisa todas las tarjetas abiertas que no están en Completado contra la evidencia actual, incluida la columna de estado de `docs/funcionalidades/README.md`, y las mueve si corresponde. El tablero tiene que reflejar siempre el estado real.
- **Siempre hacia adelante**: Backlog → En análisis (hay especificación o investigación en curso) → En desarrollo (hay commits o trabajo empezado) → En pruebas (terminado, falta verificar o integrar) → Completado (integrado o verificado). Una tarjeta que la autora movió a mano se puede llevar hacia adelante si la evidencia lo justifica; lo que nunca se hace es devolverla hacia atrás. Se comenta sin mover solo cuando de verdad no hay evidencia suficiente.
- **Verificar en vez de esperar**: si algo espera una verificación que el agente puede hacer (por ejemplo, las cabeceras o la versión en producción), la hace y mueve la tarjeta.
- **Ramas sin integrar**: el trabajo que queda en una rama no llega a Completado. Si hay ramas con commits fuera de `desarrollo`, se mantienen en la tarjeta «Revisar e integrar las ramas con trabajo sin integrar».
- **Fechas vencidas**: si una tarjeta abierta tiene la fecha vencida, se corre (P1 a la próxima fecha de entrega, el resto una semana más) y se deja el motivo en un comentario.
- **No se borra nada**: lo que sobra se archiva con un comentario que explica por qué.
- **Cada cambio deja un comentario** en la tarjeta, que empieza con «Actualización automática (fecha):» y dice qué cambió y con qué evidencia.
- **Tarjetas completadas**: el vencimiento es la fecha real del hecho (integración del Pull Request, entrevista, entrega) y se marca como cumplido.
- **Descripciones**: enlace a la especificación y al Pull Request cuando existen; las listas de tareas reflejan las casillas de `tareas.md`.
- **Orden**: el Backlog se ordena por prioridad y luego por fecha; Completado, por fecha.
- **Decisiones de la autora**: no se toman. Si una tarea depende de una (alcance, privacidad, arquitectura grande o validación con los tutores), se crea o actualiza la tarjeta con la etiqueta Autora o Tutores y se sigue.
