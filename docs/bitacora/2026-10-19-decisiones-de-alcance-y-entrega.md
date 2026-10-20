# 2026-10-19 — Decisiones de alcance y entrega

Decisiones de la autora del 2026-10-19, registradas en la especificación general.

## Decisiones

| Tema | Decisión | Dónde quedó |
|---|---|---|
| Conservación de los casos | **5 años** desde que el caso se cierra o se archiva, el plazo de prescripción del Código Civil y Comercial (art. 2560). Es el mismo plazo de la auditoría. Antes eran 2 años. | RN30, CP-05, casos de uso; constante `ANIOS_DE_RETENCION` del backend; textos de la pantalla del caso y de la Política de Privacidad |
| Cobro de los planes | No hay cobro real: es un MVP y el cobro queda en el modelo de negocios. Se hace un **flujo de pago simulado** que **aplica el plan de verdad**. No pide datos de pago y queda en la auditoría. | CP-01, CP-02, RF20 CA2, visión y alcance; se implementa en la 014 |
| Despliegue | Infraestructura con **Terraform** en la cuenta de AWS de la autora, con los créditos gratuitos, y **despliegue automático** al integrar en `main`. | CP-06; funcionalidad 017 |
| Dominio | Se compra al final. Hasta entonces se usa la dirección de la EC2. | CP-16 |
| Correos | Amazon SES en modo de prueba (sandbox), con destinatarios verificados: la autora y los tutores. | CP-16 |
| Fecha de entrega | En menos de un mes, con la plataforma y el informe completos. | CP-16 |
| Red neuronal | La entrena la autora en Kaggle, en otra sesión de trabajo. Hasta que termine, se deja de lado todo lo que depende del modelo (012). | CP-21 |

## Otros cambios

- **Rama de la red neuronal** (`claude/intelligent-franklin-yl0b03`):
  - Sus ADR pasaron de 0012 y 0013 a **0014 y 0015**, porque `desarrollo` ya usa esos números para el almacenamiento y la cola de análisis.
  - Se integró `desarrollo` en esa rama, resolviendo los conflictos de los índices.
- Esta rama incluye los dos commits de la 009 que no habían entrado en su Pull Request: la leyenda del informe en todas las páginas y la cuestión CP-21.

## Orden de trabajo hasta la entrega

1. 017: Terraform, despliegue automático y guía de AWS. Va primero porque tiene pasos de la autora.
2. 011: ELA.
3. 013: panel y notificaciones.
4. 014: planes, administración y pago simulado.
5. 015: retención.
6. 016: sello en BFA.
7. 018: cierre.
