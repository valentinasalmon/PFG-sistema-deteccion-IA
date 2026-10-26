# Especificación: 013 — Panel principal y notificaciones

- **Rama**: `funcionalidad/013-panel-y-notificaciones`
- **Estado**: Completada (pendiente de revisión de la autora en el Pull Request)
- **Requisitos que realiza**: RF47 (CA1 a CA3), RF48 (CA1 a CA3)
- **Reglas de negocio aplicadas**: RN31 (aviso de destrucción próxima en el panel), RNF06 (la actividad sale de la auditoría)
- **Casos de uso**: CU30

## Problema

Al iniciar sesión, la persona solo ve cuántos casos tiene en cada estado. Para saber qué pasó desde la última vez tiene que entrar a cada caso. Por ejemplo, que alguien de su estudio cargó imágenes, que terminó un análisis o que le compartieron un caso.

Además, los correos se envían en el momento, dentro de la operación que los origina. Si el servidor de correo tarda o falla:
- la persona espera;
- el correo se pierde sin reintentarse.

## Alcance

### Incluido

**Panel principal (RF48)**
- **Casos por estado**, con acceso al listado filtrado, como hasta ahora.
- **Últimos casos actualizados**: los cinco más recientes a los que la persona tiene acceso.
- **Análisis en curso** en esos casos, con el caso y la cantidad de imágenes.
- **Casos compartidos recientemente** con la persona: en los últimos 30 días, con quién es el Responsable y el permiso.
- **Invitaciones pendientes** a organizaciones, con acceso a la pantalla para aceptarlas.
- **Transferencias de casos pendientes** dirigidas a la persona.
- **Casos próximos a su destrucción por retención**: los casos de los que es Responsable y vencen dentro de 30 días (RN31).
- **Actividad reciente**: los últimos 10 eventos de los casos a los que tiene acceso.
  - Se redactan en lenguaje común; por ejemplo, "Ana López cargó la imagen frente.jpg en CASO-2026-000123".
  - Salen de la auditoría y solo incluyen acciones exitosas.
  - No muestran direcciones IP ni otros datos de la auditoría.
- Cada elemento lleva al caso correspondiente (RF48 CA3).

**Notificaciones por correo (RF47)**
- **Envío en segundo plano**: los correos se encolan y los envía el proceso trabajador. Una falla de envío no revierte ni demora la operación que lo originó (CA1).
- **Reintentos**: si el envío falla, se reintenta dos veces más, a los 30 segundos y a los 2 minutos, y cada falla queda en el log (CA3).
- Los correos se procesan en una cola propia, así no esperan detrás de un análisis largo.
- **Análisis finalizado o fallido**: el aviso llega a quien lo pidió y también al Responsable del caso, si es otra persona (tabla de RF47).
- Se verifica que ningún correo incluya imágenes, informes ni datos sensibles del caso: solo el número de caso y un enlace a la plataforma (CA2).

### Excluido

- **Aviso de destrucción por retención por correo**: funcionalidad 015. El panel ya muestra los casos próximos a vencer.
- **Notificaciones dentro de la plataforma** (campana o bandeja de avisos): el panel cumple ese papel en esta versión.
- **Preferencias de notificación** (elegir qué correos recibir): trabajo futuro.

## Criterios de aceptación

- [x] **CA1**: Dado un usuario con casos, cuando entra al inicio, entonces ve los casos por estado, los últimos actualizados, los análisis en curso, los casos compartidos recientemente, las invitaciones y transferencias pendientes, y los casos próximos a destruirse (RF48 CA1).
- [x] **CA2**: La actividad reciente muestra los últimos eventos de los casos a los que el usuario tiene acceso, redactados en lenguaje común, y no muestra eventos de casos ajenos (RF48 CA2).
- [x] **CA3**: Cada elemento del panel lleva al caso, a la invitación o a la transferencia correspondiente (RF48 CA3).
- [x] **CA4**: Los correos se envían en segundo plano, en una cola propia; una falla no revierte la operación y se reintenta hasta tres veces en total, registrando cada falla (RF47 CA1, CA3).
- [x] **CA5**: El aviso de análisis finalizado o fallido llega a quien lo pidió y al Responsable, sin duplicarse si es la misma persona (RF47).
- [x] **CA6**: Los correos contienen solo el número de caso y enlaces a la plataforma, sin imágenes, informes ni datos sensibles (RF47 CA2).

## Preguntas abiertas

- Ninguna que bloquee.
