# 053 · Monitoreo y alertas con CloudWatch

**Estado**: implementada (2026-11-26); falta aplicarla en AWS. **Rama**: `infraestructura/monitoreo`. **Pedido**: la autora (2026-11-24): «agreguemos alguna herramienta de monitoreo, o no sé si AWS hace».

## Problema

Si la plataforma se caía, una tarea nocturna fallaba o el disco se llenaba, nadie se enteraba hasta que una persona lo veía. La única alerta automática era la del presupuesto.

## Alcance

- **Herramienta**: Amazon CloudWatch, de AWS. Ya se paga con la misma cuenta, no suma otro proveedor que vea datos de la plataforma y entra casi entero en la capa gratuita.
- **Métricas propias, sin instalar agentes**: cada 15 minutos el servidor ejecuta `scripts/medir_salud.sh` y publica en CloudWatch, en el espacio `evidentIA`:
  - si `https://evidentiaa.com.ar/api/salud` responde (pasa por Nginx, el certificado, la aplicación, la base y Redis);
  - cuántas tareas programadas fallaron (sellos en Hedera, retención, respaldo y catálogo de la SSN);
  - el porcentaje de disco usado;
  - la memoria disponible;
  - los días que le quedan al certificado HTTPS.

  La CPU la publica AWS sin costo.
- **Frecuencia de 15 minutos** (pedido de la autora, 2026-11-26: «es un MVP»). Una caída se avisa a los 30 minutos como mucho. En una operación comercial conviene bajarla a 5 minutos: se cambia en el temporizador y en `monitoreo.tf`.
- **Alarmas que avisan por correo** (SNS) cuando algo falla y cuando se recupera:

  | Alarma | Cuándo avisa |
  |---|---|
  | Plataforma caída | `/api/salud` no responde durante 30 minutos, o el servidor dejó de publicar |
  | Servidor sin respuesta | la EC2 no pasa los controles de estado de AWS durante 5 minutos |
  | Tareas fallidas | una tarea programada terminó con error |
  | Disco lleno | disco por encima del 85 % |
  | Memoria baja | menos de 150 MB disponibles durante 30 minutos |
  | CPU alta | más del 85 % durante 15 minutos (puede agotar los créditos de la t3) |
  | Certificado por vencer | menos de 14 días (falló la renovación de Let's Encrypt) |

- **Tablero** en CloudWatch con las cinco métricas.
- Realiza RNF15 (disponibilidad y respaldo) y RNF16 (tolerancia a fallos): las caídas y las tareas fallidas dejan de pasar inadvertidas.
- **Si falla el hardware de AWS**, la EC2 se recupera sola: la recuperación automática simplificada viene activa en las t3. La alarma avisa igual.
- **Costo estimado**: 5 métricas propias × USD 0,30 = USD 1,50 por mes. AWS cobra por métrica, no por medición, así que medir más seguido no cambia el costo. Las 7 alarmas entran en las 10 gratuitas.
- **Guía de qué hacer con cada alerta**: [monitoreo-y-alertas.md](../../guias/monitoreo-y-alertas.md).

## Criterios de aceptación

- [x] **CA1**: El script mide y publica las métricas. Probado en local con un `aws` falso: con el sitio de producción respondió 1 y con un dominio inexistente, 0. Si no puede leer el certificado, no publica ese dato, para no dar una alarma falsa.
- [x] **CA2**: Terraform válido (`terraform validate` y `fmt`), con permiso de mínimo privilegio: solo `PutMetricData` en el espacio `evidentIA`. `shellcheck` sin observaciones.
- [ ] **CA3**: Aplicado en AWS por la autora (`terraform apply`), suscripción de correo confirmada y temporizador activo. **No verificado todavía.**
- [ ] **CA4**: Prueba de una alarma real: con `plataforma-web` detenido 30 minutos llega un correo «ALARM» y, al volver a levantarlo, uno «OK». **No verificado todavía.**
