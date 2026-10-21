# 2026-10-21 — Funcionalidad 013: panel principal y notificaciones

## Qué se hizo

- **Panel principal (RF48)**: la pantalla de inicio reúne:
  - los casos por estado;
  - lo pendiente: invitaciones, transferencias y casos que se destruyen dentro de 30 días;
  - los análisis en curso;
  - los casos compartidos con la persona en los últimos 30 días;
  - los últimos casos actualizados;
  - la **actividad reciente**.

  La actividad se arma con la auditoría y se redacta en lenguaje común, por ejemplo "Rita Prueba cargó la imagen «frente.jpg» en CASO-2026-000021". Cada elemento lleva a su caso.
- **Correos en segundo plano (RF47)**: los correos se encolan en una cola propia (`correos`) que el trabajador atiende antes que la de análisis.
  - Si el envío falla, se reintenta a los 30 segundos y a los 2 minutos, y cada falla queda en el log.
  - La operación que originó el correo no espera ni se revierte.
- **Aviso de análisis**: llega a quien lo pidió y también al Responsable del caso, como pide la tabla de RF47.

Documentos: [especificación](../funcionalidades/013-panel-y-notificaciones/especificacion.md), [plan](../funcionalidades/013-panel-y-notificaciones/plan.md) y [tareas](../funcionalidades/013-panel-y-notificaciones/tareas.md). La rama `funcionalidad/013-panel-y-notificaciones` parte de `desarrollo` con la 011 integrada.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 Secciones | Pruebas de integración de cada sección (vacío, recientes, en curso, compartidos, invitaciones, transferencias, próximos a destruirse) | Cumplido |
| CA2 Actividad | Textos esperados y sin eventos de casos ajenos; variantes de estado y de transferencia | Cumplido |
| CA3 Enlaces | Pruebas del frontend: cada caso a su detalle, invitaciones a Organizaciones, transferencias a Casos | Cumplido |
| CA4 Segundo plano | Reintentos en las tres colas, falla final sin propagarse, enviador según el entorno, RQ con `Retry` | Cumplido |
| CA5 Aviso al Responsable | Colaborador pide el análisis: avisos a los dos; Responsable que lo pide: un solo aviso | Cumplido |
| CA6 Sin datos sensibles | El aviso solo tiene el número de caso y el enlace, sin nombres de imágenes | Cumplido |

**Cifras:**
- Backend: 432 pruebas, más 2 que solo corren con las imágenes del TIF; cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 191 pruebas, ESLint sin errores y compilación correcta.

**Recorrido en navegador real**:
- El registro funcionó con el correo de verificación enviado en segundo plano.
- Se creó un caso, se cargó una imagen y se analizó.
- El panel mostró el caso analizado y cinco eventos de actividad redactados.
- En celular no hay desborde, y no hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Una sola consulta para el panel** (`GET /api/panel`): la pantalla de inicio carga de una vez y no con siete pedidos.
- **La actividad sale de la auditoría**: es el registro completo de lo que pasa en cada caso, y no hace falta otra tabla.
  - Solo se muestran acciones exitosas que cambian el caso; las descargas quedan afuera.
  - No se muestran direcciones IP.
- **Cola propia para los correos**, atendida primero: un correo de verificación no debe esperar detrás de un análisis.
- **Dos reintentos** (30 segundos y 2 minutos): cubren una caída breve del servidor de correo sin demorar mucho un aviso.
- **Correos sincrónicos en las pruebas**, para poder revisar su contenido.
- **Secciones vacías ocultas**: el panel muestra siempre el resumen de casos y, del resto, solo lo que tiene contenido.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| Las pruebas del log fallaban solo en la suite completa | Las pruebas de migraciones apagan los registradores existentes; las pruebas nuevas los vuelven a encender, como las anteriores |
| La prueba del repositorio de auditoría exigía solo tres métodos públicos | Se sumó la consulta nueva, que también es de solo lectura |

## Pendientes

- **Autora**: revisar e integrar el Pull Request de la 013. Al integrarlo en `main`, el trabajador del servidor empieza a atender también la cola de correos.
- **015**: el correo de aviso de destrucción por retención. El panel ya muestra esos casos.
- **Siguiente**: 014 (planes, administración y pago simulado).
